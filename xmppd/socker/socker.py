#!python
# -*- coding: utf-8 -*-
#
# Socker™ network load balancer & reverse proxy dæmon
#
# Copyright (C) 2005 BlueBridge Technologies Group, Inc.
# All rights reserved.
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# [*] Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
# [*] Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
# [*] Neither the name of BlueBridge Technologies nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"Socker™ network load balancer & reverse proxy dæmon"

__author__ = "Kristopher Tate <kris@bbridgetech.com>"
__version__ = "0.2"
__copyright__ = "Copyright (C) 2005 BlueBridge Technologies Group, Inc."
__license__ = "BSD"

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-t", "--test",
                  action="store_true", dest="enable_test",
                  help="Start-up test configuration")

parser.add_option("-d", "--debug",
                  action="store_true", dest="enable_debug",
                  help="Enables debug messaging to console")

(cmd_options, cmd_args) = parser.parse_args()

try:
    import event
except:
    print "Oops, you don't seem to have libevent and/or pyevent installed."
    print "Please review the README file accompanying this software. Thank-you."
    import sys
    sys.exit(1)


import socket
import time
import threading
import thread
import sys
import xmlrpclib
import traceback

# maximum allowed length of XML-RPC request (in bytes)
MAXREQUESTLENGTH = 10000
XMLRPC_PORT = 8000

XMLRPC_STAGE_ZERO = 0
XMLRPC_STAGE_ONE = 1
XMLRPC_STAGE_TWO = 2
XMLRPC_STAGE_THREE = 4
XMLRPC_STAGE_FOUR = 8


class Client:
    def __init__(self, socket, owner, type_guid, server_guid, fsock=False):
        self._sock = socket
        self._owner = owner
        self._tguid = type_guid
        self._sguid = server_guid
        self.linked = False

        if fsock is False:
            try:
                self.connect(type_guid, server_guid)
            except:  # GO SECOND CHANCE!
                new_server = self._owner.get_good_server(self._tguid)
                if new_server is not None:
                    if globals()['cmd_options'].enable_debug is True:
                        print "Connection to %(old_server)s failed; Using new server %(new_server)s" % {'old_server': server_guid, 'new_server': new_server}
                    self._sguid = new_server
                    self.connect(type_guid, new_server)

    def connect(self, type_guid, server_guid):
        #create an INET, STREAMing socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Now connect
        destination = (self._owner.routes[type_guid][server_guid]['info']['host'], self._owner.routes[type_guid][server_guid]['info']['port'])
        if globals()['cmd_options'].enable_debug is True:
            print "Connecting to ", destination
        sock.connect(destination)

        s = Client(sock, self._owner, type_guid, server_guid, True)

        self._owner.registersession(s, 2, type_guid, server_guid)
        self._owner.link_manager('a', self, s)

        s.linked = True
        self.linked = True

        return s

    def route(self, data, fileno):
        s = self._owner.sockets[self._owner.links[fileno]['fn']]['sock']
        s.send(data)

    def receive(self):
        """Reads all pending incoming data. Raises IOError on disconnect."""
        try:
            received = self._sock.recv(40960)
        except:
            received = ''

        if len(received) == 0:  # length of 0 means disconnect
            raise IOError("Peer disconnected")
        return received

    def send(self, msg):
        try:
            totalsent = 0
            while totalsent < len(msg):
                sent = self._sock.send(msg[totalsent:])
                if sent == 0:
                    self.terminate()
                totalsent = totalsent + sent
        except:
            pass

    def fileno(self):
        return self._sock.fileno()

    def getsockname(self):
        return self._sock.getsockname()

    def terminate(self):
        if self.linked is True:
            linkup = self._owner.sockets[self._owner.links[self.fileno()]['fn']]['sock']

            if globals()['cmd_options'].enable_debug is True:
                print "Terminating %s::%s" % (self.fileno(), linkup.fileno())
            self._owner.link_manager('r', self)
            self._owner.unregistersession(linkup)
            # Handle forward socket
            linkup._sock.close()

        # Handle our socket
        self._owner.unregistersession(self)
        self._sock.close()

        self.linked = False


class RPC_Client:
    def __init__(self, owner, socket, addr, host, port):
        self._sock = socket
        self._owner = owner

        self.addr = addr
        self.host = host
        self.port = port

        self.stage = XMLRPC_STAGE_ZERO
        self.RPC_handler(None)

    def RPC_handler(self, data):
        "Handler for incoming remote procedure calls"
        try:
            if self.stage == XMLRPC_STAGE_ZERO:
                self.stage = XMLRPC_STAGE_ONE  # Get client's headers out of the buffer
            elif self.stage == XMLRPC_STAGE_ONE:
                self.stage = XMLRPC_STAGE_TWO

                params, method = xmlrpclib.loads(data)
                if isinstance(params[0], type({})):
                    aside = params[0]
                    aside['_socket'] = self._sock
                    aside['_socket_info'] = (self.host, self.port)
                    params = (aside,)
                result = self.rpc_dispatch(method, params)
                if getattr(result, 'faultCode', None) is not None:
                    response = xmlrpclib.dumps(result)
                else:
                    response = xmlrpclib.dumps(result, methodresponse=1)

        except:
            response = xmlrpclib.dumps(xmlrpclib.Fault(1, "Socker(tm): %s" % traceback.format_exc()))

        if self.stage == XMLRPC_STAGE_TWO:
            final_output = ["HTTP/1.1 200 OK", "Server: BlueBridge Socker(tm)", "Content-Length: %i" % len(response), "Connection: close", "Content-Type: text/xml", "", response]
            self.send('\n'.join(final_output))
            self.terminate()

    def receive(self):
        """Reads all pending incoming data. Raises IOError on disconnect."""
        try:
            received = self._sock.recv(globals()['MAXREQUESTLENGTH'])
        except:
            received = ''

        if len(received) == 0:  # length of 0 means disconnect
            raise IOError("Peer disconnected")
        return received

    def send(self, msg):
        try:
            totalsent = 0
            while totalsent < len(msg):
                sent = self._sock.send(msg[totalsent:])
#                print "sent",msg,sent
                if sent == 0:
                    self.terminate()
                totalsent = totalsent + sent
        except:
            pass

    def fileno(self):
        return self._sock.fileno()

    def getsockname(self):
        return self._sock.getsockname()

    def terminate(self):
        # Handle our socket
        self._owner.unregistersession(self)
        self._sock.close()

    def rpc_dispatch(self, method, params):
        try:
            # We are forcing the 'export_' prefix on methods that are
            # callable through XML-RPC to prevent potential security
            # problems
            func = getattr(self, 'export_' + method)
        except AttributeError:
            raise Exception('method "%s" is not supported' % method)
        else:
            result = func(*params)
            if getattr(result, 'faultCode', None) is None:
                result = (result,)
            return result

    def execute_program(self, command):
        import os
        a = os.popen(command, 'r')
        out = str(a.read()).replace("\n", "")
        a.close()
        return out

    def rpc_security(self, inpt):
        if 'type_guid' in inpt and 'server_guid' in inpt and 'pass' in inpt:
            if 'pass' in self._owner.routes[inpt['type_guid']][inpt['server_guid']]['info'] and inpt['pass'] == self._owner.routes[inpt['type_guid']][inpt['server_guid']]['info']['pass']:
                return True
            elif 'pass' not in self._owner.routes[inpt['type_guid']][inpt['server_guid']]['info']:
                return True
        elif 'type_guid' in inpt and 'server_guid' in inpt and 'pass' not in self._owner.routes[inpt['type_guid']][inpt['server_guid']]['info']:
            return True
        return False

    def export_hello(self, inpt):
        return {'code': 1, 'msg': 'Hello!'}

    def export_broadcast(self, inpt):
#        print inpt
        if inpt['type_guid'] in self._owner.routes.keys():
            node_list = []
            message = {'act': 'bc', 'stanza': inpt['stanza']}
            for x in self._owner.routes[inpt['type_guid']].keys():
                if x not in ['bind', 'data'] and x != inpt['server_guid']:
                    node_list += [x]
                    if 'pass' in self._owner.routes[inpt['type_guid']][x]['info'].keys():
                        message['pass'] = self._owner.routes[inpt['type_guid']][x]['info']['pass']
                    xmlrpclib.ServerProxy(self._owner.routes[inpt['type_guid']][x]['info']['xmlrpc-callback']).socker(message)
                    if 'pass' in message.keys():
                        del message['pass']

            return {'code': 1, 'msg': 'BC-OK', 'nodes': node_list}
        else:
            return {'code': 0, 'msg': 'BAD-TGUID'}

    def export_hostname(self, inpt):
        if globals()['cmd_options'].enable_debug is True:
            print inpt
        if '_socket_info' in inpt.keys():
            return {'code': 1, 'hostname': inpt['_socket_info'][0]}
        else:
            return {'code': 0, 'msg': 'Cannot detect your hostname!'}

    def export_data(self, inpt):
        if 'type_guid' in inpt and 'server_guid' in inpt and 'act' in inpt:
            try:
                if inpt['act'] == 'add' and self.rpc_security(inpt) is True:
                    print "[RPC:DATA] Added!"
                    for x, y in inpt['add'].iteritems():
                        if x not in self._owner.routes[inpt['type_guid']][inpt['server_guid']]['data']:
                            self._owner.routes[inpt['type_guid']][inpt['server_guid']]['data'][x] = y
                        else:
                            self._owner.routes[inpt['type_guid']][inpt['server_guid']]['data'][x].update(y)

                elif inpt['act'] == 'get':
                    data = eval("self._owner.routes[inpt['type_guid']][inpt['server_guid']]['data']" + ''.join(map(lambda x: "['" + x + "']", inpt['get'])))
                    return {'code': 1, 'msg': 'RC-OK', 'rs': data}

                elif inpt['act'] == 'remove' and self.rpc_security(inpt) is True:
                    print "[RPC:DATA] Removed!"
                    eval("self._owner.routes[inpt['type_guid']][inpt['server_guid']]['data']" + ''.join(map(lambda x: "['" + x + "']", inpt['remove'][:-1])) + ".pop('%s')" % inpt['remove'][-1])
                return {'code': 1, 'msg': 'RC-OK'}
            except:
                return {'code': 0, 'msg': 'RC-BAD'}

        elif 'type_guid' in inpt and 'act' in inpt:
            try:
                if inpt['act'] == 'add':
                    print "[RPC:DATA] Added!"
                    for x, y in inpt['add'].iteritems():
                        if x not in self._owner.routes[inpt['type_guid']]['data']:
                            self._owner.routes[inpt['type_guid']]['data'][x] = y
                        else:
                            self._owner.routes[inpt['type_guid']]['data'][x].update(y)

                elif inpt['act'] == 'get':
                    data = eval("self._owner.routes[inpt['type_guid']]['data']" + ''.join(map(lambda x: "['" + x + "']", inpt['get'])))
                    return {'code': 1, 'msg': 'RC-OK', 'rs': data}

                elif inpt['act'] == 'remove':
                    print "[RPC:DATA] Removed!"
                    eval("self._owner.routes[inpt['type_guid']]['data']" + ''.join(map(lambda x: "['" + x + "']", inpt['remove'][:-1])) + ".pop('%s')" % inpt['remove'][-1])
            except:
                return {'code': 0, 'msg': 'RC-BAD'}
            return {'code': 1, 'msg': 'RC-OK'}
        else:
            return {'code': 0, 'msg': 'RC-BAD'}

    def export_getchain(self, inpt):
        if 'type_guid' in inpt.keys():
            chain_data = {}
            try:
                for x, y in self._owner.routes[inpt['type_guid']].iteritems():
                    if x not in ['bind', 'data']:
                        chain_data[x] = y['info']
                        chain_data[x]['active'] = len(self._owner.routes[inpt['type_guid']][x]['clients'])
                        if 'pass' in chain_data[x]:
                            del chain_data[x]['pass']
                return {'code': 1, 'chain': chain_data}
            except:
                return {'code': 2, 'msg': 'Incorrect TGUID or TGUID not created!'}
        else:
            return {'code': 0, 'msg': 'Not enough information'}

    def export_uuidgen(self, args):
        uuid = self.execute_program('uuidgen')  # Look for uuidgen for super-fast uuid generation.
        if len(uuid) > 0:
            import re
            import sha
            y = re.compile('^(.*)-(.*)-(.*)-(.*)-(.*)$')
            r = y.match('6aa6cd92-1b15-4ccd-98a0-7a77b473fe4b').group(0, 1, 2, 3, 4, 5)
            return '{%s%s-%s-%s-%s}' % (r[1], r[2], r[3], r[4], sha.new(str(time.time())).hexdigest()[20:])

        else:
            import random
            import md5
            t = long(time.time() * 1000)
            r = long(random.random() * 100000000000000000L)
            try:
                a = socket.gethostbyname(socket.gethostname())
            except:
                # if we can't get a network address, just imagine one
                a = random.random() * 100000000000000000L
            data = str(t) + ' ' + str(r) + ' ' + str(a) + ' ' + str(args)
            data = md5.md5(data).hexdigest()
            return '{%s}' % data

    def export_add(self, inpt):
        try:
            options = {}

            for field in ['conn_max', 'xmlrpc-callback', 'pass']:
                if field in inpt.keys():
                    options.update({field: inpt[field]})

            if inpt['outside_port'] == globals()['XMLRPC_PORT']:
                s = None
            else:
                s = self._owner.register_port(inpt['outside_port'], inpt['type_guid'], inpt['server_guid'], inpt['server_host'], inpt['server_port'], options)

            if s['s'] is None and s['mode'] == 3:
                return {'code': 1, 'status': 'registered', 'handle': 0, 'mode': s['mode'], 'port': inpt['server_port'], 'outside_port': inpt['outside_port']}
            elif s['s']:
                return {'code': 1, 'status': 'registered', 'handle': s['s'].fileno(), 'mode': s['mode'], 'port': inpt['server_port'], 'outside_port': inpt['outside_port']}
            else:
                return {'code': 0, 'status': 'unknown error'}
        except:
            return xmlrpclib.Fault(1, "Datastar RPC (%s): %s" % sys.exc_info()[:2])

    def export_delete(self, inpt):
        try:
            result = self._owner.unregistersession(inpt['handle'], inpt['type_guid'], inpt['server_guid'])
            if result is True:
                return {'code': 1, 'status': 'unregistered'}
            else:
                return {'code': 0, 'status': 'unknown error'}
        except:
            return xmlrpclib.Fault(1, "Datastar RPC: %s" % traceback.format_exc())


class Router:

    def __init__(self):
        self.leventobjs = {}
        self.sockets = {}
        self.types_by_port = {}
        self.socket_by_port = {}
        self.links = {}
        self.routes = {}
        self.SESS_LOCK = thread.allocate_lock()
        self.port_pool = []
#        self.register_port(2005)
        self.register_xmlrpc_agent()

    def register_xmlrpc_agent(self):
        self.SESS_LOCK.acquire()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', globals()['XMLRPC_PORT']))  # add host_name specific later
        s.listen(4)

        self.sockets[s.fileno()] = {'sock': s, 'special': 'XMLRPC'}  # Register socket

        self.leventobjs[s.fileno()] = event.event(self.libevent_read_callback, handle=s, evtype=event.EV_TIMEOUT | event.EV_READ | event.EV_PERSIST)  # Register callback agent
        if self.leventobjs[s.fileno()] is not None:
            self.leventobjs[s.fileno()].add()  # Add agent to the queue.

        self.SESS_LOCK.release()
        if globals()['cmd_options'].enable_debug is True:
            print "XMLRPC has been registered to port %i" % globals()['XMLRPC_PORT']
        return True

    def register_port(self, outside_port, type_guid, server_guid, server_host, server_port, options=None):
        "Takes a port number, binds it to the server, registers it into the registry, and then returns the socket handle"
        if outside_port not in self.port_pool:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', outside_port))  # add host_name specific later
            s.listen(1)

            self.port_pool += [outside_port]
            if globals()['cmd_options'].enable_debug is True:
                print "We have registered port No. %i" % outside_port
            r = self.registersession(s, 1, type_guid, server_guid, server_host, server_port, options)
            return {'mode': 1, 's': r}
        else:
            r = self.registersession(None, 3, type_guid, server_guid, server_host, server_port, options)
            return {'mode': 3, 's': r}

    def link_manager(self, mode, client, server=None):
        try:
            if mode == 'a' and server is not None:
                self.links[client.fileno()] = {'fn': server.fileno(), 'typ': 'server'}
                self.links[server.fileno()] = {'fn': client.fileno(), 'typ': 'client'}
                if globals()['cmd_options'].enable_debug is True:
                    print "Link up between %s and %s is complete -- Tunneling" % (client.fileno(), server.fileno())
            elif mode == 'r':
                other = self.links[client.fileno()]['fn']
                del self.links[client.fileno()]
                del self.links[other]
                if globals()['cmd_options'].enable_debug is True:
                    print "Link down between %s and %s is complete -- Tunnel closed" % (client.fileno(), other)
        except:
            pass

    def registersession(self, s, mode, type_guid, server_guid, server_host=None, server_port=None, options=None):
        self.SESS_LOCK.acquire()

        if mode == 0:
            self.routes[type_guid][server_guid]['clients'] += [s]
        elif mode == 1 or mode == 3:
            if type_guid in self.routes.keys() is False:
                self.routes[type_guid] = {}
            if mode == 1:
                self.routes[type_guid]['bind'] = s
                self.routes[type_guid]['data'] = {}
            if server_guid in self.routes[type_guid].keys() is False:
                self.routes[type_guid].update({server_guid: {'clients': [],
                                                             'info': {'port': server_port,
                                                                      'host': server_host},
                                                             'data': {},
                                                             'channels': []}})
            else:
                self.routes[type_guid][server_guid]['info'] = {'port': server_port, 'host': server_host, 'bind': s}
                self.routes[type_guid][server_guid]['data'] = {}
            if isinstance(options, type({})):
                for x, y in options.iteritems():
                    self.routes[type_guid][server_guid]['info'][x] = y

            if mode == 3:
                self.SESS_LOCK.release()
                if globals()['cmd_options'].enable_debug is True:
                    print "registered secondary as type %s" % str(mode)
                return s
            else:
                self.types_by_port[str(s.getsockname()[1])] = type_guid

        elif mode == 2:
            self.routes[type_guid][server_guid]['channels'] += [s]

        self.sockets[s.fileno()] = {'sock': s, 'tguid': type_guid, 'sguid': server_guid}  # Register socket

        self.leventobjs[s.fileno()] = event.event(self.libevent_read_callback, handle=s, evtype=event.EV_TIMEOUT | event.EV_READ | event.EV_PERSIST)  # Register callback agent
        if self.leventobjs[s.fileno()] is not None:
            self.leventobjs[s.fileno()].add()  # Add agent to the queue.
        self.SESS_LOCK.release()
        if globals()['cmd_options'].enable_debug is True:
            print "registered socket %s as type %s" % (s.fileno(), str(mode))
        return s

    def unregistersession(self, s=None, type_guid=None, server_guid=None):
        self.SESS_LOCK.acquire()
        if s is not None and s != 0:
            if isinstance(s, type(1)):
                try:
                    s = self.sockets[s]['sock']
                except:
                    self.SESS_LOCK.release()
                    return False

#        if globals()['cmd_options'].enable_debug == True: print 'keys!!!!',len(self.routes[type_guid].keys()), self.routes[type_guid].keys()
        if type_guid is not None and len(self.routes[type_guid].keys()) <= 2:
            s = self.routes[type_guid]['bind']
            self.unregister_port(s)

            if s.fileno() in self.leventobjs.keys() and self.leventobjs[s.fileno()] is not None:
                self.leventobjs[s.fileno()].delete()  # Kill libevent event
                del self.leventobjs[s.fileno()]

            del self.sockets[s.fileno()]  # Destroy the record
            del self.routes[type_guid]

            s.close()  # close our server watching guy!

        try:
            if type_guid is None or server_guid is None and s is not None and s != 0:
                self.routes[self.sockets[s.fileno()]['tguid']][self.sockets[s.fileno()]['sguid']]['clients'].remove(s)
                self.routes[self.sockets[s.fileno()]['tguid']][self.sockets[s.fileno()]['sguid']]['channels'].remove(s)
            elif type_guid is not None and server_guid is not None:
                del self.routes[type_guid][server_guid]
        except:
            pass

        if type_guid is None or server_guid is None and s is not None and s != 0:
            if s.fileno() in self.leventobjs.keys() and self.leventobjs[s.fileno()] is not None:
                self.leventobjs[s.fileno()].delete()  # Kill libevent event
                del self.leventobjs[s.fileno()]
            del self.sockets[s.fileno()]  # Destroy the record
            if globals()['cmd_options'].enable_debug is True:
                print "UNregistered socket %s" % s.fileno()
        else:
            if globals()['cmd_options'].enable_debug is True:
                print "UNregistered socket %s::%s" % (type_guid, server_guid)
        self.SESS_LOCK.release()
        return True

    def unregister_port(self, s):
        if isinstance(s, type(1)):
            try:
                s = self.sockets[s]['sock']
            except:
                return False
        try:
            port = s.getsockname()[1]
            self.port_pool.remove(port)
            del self.types_by_port[str(port)]
            if globals()['cmd_options'].enable_debug is True:
                print "UNREGISTERED PORT %i" % port
            return True
        except:
            return False

    def libevent_read_callback(self, ev, fd, evtype, pipe):
        if isinstance(fd, Client):
            sess = fd
            try:
                data = sess.receive()
            except IOError:  # client closed the connection
                sess.terminate()
                data = ''
            if data:
                sess.route(data, fd.fileno())

        elif isinstance(fd, RPC_Client):
            sess = fd
            try:
                data = sess.receive()
            except IOError:  # client closed the connection
                sess.terminate()
                data = ''
            if data:
                sess.RPC_handler(data)

        elif isinstance(fd, socket.socket):
            conn, addr = fd.accept()
            host, port = fd.getsockname()
            if port in self.port_pool:
                type_guid = self.types_by_port[str(port)]
                server = self.get_good_server(type_guid)
                if server is not None:
                    if globals()['cmd_options'].enable_debug is True:
                        print "Using server %s" % server
                    sess = Client(conn, self, type_guid, server)
                    self.registersession(sess, 0, self.types_by_port[str(port)], sess._sguid)
            elif port == globals()['XMLRPC_PORT']:
                sess = RPC_Client(self, conn, addr, host, port)
                self.registersession(sess, 4, 'I-XR', 'I-XR')
                try:
                    data = sess.receive()
                except IOError:  # client closed the connection
                    sess.terminate()
                    data = ''
                if data:
                    sess.send("")  # let it know that we're ready to accept

        else:
            raise "Unknown instance type: %s" % sock

    def get_good_server(self, type_guid):
        out = {'ratio': 2.0, 'server': None}
        for server, info in self.routes[type_guid].iteritems():
            if server in ['bind', 'data']:
                continue
            server_ratio = len(info['clients']) / (info['info']['conn_max'] * 1.0)
            if 'conn_max' not in info['info'].keys():
                info['info']['conn_max'] = 100  # Change all of this later
            if globals()['cmd_options'].enable_debug is True:
                print "Info:", server, len(info['clients']), info['info']['conn_max'], server_ratio
            if len(info['clients']) < info['info']['conn_max'] and server_ratio < out['ratio']:
                out['ratio'] = server_ratio
                out['server'] = server
        return out['server']

    """def shutdown(self,reason):
        global GLOBAL_TERMINATE
        GLOBAL_TERMINATE = True
        socklist=self.sockets.keys()
        for fileno in socklist:
            s=self.sockets[fileno]
            if isinstance(s,socket.socket):
                self.unregistersession(s)
                s.shutdown(2)
                s.close()
            elif isinstance(s,Client): s.terminate_stream(reason)"""

    def broadcast_shutdown(self):
        message = {'act': 'sd', 'time': time.time()}
        server_num = 0
        for y in self.routes.keys():
            for x in self.routes[y].keys():
                if x not in ['bind', 'data']:
                    print x
                    if 'pass' in self.routes[y][x]['info'].keys():
                        message['pass'] = self.routes[y][x]['info']['pass']
                    xmlrpclib.ServerProxy(self.routes[y][x]['info']['xmlrpc-callback']).socker(message)
                    if 'pass' in message.keys():
                        del message['pass']
                    server_num += 1
        return server_num


def _lib_out(router):
    if globals()['shutdown_in_progress'] is False:  # We don't want to add more shutdown notices to the queue...
        globals()['shutdown_in_progress'] = True
        event.timeout(router.broadcast_shutdown(), event.abort)  # for each server, add one second onto the shutdown timeout..

r = Router()

if cmd_options.enable_test is True:
    options = {'conn_max': 300}
    options2 = {'conn_max': 300}

    inpt = {'outside_port': 9000, 'type_guid': 'apple', 'server_guid': 'co_jp', 'server_host': 'www.apple.co.jp', 'server_port': 80}
    inpt2 = {'outside_port': 9000, 'type_guid': 'apple', 'server_guid': 'com', 'server_host': 'www.apple.com', 'server_port': 80}

    r.register_port(inpt['outside_port'], inpt['type_guid'], inpt['server_guid'], inpt['server_host'], inpt['server_port'], options)
    r.register_port(inpt2['outside_port'], inpt2['type_guid'], inpt2['server_guid'], inpt2['server_host'], inpt2['server_port'], options2)

event.signal(2, _lib_out, r).add()
globals()['shutdown_in_progress'] = False
#Server(r).start()
event.dispatch()
