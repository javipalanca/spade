#!/usr/bin/python
# -*- coding: utf-8 -*-

# XMPPD :: eXtensible Messaging and Presence Protocol Daemon

# Copyright (C) 2012 Javier Palanca & Gustavo Aranda
# Copyright (C) 2005 Kristopher Tate / BlueBridge Technologies Group, Inc.
# Copyright (C) 2004 Alexey Nezhdanov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"XMPPD :: eXtensible Messaging and Presence Protocol Daemon"

__author__ = "Kristopher Tate <kris@bbridgetech.com>"
__version__ = "0.3-RC1"
__copyright__ = "Copyright (C) 2005 BlueBridge Technologies Group, Inc."
__license__ = "GPL"


from xmpp import *
from math import *
import traceback

import socket
import select
import random
import os
import sys
import thread
import errno
import time
import threading
import hashlib
globals()['DEFAULT_LANG'] = 'en'
#globals()['LANG_LIST'] = []

globals()['SERVER_MOTD'] = "Hello, I'm Help Desk. Type 'menu' for help."

globals()['PORT_5222'] = 5222  # Default XMPP port for c2s
globals()['PORT_5223'] = 5223  # Default XMPP port for c2s (w/ TLS)
globals()['PORT_5269'] = 5269  # Default XMPP port for s2s
globals()['PORT_8000'] = 8001  # Port to open for all XMLRPC requests

globals()['MAXREQUESTLENGTH'] = 10000  # maximum allowed length of XML-RPC request (in bytes)
globals()['XMPPD_MAX_CONNECTIONS'] = 1  # [SOCKER] Set maximum number of connections for this node.

globals()['SOCKER_TGUID'] = 'BBTECH_XMPPD'  # CHANGE THIS IF YOU ARE TO USE SOCKER!


GLOBAL_TERMINATE = False

"""
_socket_state live/dead
_session_state   no/in-process/yes
_stream_state not-opened/opened/closing/closed
"""
# Transport-level flags
SOCKET_UNCONNECTED = 0
SOCKET_ALIVE = 1
SOCKET_DEAD = 2
# XML-level flags
STREAM__NOT_OPENED = 1
STREAM__OPENED = 2
STREAM__CLOSING = 3
STREAM__CLOSED = 4
# XMPP-session flags
SESSION_NOT_AUTHED = 1
SESSION_AUTHED = 2
SESSION_BOUND = 3
SESSION_OPENED = 4
# XMLRPC-session flags
XMLRPC_STAGE_ZERO = 0
XMLRPC_STAGE_ONE = 1
XMLRPC_STAGE_TWO = 2
XMLRPC_STAGE_THREE = 4
XMLRPC_STAGE_FOUR = 8


class fake_select:
    def __init__(self):
        ## poll flags
        self.POLLIN = 0x0001
        self.POLLOUT = 0x0004
        self.POLLERR = 0x0008

        ## synonyms
        self.POLLNORM = self.POLLIN
        self.POLLPRI = self.POLLIN
        self.POLLRDNORM = self.POLLIN
        self.POLLRDBAND = self.POLLIN
        self.POLLWRNORM = self.POLLOUT
        self.POLLWRBAND = self.POLLOUT

        ## ignored
        self.POLLHUP = 0x0010
        self.POLLNVAL = 0x0020

    """def select(self, rlist, wlist, xlist, timeout=1.0):
        import select
        return select.select(rlist, wlist, xlist, timeout)"""

    class poll:
        def __init__(self):
            ## poll flags
            self.POLLIN = 0x0001
            self.POLLOUT = 0x0004
            self.POLLERR = 0x0008

            ## synonyms
            self.POLLNORM = self.POLLIN
            self.POLLPRI = self.POLLIN
            self.POLLRDNORM = self.POLLIN
            self.POLLRDBAND = self.POLLIN
            self.POLLWRNORM = self.POLLOUT
            self.POLLWRBAND = self.POLLOUT

            ## ignored
            self.POLLHUP = 0x0010
            self.POLLNVAL = 0x0020
            self._registered = {}

        def register(self, fd, eventmask=None):
            try:
                self._registered[fd.fileno()] = {'fd': fd, 'mask': eventmask}
                return True
            except:
                return False

        def unregister(self, fd):
            try:
                del self._registered[fd.fileno()]
                return True
            except:
                return False

        def poll(self, timeout=None):

            data = {}
            poll = {'in': [], 'out': [], 'err': []}
            out = []
            for x, y in self._registered.iteritems():
                if y['mask'] & self.POLLIN == self.POLLIN:
                    poll['in'] += [y['fd']]
                if y['mask'] & self.POLLOUT == self.POLLOUT:
                    poll['out'] += [y['fd']]
                if y['mask'] & self.POLLERR == self.POLLERR:
                    poll['err'] += [y['fd']]

            #Select does not work with every list empty. PATCH:
            if len(poll['in']) == 0 and len(poll['out']) == 0 and len(poll['err']) == 0:
                if timeout:
                    time.sleep(timeout / 1000.0)
                return out

            if timeout < 1 or timeout is None:
                pi, po, pe = select.select(poll['in'], poll['out'], poll['err'])
            else:
                pi, po, pe = select.select(poll['in'], poll['out'], poll['err'], timeout / 1000.0)

            for x in poll['in']:
                if x in pi:
                    if x.fileno() in data.keys():
                        data[x.fileno()]['mask'] = data[x.fileno()]['mask'] | self.POLLIN
                    else:
                        data[x.fileno()] = {'fd': x, 'mask': self.POLLIN}

            for x in poll['out']:
                if x in po:
                    if x.fileno() in data.keys():
                        data[x.fileno()]['mask'] = data[x.fileno()]['mask'] | self.POLLOUT
                    else:
                        data[x.fileno()] = {'fd': x, 'mask': self.POLLOUT}

            for x in poll['err']:
                if x in pe:
                    if x.fileno() in data.keys():
                        data[x.fileno()]['mask'] = data[x.fileno()]['mask'] | self.POLLERR
                    else:
                        data[x.fileno()] = {'fd': x, 'mask': self.POLLERR}

            for k, d in data.iteritems():
                out += [(k, d['mask'])]
            return out


try:
    select.poll()
except:
    import select as original_select
    select = fake_select()
    select.select = original_select.select


#Import all of the localization files
globals().update({'LANG_LIST': []})
#for m in os.listdir('locale'):
#    if m[:2]=='__' or m[-3:]<>'.py': continue
#    execfile(os.getcwd() + '/locale/' + m[:-3] + '.py')
from locales import *


class localizer:
    def __init__(self, lang=None):
        global DEFAULT_LANG
        self._default = DEFAULT_LANG
        if lang is None or not isinstance(lang, type('')):
            self._lang = DEFAULT_LANG
        else:
            self._lang = lang

    def set_lang(self, lang):
        self._lang = lang
        return True

    def localize(self, val, lang=None):
        if lang is None or lang not in val.keys():
            lang = self._lang
        if lang not in val.keys() and self._default in val.keys():
            lang = self._default

        try:
            return val[lang]
        except:
            if len(val.keys()) > 0:
                return val[val.keys()[0]]
            else:
                return ''

    def build_localeset(self, records):
        for record in records.split('\n')[1:]:
            var, code, text = record.split(' -- ')
            name = var.upper().replace('-', '_')
            #if globals()['cmd_options'].enable_debug == True: print 'adding ' + name + '::' + code
            if name in globals().keys():
                globals()[name].update({code: text})
            else:
                globals()[name] = {code: text}
        del var, code, text


class Session_Dummy:
    "Session_Dummy is used to trick dispatch into actually sending information!"
    def __init__(self, server):
        self.Stream()
        self.DEBUG = server.Dispatcher.DEBUG
        self._expected = {}

    class Stream:
        def __init__(self):
            self._mini_dom = None


class Session:
    def __init__(self, socket, server, xmlns, peer=None):
        self._lock = thread.allocate_lock()
        self.xmlns = xmlns
        if peer:
            self.TYP = 'client'
            self.peer = peer
            self._socket_state = SOCKET_UNCONNECTED
        else:
            self.TYP = 'server'
            self.peer = None
            self._socket_state = SOCKET_ALIVE
            server.num_servers += 1
        self._sock = socket
        self._send = socket.send
        self._recv = socket.recv
        self._registered = 0
        self.trusted = 0
        self.conn_since = time.time()
        self.last_seen = time.time()
        self.isAdmin = False

        self.Dispatcher = server.Dispatcher
        self.DBG_LINE = 'session'
        self.DEBUG = server.Dispatcher.DEBUG
        self._expected = {}
        self._owner = server
        if self.TYP == 'server':
            #self.ID = `random.random()`[2:]
            self.ID = repr(random.random())[2:]
        else:
            self.ID = None

        self.sendbuffer = ''
        self.lib_event = None
        self._stream_pos_queued = None
        self._stream_pos_sent = 0
        self.deliver_key_queue = []
        self.deliver_queue_map = {}
        self.stanza_queue = []

        self._session_state = SESSION_NOT_AUTHED
        self.waiting_features = []
        for feature in [NS_TLS, NS_SASL, NS_BIND, NS_SESSION]:
            if feature in server.features:
                self.waiting_features.append(feature)
        self.features = []
        self.feature_in_process = None
        self.slave_session = None
        self.StartStream()

    def StartStream(self):
        self._stream_state = STREAM__NOT_OPENED
        self.Stream = simplexml.NodeBuilder()
        self.Stream._dispatch_depth = 2
        self.Stream.dispatch = self.dispatch
        self.Parse = self.Stream.Parse
        self.Stream.stream_footer_received = self._stream_close
        if self.TYP == 'client':
            self.Stream.stream_header_received = self._catch_stream_id
            self._stream_open()
        else:
            self.Stream.stream_header_received = self._stream_open

    def receive(self):
        """Reads all pending incoming data. Raises IOError on disconnect."""
        try:
            received = self._recv(10240)
        except:
            received = ''

        if len(received):  # length of 0 means disconnect
            #self.DEBUG(`self._sock.fileno()`+' ' + received, 'got')
            self.DEBUG(repr(self._sock.fileno()) + ' ' + received, 'got')
            self.last_seen = time.time()
        else:
            self.DEBUG(self._owner._l(SESSION_RECEIVE_ERROR), 'error')
            self.set_socket_state(SOCKET_DEAD)
            raise IOError("Peer disconnected")
        return received

    def send(self, chunk):
        try:
            if isinstance(chunk, Node):
                chunk = unicode(chunk).encode('utf-8')
            elif type(chunk) == type(u''):
                chunk = chunk.encode('utf-8')
            #self.enqueue(chunk)
        except:
            pass
        self.enqueue(chunk)

    def enqueue(self, stanza):
        """ Takes Protocol instance as argument. """
        self._lock.acquire()
        try:
            self._owner.num_messages += 1
            if isinstance(stanza, Protocol):
                self.stanza_queue.append(stanza)
            else:
                self.sendbuffer += str(stanza)
            if self._socket_state >= SOCKET_ALIVE:
                self.push_queue()
        finally:
            self._lock.release()

    def push_queue(self, failreason=ERR_RECIPIENT_UNAVAILABLE):

        if self._stream_state >= STREAM__CLOSED or self._socket_state >= SOCKET_DEAD:  # the stream failed. Return all stanzas that are still waiting for delivery.
            self._owner.deactivatesession(self)
            self.trusted = 1
            for key in self.deliver_key_queue:                            # Not sure. May be I
                self.dispatch(Error(self.deliver_queue_map[key], failreason))  # should simply re-dispatch it?
            for stanza in self.stanza_queue:                              # But such action can invoke
                self.dispatch(Error(stanza, failreason))                   # Infinite loops in case of S2S connection...
            self.deliver_queue_map, self.deliver_key_queue, self.stanza_queue = {}, [], []
            return
        elif self._session_state >= SESSION_AUTHED:       # FIXME!
            #### LOCK_QUEUE
            for stanza in self.stanza_queue:
                txt = stanza.__str__().encode('utf-8')
                self.sendbuffer += txt
                self._stream_pos_queued += len(txt)       # should be re-evaluated for SSL connection.
                self.deliver_queue_map[self._stream_pos_queued] = stanza     # position of the stream when stanza will be successfully and fully sent
                self.deliver_key_queue.append(self._stream_pos_queued)
            self.stanza_queue = []
            #### UNLOCK_QUEUE

        if self.sendbuffer and select.select([], [self._sock], [])[1]:
            try:
                # LOCK_QUEUE
                sent = self._send(str(self.sendbuffer))
            except Exception, err:
                #self.DEBUG('server','Attempting to kill %i!!!\n%s'%(self._sock.fileno(),err),'warn')
                self.DEBUG('Attempting to kill %i!!!\n%s' % (self._sock.fileno(), err), 'warn')
                # UNLOCK_QUEUE
                self.set_socket_state(SOCKET_DEAD)
                self.DEBUG(self._owner._l(SESSION_SEND_ERROR), 'error')
                return self.terminate_stream()
            #self.DEBUG(`self._sock.fileno()`+' ' + self.sendbuffer[:sent], 'sent')
            self.DEBUG(repr(self._sock.fileno()) + ' ' + self.sendbuffer[:sent], 'sent')
            self._stream_pos_sent += sent
            self.sendbuffer = self.sendbuffer[sent:]
            self._stream_pos_delivered = self._stream_pos_sent            # Should be acquired from socket somehow. Take SSL into account.
            while self.deliver_key_queue and self._stream_pos_delivered > self.deliver_key_queue[0]:
                del self.deliver_queue_map[self.deliver_key_queue[0]]
                self.deliver_key_queue.remove(self.deliver_key_queue[0])
            # UNLOCK_QUEUE
        """
        elif self.lib_event == None:
            if globals()['cmd_options'].enable_debug == True: print 'starting-up libevent write-event for %i'%self._sock.fileno()
            self.lib_event = event.write(self._sock,self.libevent_write)
            self.lib_event.add()
        else:
            self.lib_event.add()"""

    def libevent_write(self):
        if self.sendbuffer:

            try:
                # LOCK_QUEUE
                sent = self._send(str(self.sendbuffer))
            except Exception, err:
                self.DEBUG('server', 'Attempting to kill %i!!!\n%s' % (self._sock.fileno(), err), 'warn')
                # UNLOCK_QUEUE
                self.set_socket_state(SOCKET_DEAD)
                self.DEBUG(self._owner._l(SESSION_SEND_ERROR), 'error')
                return self.terminate_stream()
            #self.DEBUG(`self._sock.fileno()`+' ' + self.sendbuffer[:sent], 'sent')
            self.DEBUG(repr(self._sock.fileno()) + ' ' + self.sendbuffer[:sent], 'sent')
            self._stream_pos_sent += sent
            self.sendbuffer = self.sendbuffer[sent:]
            self._stream_pos_delivered = self._stream_pos_sent            # Should be acquired from socket somehow. Take SSL into account.
            while self.deliver_key_queue and self._stream_pos_delivered > self.deliver_key_queue[0]:
                del self.deliver_queue_map[self.deliver_key_queue[0]]
                self.deliver_key_queue.remove(self.deliver_key_queue[0])
            # UNLOCK_QUEUE

    def dispatch(self, stanza):
        if self._stream_state == STREAM__OPENED:                  # if the server really should reject all stanzas after he is closed stream (himeself)?
            self.DEBUG(stanza.__str__(), 'dispatch')
            return self.Dispatcher.dispatch(stanza, self)

    def fileno(self):
        return self._sock.fileno()

    def _catch_stream_id(self, ns=None, tag='stream', attrs={}):
        if 'id' not in attrs.keys() or not attrs['id']:
            return self.terminate_stream(STREAM_INVALID_XML)
        self.ID = attrs['id']
        if 'version' not in attrs.keys():
            self._owner.Dialback(self)

    def _stream_open(self, ns=None, tag='stream', attrs={}):
        text = '<?xml version="1.0" encoding="utf-8"?>\n<stream:stream'
        if self.TYP == 'client':
            text += ' to="%s"' % self.peer
        else:
            text += ' id="%s"' % self.ID
            if 'to' not in attrs.keys():
                text += ' from="%s"' % self._owner.servernames[0]
            else:
                text += ' from="%s"' % attrs['to']
        if 'xml:lang' in attrs.keys():
            text += ' xml:lang="%s"' % attrs['xml:lang']
        #if self.xmlns: xmlns=self.xmlns
        if self.Stream.xmlns in [NS_CLIENT, NS_COMPONENT_ACCEPT]:
            self.xmlns = xmlns = self.Stream.xmlns
        else:
            xmlns = NS_SERVER
        text += ' xmlns:db="%s" xmlns:stream="%s" xmlns="%s"' % (NS_DIALBACK, NS_STREAMS, xmlns)
        if 'version' in attrs.keys() or self.TYP == 'client':
            text += ' version="1.0"'
        self.send(text + '>')
        self.set_stream_state(STREAM__OPENED)
        if self.TYP == 'client':
            return
        if tag != 'stream':
            return self.terminate_stream(STREAM_INVALID_XML)
        if ns != NS_STREAMS:
            return self.terminate_stream(STREAM_INVALID_NAMESPACE)
        if self.Stream.xmlns != self.xmlns:
            return self.terminate_stream(STREAM_BAD_NAMESPACE_PREFIX)
        if 'to' not in attrs.keys():
            return self.terminate_stream(STREAM_IMPROPER_ADDRESSING)
        if attrs['to'] not in self._owner.servernames:
            return self.terminate_stream(STREAM_HOST_UNKNOWN)
        self.ourname = attrs['to'].lower()
        if self.TYP == 'server' and 'version' in attrs.keys():
            self.send_features()

    def send_features(self):
        features = Node('stream:features')
        if NS_TLS in self.waiting_features:
            features.NT.starttls.setNamespace(NS_TLS)
            features.T.starttls.NT.required
        if NS_SASL in self.waiting_features:
            features.NT.mechanisms.setNamespace(NS_SASL)
            for mec in self._owner.SASL.mechanisms:
                features.T.mechanisms.NT.mechanism = mec
        else:
            if NS_BIND in self.waiting_features:
                features.NT.bind.setNamespace(NS_BIND)
            if NS_SESSION in self.waiting_features:
                features.NT.session.setNamespace(NS_SESSION)
        self.send(features)

    def getResource(self):
        jid = self.peer
        try:
            barejid, resource = jid.split('/')
        except:
            return None
        return resource

    def getRoster(self):
        split_jid = self.getSplitJID()
        return self._owner.DB.get(split_jid[1], split_jid[0], 'roster')

    def getGroups(self):
        split_jid = self.getSplitJID()
        return self._owner.DB.get(split_jid[1], split_jid[0], 'groups')

    def getName(self):
        split_jid = self.getSplitJID()
        name = self._owner.DB.get(split_jid[1], split_jid[0], 'name')
        if name is None:
            name = '%s@%s' % split_jid[0:2]
        return name

    def getSplitJID(self):
        return self._owner.tool_split_jid(self.peer)

    def getBareJID(self):
        try:
            return '%s@%s' % self.getSplitJID()[0:2]
        except:
            # Component JID
            return self.peer.split("/")[0]

    def getKarma(self):
        split_jid = self.getSplitJID()
        if split_jid is not None:
            return self._owner.DB.get_store(split_jid[1], split_jid[0], 'karma')
        else:
            return None

    def updateKarma(self, karma):
        split_jid = self.getSplitJID()
        if split_jid is not None:
            return self._owner.DB.store(split_jid[1], split_jid[0], karma, 'karma')
        else:
            return None

    def feature(self, feature):
        if feature not in self.features:
            self.features.append(feature)
        self.unfeature(feature)

    def unfeature(self, feature):
        if feature in self.waiting_features:
            self.waiting_features.remove(feature)

    def _stream_close(self, unregister=1):
        if self._stream_state >= STREAM__CLOSED:
            return
        self.set_stream_state(STREAM__CLOSING)
        self.send('</stream:stream>')
        self.set_stream_state(STREAM__CLOSED)
        self.push_queue()       # decompose queue really since STREAM__CLOSED
        if unregister:
            self._owner.unregistersession(self)
        if self.lib_event is not None:
            self.lib_event.delete()
        self._destroy_socket()

    def terminate_stream(self, error=None, unregister=1):
        if self._stream_state >= STREAM__CLOSING:
            return
        if self._stream_state < STREAM__OPENED:
            self.set_stream_state(STREAM__CLOSING)
            self._stream_open()
        else:
            self.set_stream_state(STREAM__CLOSING)
            p = Presence(typ='unavailable')
            p.setNamespace(NS_CLIENT)
            self.Dispatcher.dispatch(p, self)
        if error:
            if isinstance(error, Node):
                self.send(error)
            else:
                self.send(ErrorNode(error))
        self._stream_close(unregister=unregister)
        if self.slave_session:
            self.slave_session.terminate_stream(STREAM_REMOTE_CONNECTION_FAILED)

    def _destroy_socket(self):
        """ breaking cyclic dependancy to let python's GC free memory just now """
        self.Stream.dispatch = None
        self.Stream.stream_footer_received = None
        self.Stream.stream_header_received = None
        self.Stream.destroy()
        self._sock.close()
        self.set_socket_state(SOCKET_DEAD)

    def start_feature(self, f):
        if self.feature_in_process:
            raise "Starting feature %s over %s !" % (f, self.feature_in_process)
        self.feature_in_process = f

    def stop_feature(self, f):
        if self.feature_in_process != f:
            self.DEBUG("Stopping feature %s instead of %s !" % (f, self.feature_in_process), 'info')
        self.feature_in_process = None

    def set_socket_state(self, newstate):
        if self._socket_state < newstate:
            self._socket_state = newstate

    def set_session_state(self, newstate):
        if self._session_state < newstate:
            if self._session_state < SESSION_AUTHED and \
                    newstate >= SESSION_AUTHED:
                self._stream_pos_queued = self._stream_pos_sent
            self._session_state = newstate
            split_jid = self.getSplitJID()
            if split_jid is not None and split_jid[0] in self._owner.administrators[self.ourname]:
                self.isAdmin = True
                self.DEBUG(self._owner._l(SESSION_ADMIN_SET) % str(split_jid[0]), 'info')
#            if newstate==SESSION_OPENED: self.enqueue(Message(self.peer,SERVER_MOTD,frm=self.ourname))     # Remove in prod. quality server
            if newstate == SESSION_OPENED:
                # Enqueue previously stored messages
                for msg in self._owner.DB.get_storage(self.peer, ""):
                    #print "### ENQ ", str(msg)
                    self.enqueue(msg)

    def set_stream_state(self, newstate):
        if self._stream_state < newstate:
            self._stream_state = newstate


class Socker_client:
    def __init__(self, owner, socker_host, tguid, sguid=None):
        self._owner = owner
        self._proxy = xmlrpclib.ServerProxy('http://%s' % socker_host)

        try:  # See if the Socker server will say hello...
            ok_res = self._proxy.hello({})
            if ok_res['code'] == 1:
                self.conn_okay = True
        except:
            self.conn_okay = False

        self._tguid = tguid
        if self.owner.cmd_options.setdefault('hostname', False) is not None:
            self.owner.DEBUG('server', "[SOCKER] hostname set to <%s>" % self.owner.cmd_options['hostname'], 'info')
            self._hostname = str(self.owner.cmd_options['hostname'])
        else:
            self._hostname = None

        if sguid is None:
            self._sguid = self.get_uuid()
        else:
            self._sguid = sguid

        self._chain = {}
        self.fake_to_real_port = {}
        self._registered = []

    def get_uuid(self):
        if self.conn_okay is True:
            return self._proxy.uuidgen({})
        else:
            return None

    def get_hostname(self):
        if self.conn_okay is True:
            res = self._proxy.hostname({})
            if 'hostname' in res.keys():
                self._hostname = res['hostname']
                return res['hostname']
            else:
                return None
        else:
            return None

    def get_sguid(self):
        return self._sguid

    def get_tguid(self):
        return self._tguid

    def send_broadcast(self, stanza):
        if self.conn_okay is True:
            res = self._proxy.broadcast({'type_guid': self._tguid + '_p%s' % str(self.fake_to_real_port[str(globals()['PORT_5222'])]), 'server_guid': self._sguid, 'stanza': stanza})  # Send broadcast to Socker
            if res['code'] != 1:
                return None
            else:
                return res

    def add_port(self, outside_port, host, port, options=None):
        self.onwer.DEBUG('server' "[SOCKER] attempting to add route to Socker [%s]" % str((outside_port, host, port, options)), 'info')
        if host is None and self._hostname is not None:
            host = self._hostname
        elif host is None and self._hostname is None:
            host = self.get_hostname()

        self._chain[self._tguid + '_p%s' % str(outside_port)] = self._proxy.getchain({'type_guid': self._tguid + '_p%s' % str(outside_port)})
        if self._chain[self._tguid + '_p%s' % str(outside_port)]['code'] != 1:
            del self._chain[self._tguid + '_p%s' % str(outside_port)]

        inpt = {'outside_port': outside_port, 'type_guid': self._tguid + '_p%s' % str(outside_port), 'server_guid': self._sguid, 'server_host': host, 'server_port': port}
        if options is not None:
            inpt.update(options)

        if self.conn_okay is True:
            res = self._proxy.add(inpt)  # Send request to Socker
            if res['code'] != 1:
                return None
            else:
                self._registered += [res]
                self.fake_to_real_port[str(port)] = outside_port
                return res
        else:
            return None

    def add_data(self, data):
        if self.conn_okay is True:
            res = self._proxy.data({'act': 'add', 'type_guid': self._tguid + '_p%s' % str(self.fake_to_real_port[str(globals()['PORT_5222'])]), 'server_guid': self._sguid, 'pass': globals()['RPC_PASSWORD'], 'add': data})
            if res['code'] == 1:
                return True
        return False

    def remove_data(self, data):
        if self.conn_okay is True:
            res = self._proxy.data({'act': 'remove', 'type_guid': self._tguid + '_p%s' % str(self.fake_to_real_port[str(globals()['PORT_5222'])]), 'server_guid': self._sguid, 'pass': globals()['RPC_PASSWORD'], 'remove': data})
            if res['code'] == 1:
                return True
        return False

    def add_data_root(self, data):
        if self.conn_okay is True:
            res = self._proxy.data({'act': 'add', 'type_guid': self._tguid + '_p%s' % str(self.fake_to_real_port[str(globals()['PORT_5222'])]), 'pass': globals()['RPC_PASSWORD'], 'add': data})
            if res['code'] == 1:
                return True
        return False

    def remove_data_root(self, data):
        if self.conn_okay is True:
            res = self._proxy.data({'act': 'remove', 'type_guid': self._tguid + '_p%s' % str(self.fake_to_real_port[str(globals()['PORT_5222'])]), 'pass': globals()['RPC_PASSWORD'], 'remove': data})
            if res['code'] == 1:
                return True
        return False

    def destroy(self):
        for registered in self._registered:
            res = self._proxy.delete({'handle': registered['handle'], 'type_guid': self._tguid + '_p%s' % str(registered['outside_port']), 'server_guid': self._sguid})  # Send request to Socker

        if res['code'] != 1:
            return None
        else:
            self._registered = []
            return res


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
            func = getattr(self, 'rpcexport_' + method)
        except AttributeError:
            raise Exception('method "%s" is not supported' % method)
        else:
            result = func(*params)
            if getattr(result, 'faultCode', None) is None:
                result = (result,)
            return result

    def rpcexport_socker(self, inpt):
        "RPC endpoint for all Socker™ related inquiries."

        if 'pass' not in inpt or inpt['pass'] != globals()['RPC_PASSWORD']:
            return {'code': 0, 'msg': 'PASS-BAD'}

        if inpt['act'] == 'bc':
            try:
                self._owner.Dispatcher.dispatch(Node(node=inpt['stanza']), Session_Dummy(self._owner))
            except:
                pass
            return {'code': 1, 'msg': 'BC-OK'}
        elif inpt['act'] == 'sd':
            try:
                if inpt['time'] > time.time():
                    event.timeout(int(time.time() - inpt['time']), self._owner._lib_out)
                else:
                    event.timeout(1, self._owner._lib_out)
            except:
                pass
            return {'code': 1, 'msg': 'SD-OK'}
        return {'code': 0, 'msg': 'RC-BAD'}

    def rpcexport_hello(self, inpt):
        return {'code': 1, 'msg': 'Hello!'}

    def rpcexport_status(self, inpt):
        "RPC endpoint to get status information"
        return {'code': 1, 'msg': 'RC-OK', 'data': self._owner.tool_get_status()}


class multisession_manager:

    def __init__(self, owner, nthreads=32):

        self._owner = owner
        self.nthreads = nthreads

        self.threads = {}

        for i in range(0, nthreads):
            t = self.multisession_thread(self._owner, i)
            t.start()
            self.threads[i] = t

    def destroy(self):
        for t in self.threads.values():
            t.stop()

    def select_thread(self):
        return random.choice(self.threads.values())

    def registersession(self, s):
        self.select_thread().registersession(s)

    def unregistersession(self, s):
        self.threads[s.thread_id].unregistersession(s)

    class multisession_thread(threading.Thread):

        def __init__(self, owner, index):

            threading.Thread.__init__(self)
            self.setDaemon(False)
            self.setName("multisession_thread:" + str(index))
            self._alive = True  # Boolean attribute indicating wether the thread is alive

            self.sockpoll = select.poll()
            self.sockets = {}
            self.SESS_LOCK = thread.allocate_lock()

            self._owner = owner
            self.index = index

        def run(self):
            while self._alive:  # and self.isAlive():
                try:
                    for fileno, ev in self.sockpoll.poll(1000):
                        try:
                            sess = self.sockets[fileno]
                        except:
                            sess = None
                        if isinstance(sess, Session):
                            try:
                                data = sess.receive()
                            except IOError:  # client closed the connection
                                sess.terminate_stream()
                                self.unregistersession(sess)
                                data = ''
                            if data:
                                try:
                                    sess.Parse(data)
                                except simplexml.xml.parsers.expat.ExpatError:
                                    sess.terminate_stream(STREAM_XML_NOT_WELL_FORMED)
                                    self.unregistersession(sess)
                                if time.time() - sess.last_seen >= 60.0:
                                    sess.terminate_stream()
                                    self.unregistersession(sess)
                except:
                    pass

        def stop(self):
            self._alive = False

        def registersession(self, s):
            self.SESS_LOCK.acquire()
            s.thread_id = self.index
            if isinstance(s, Session):
                if s._registered:
                    self.SESS_LOCK.release()
                    return
                s._registered = 1
            self.sockets[s.fileno()] = s
            self.sockpoll.register(s, 1 | 2 | 8)
            self.SESS_LOCK.release()

        def unregistersession(self, s):
            self.SESS_LOCK.acquire()
            if isinstance(s, Session):
                if not s._registered:
                    p = Presence(typ='unavailable')
                    p.setNamespace(NS_CLIENT)
                    self._owner.Dispatcher.dispatch(p, s)
                    self.SESS_LOCK.release()
                    return
                s._registered = 0
                self.sockpoll.unregister(s)

            del self.sockets[s.fileno()]  # Destroy the record
            self._owner.DEBUG('server', self._owner._l(SERVER_NODE_UNREGISTERED) % {'fileno': s.fileno(), 'raw': s})
            self.SESS_LOCK.release()


class Server:
    def __init__(self, cfgfile="./xmppd.xml", cmd_options={}, under_restart=False):
#        threading.Thread.__init__(self)
        self.defaultNamespace = NS_CLIENT
        #Load localizer as _l
        self.l = localizer()
        self._l = self.l.localize
        for x in globals()['LANG_LIST']:
            self.l.build_localeset(x)

        cmd_options.setdefault('select_enabled', False)
        try:
            import event   # Do we have lib event???
            #print "LIBEVENT ENABLED"
        except:
            cmd_options['select_enabled'] = True  # If not, we'll have to just use the old select :/
            #print "SELECT ENABLED"
        if not cmd_options['select_enabled']:
            event.init()

        # Components dict
        self.components = {}

        self.sockets = {}
        self.leventobjs = {}

        debug_path = cmd_options.setdefault('debug_file', sys.stdout)
        if debug_path != sys.stdout:
            debug_file = file(debug_path, 'w+')
        else:
            debug_file = debug_path
        if cmd_options.setdefault('enable_debug', []) != []:
            debug = ['always']
        else:
            debug = []
        self._DEBUG = Debug.Debug(debug, debug_path)
        self.DEBUG = self._DEBUG.Show
        self.debug_flags = self._DEBUG.debug_flags
        self.debug_flags.append('session')
        self.debug_flags.append('dispatcher')
        self.debug_flags.append('server')

        if cmd_options['select_enabled'] is not True:  # and getattr(select,'poll',None) == None:
            self.sockpoll = fake_select.poll()
            self.DEBUG('server', 'Using fake_select poll', 'info')
        elif cmd_options['select_enabled'] is True:
            self.sockpoll = select.poll()
            self.DEBUG('server', 'Using select poll', 'info')

        #self.ID = `random.random()`[2:]
        self.ID = repr(random.random())[2:]

        #Config file
        self.cfgfile = cfgfile
        if not os.path.exists(self.cfgfile):
            self.DEBUG('server', 'Could not load configuration file for xmppd. Bye', 'error')
            self.shutdown(STREAM_SYSTEM_SHUTDOWN)
            sys.exit(1)

        if cmd_options.setdefault('enable_psyco', False):
            self.DEBUG('server', "Starting PsyCo...", 'info')
            try:
                import psyco
                #psyco.log()
                psyco.full()
                self.DEBUG('server', "PsyCo is loaded.", 'ok')
            except:
                self.DEBUG('server', "Could not Load PsyCo!", 'error')

        if cmd_options.setdefault('socker_info', False):
            import xmlrpclib

        if not cmd_options.setdefault('password', None):
            globals()['RPC_PASSWORD'] = hashlib.sha1(str(time.time()) + globals()['SOCKER_TGUID'] + hashlib.sha1(str(time.time())).hexdigest()).hexdigest()
        else:
            globals()['RPC_PASSWORD'] = cmd_options['password']

        self.DEBUG('server', "[SECURITY] RPC_PASSWORD SET TO [%(pass)s]" % {'pass': globals()['RPC_PASSWORD']}, 'info')

        #Temp lang stuff
        globals()['DEFAULT_LANG'] = cmd_options.setdefault('language', 'en')  # Changed to the --lang flag

        self.multisession_manager = multisession_manager(self)

        self._component = 0
        self.SESS_LOCK = thread.allocate_lock()
        self.Dispatcher = dispatcher.Dispatcher()
        self.Dispatcher._owner = self
        self.Dispatcher._init()

        #stats
        self.up_since = time.time()
        self.num_messages = 0
        self.num_servers = 0

        self.features = []

        self.routes = {}
        self.sisters = {}

        import modules
        if under_restart is True:
            reload(modules)
        for addon in modules.addons:
            #if issubclass(addon,PlugIn):
            try:
                if addon().__class__.__name__ in self.__dict__.keys() and under_restart is True:
                    #self.DEBUG('server','Plugging-out?','info')

                    self.DEBUG('server', 'Plugging %s out of %s.' % (addon(), self), 'stop')
                    if addon().DBG_LINE in self.debug_flags:
                        self.debug_flags.remove(addon().DBG_LINE)
                    if getattr(addon(), '_exported_methods', None) is not None:
                        for method in addon()._exported_methods:
                            del self.__dict__[method.__name__]
                    if getattr(addon(), '_old_owners_methods', None) is not None:
                        for method in addon()._old_owners_methods:
                            self.__dict__[method.__name__] = method
                    del self.__dict__[addon().__class__.__name__]
                    if 'plugout' in addon().__class__.__dict__.keys():
                        return addon().plugout()

                    addon().PlugIn(self)
                else:
                    addon().PlugIn(self)
            #else: self.__dict__[addon().__class__.__name__]=addon()
            except:
                self.__dict__[addon().__class__.__name__] = addon()
            self.feature(addon.NS)

        self.cmd_options = cmd_options

        self._socker = None
        if cmd_options.setdefault('socker_info', None):
            self._socker = Socker_client(self, cmd_options['socker_info'], globals()['SOCKER_TGUID'])
        if self._socker is not None and self._socker.conn_okay is True:
            self.DEBUG('server', "[SOCKER] Socker(tm) support is enabled.", 'info')
            self.DEBUG('server' "[SOCKER] Randomizing incoming connection ports.", 'info')

            #Generate port map
            guide = [[globals()['PORT_5222'], self.pick_rand(), '5222'], [globals()['PORT_5223'], self.pick_rand(), '5223'], [globals()['PORT_5269'], self.pick_rand(), '5269'], [globals()['PORT_8000'], self.pick_rand(), '8000']]

            port_map = {}
            for x in guide:
                if x[2] != '8000':
                    port_map[str(x[0])] = x[1]
                globals()['PORT_%s' % x[2]] = x[1]

            for port, new_port in port_map.iteritems():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', new_port))
                sock.listen(4)
                self.registersession(sock)
                info = self._socker.add_port(int(port), None, new_port, {'conn_max': globals()['XMPPD_MAX_CONNECTIONS'], 'xmlrpc-callback': 'http://%s:%i' % (self._socker._hostname, globals()['PORT_8000']), 'pass': globals()['RPC_PASSWORD']})
                if info is None:
                    self._socker.destroy()
                    raise Exception
        else:
            if cmd_options.setdefault('socker_info', None):
                self.DEBUG('server', "[SOCKER] Socker(tm) support could not be enabled. Please make sure that the Socker server is active.", 'error')
            self._socker = None
            for port in [globals()['PORT_5222'], globals()['PORT_5223'], globals()['PORT_5269']]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                sock.listen(4)
                self.registersession(sock)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', globals()['PORT_8000']))  # add host_name specific later
        s.listen(4)

        if cmd_options['select_enabled'] is True:
            reg_method = 'select'
            self.sockpoll.register(s, 1 | 2 | 8)
        else:  # event
            reg_method = 'libevent'
            self.leventobjs[s.fileno()] = event.event(self.libevent_read_callback, handle=s, evtype=event.EV_TIMEOUT | event.EV_READ | event.EV_PERSIST)
            if self.leventobjs[s.fileno()] is not None:
                self.leventobjs[s.fileno()].add()
        self.sockets[s.fileno()] = s

    def tool_split_jid(self, jid):
        "Returns tuple of id,server,resource"
        if "@" in jid:
            try:
                name, extras = jid.split('@')
            except:
                return None
            try:
                server, resource = extras.split('/')
            except:
                return (name, extras)
            return (name, server, resource)
        else:  # Component or Server
            if "/" in jid:  # With resource
                server, resource = jid.split("/")
                return (server, resource)
            else:  # No resource, only dots
                return (jid)

    def tool_timeDurration(self, the_time):
        days = floor(the_time / 60 / 60 / 24)
        hours = floor((the_time - days * 60 * 60 * 24) / 60 / 60)
        minutes = floor((the_time - days * 60 * 60 * 24 - hours * 60 * 60) / 60)
        seconds = floor((the_time - days * 60 * 60 * 24 - hours * 60 * 60 - minutes * 60))
        return (days, hours, minutes, seconds)

    def tool_readableTimeDurration(self, in_time):
        if type(in_time) != ((1,)):
            in_time = self.tool_timeDurration(in_time)
        out = ''
        if in_time[0] >= 1:
            out += '%i%s ' % (in_time[0], 'd')
        if in_time[1] >= 1:
            out += '%i%s ' % (in_time[1], 'h')
        if in_time[2] >= 1:
            out += '%i%s ' % (in_time[2], 'm')
        if in_time[3] >= 1:
            out += '%i%s ' % (in_time[3], 's')
        return out

    def tool_get_status(self):
        "Get this node's status"
        data = {}
        data['soft'] = 'BlueBridge Jibber-Jabber 0.3'

        data['no_registered'] = {}
        for x in self.servernames:
            data['no_registered'][x] = self.DB.getNumRegistered(x)

        data['uptime'] = self.tool_readableTimeDurration(time.time() - self.up_since)
        data['raw_uptime'] = time.time() - self.up_since
        data['no_routes'] = len(self.routes.keys())
        data['no_reg_users_conn'] = len(self.Router._data)
        data['no_conn_servers'] = self.num_servers
        data['no_msg_routed'] = self.num_messages
        return data

    def feature(self, feature):
        if feature and feature not in self.features:
            self.features.append(feature)

    def unfeature(self, feature):
        if feature and feature in self.features:
            self.features.remove(feature)

    def registersession(self, s):
        self.SESS_LOCK.acquire()
        if isinstance(s, Session):
            if s._registered:
                self.SESS_LOCK.release()
                if self._DEBUG.active:
                    raise "Twice session Registration!"
                else:
                    return
            #s._registered=1
            self.multisession_manager.registersession(s)
            self.SESS_LOCK.release()
            return
        reg_method = ''
        self.sockets[s.fileno()] = s
        if self.cmd_options['select_enabled'] is True:
            reg_method = 'select'
            self.sockpoll.register(s, 1 | 2 | 8)
        else:  # if 'event' in globals().keys():
            reg_method = 'libevent'
            self.leventobjs[s.fileno()] = event.event(self.libevent_read_callback, handle=s, evtype=event.EV_TIMEOUT | event.EV_READ | event.EV_PERSIST)
            if self.leventobjs[s.fileno()] is not None:
                self.leventobjs[s.fileno()].add()
        if isinstance(self._socker, Socker_client):
            socker_notice = "->[SOCKER(TM)]"
        else:
            socker_notice = ''
        self.DEBUG('server', self._l(SERVER_NODE_REGISTERED) % {'fileno': s.fileno(), 'raw': s, 'method': reg_method, 'socker_notice': socker_notice})
        self.SESS_LOCK.release()

    def unregistersession(self, s):
        self.SESS_LOCK.acquire()
        if isinstance(s, Session):
            if not s._registered:
                p = Presence(typ='unavailable')
                p.setNamespace(NS_CLIENT)
                self.Dispatcher.dispatch(p, s)
                self.SESS_LOCK.release()
                if self._DEBUG.active:
                    raise "Twice session UNregistration!"
                else:
                    return
            #s._registered=0
            self.multisession_manager.unregistersession(s)
            self.SESS_LOCK.release()
            return
        if getattr(self, 'sockpoll', None) is not None:
            self.sockpoll.unregister(s)
        elif s.fileno() in self.leventobjs.keys() and self.leventobjs[s.fileno()] is not None:
            self.leventobjs[s.fileno()].delete()  # Kill libevent event
            del self.leventobjs[s.fileno()]

        del self.sockets[s.fileno()]  # Destroy the record
        self.DEBUG('server', self._l(SERVER_NODE_UNREGISTERED) % {'fileno': s.fileno(), 'raw': s})
        self.SESS_LOCK.release()

    def activatesession(self, s, peer=None):
        #print "### TRYING TO ACTIVATE SESSION %s WITH PEER %s"%(str(s),str(peer))
        try:
            if not peer:
                peer = s.peer
            alt_s = self.getsession(peer)
            if s == alt_s:
                return
            elif alt_s:
                self.deactivatesession(peer)
            self.routes[peer] = s
        except Exception, e:
            print "###########ERRORRRRRRRRR  " + str(e)
        #print "### ACTIVATED SESSION %s WITH PEER %s"%(str(s),str(peer))

    def getsession(self, jid):
        try:
            return self.routes[jid]
        except KeyError:
            pass

    def deactivatesession(self, peer):
        s = self.getsession(peer)
        if peer in self.routes.keys():
            del self.routes[peer]
        if peer in self.sisters.keys():
            del self.sisters[peer]
        #print "### TRYING TO DE-ACTIVATE SESSION OF PEER %s : %s"%(str(peer),str(s))
        return s

    def run(self):
        global GLOBAL_TERMINATE
        if 'event' in globals().keys():
            event.signal(2, self._lib_out).add()
        if self.cmd_options['select_enabled'] is True:
            while GLOBAL_TERMINATE is False:
                self.select_handle()

        elif 'event' in globals().keys():
            event.dispatch()

    def libevent_read_callback(self, ev, fd, evtype, pipe):
        "Functions as a callback for libevent pased "
        self._socket_handler(self.sockets[fd.fileno()], 'libevent')

    def select_handle(self):
        "Handles select-based socket handling"
        try:
            for fileno, ev in self.sockpoll.poll(1000):
                self._socket_handler(self.sockets[fileno], 'select')
        except Exception, e:
            self.DEBUG('server', str(e), 'err')

    def _socket_handler(self, sock, mode):
        "Accepts incoming sockets and ultimately handles the core-routing of packets"
        if isinstance(sock, Session):
            sess = sock
            try:
                data = sess.receive()
            except IOError:  # client closed the connection
                sess.terminate_stream()
                data = ''
            if data:
                try:
                    sess.Parse(data)
                except simplexml.xml.parsers.expat.ExpatError:
                    sess.terminate_stream(STREAM_XML_NOT_WELL_FORMED)
            if time.time() - sess.last_seen >= 60.0:
                sess.terminate_stream()

        elif isinstance(sock, RPC_Client):
            sess = sock
            try:
                data = sess.receive()
            except IOError:  # client closed the connection
                sess.terminate()
                data = ''
            if data:
                sess.RPC_handler(data)

        elif isinstance(sock, socket.socket):
            conn, addr = sock.accept()
            host, port = sock.getsockname()
            if port in [globals()['PORT_5222'], globals()['PORT_5223']]:
                sess = Session(conn, self, NS_CLIENT)
#                    self.DEBUG('server','%s:%s is a client!'%(host,port),'info')

            elif port == globals()['PORT_8000']:
                sess = RPC_Client(self, conn, addr, host, port)
                self.registersession(sess)
                try:
                    data = sess.receive()
                except IOError:  # client closed the connection
                    sess.terminate()
                    data = ''
                if data:
                    sess.send("")  # let it know that we're ready to accept
                return True

            else:
#                    self.DEBUG('server','%s:%s is a server!'%(host,port),'info')
                sess = Session(conn, self, NS_SERVER)
            self.registersession(sess)
            if port == globals()['PORT_5223']:
                self.TLS.startservertls(sess)

        else:
            raise "Unknown instance type: %s" % sock

    def _lib_out(self):
        if isinstance(self._socker, Socker_client):
            self._socker.destroy()
        event.abort()
        self.DEBUG('server', self._l(SERVER_SHUTDOWN_MSG), 'info')
        self.shutdown(STREAM_SYSTEM_SHUTDOWN)

    def shutdown(self, reason):
        global GLOBAL_TERMINATE
        GLOBAL_TERMINATE = True
        socklist = self.sockets.keys()
        for fileno in socklist:
            s = self.sockets[fileno]
            if isinstance(s, socket.socket):
                try:
                    self.unregistersession(s)
                    s.shutdown(2)
                    s.close()
                except:
                    pass
            elif isinstance(s, Session):
                s.terminate_stream(reason)
        try:
            self.multisession_manager.destroy()
        except:
            self.DEBUG('server', "Could not destroy multisession manager", "warn")

    def S2S(self, ourname, domain, slave_session=None, port=None, route_everything=False):
        ### THIS IS FUCKING DANGEROUS!!!!!
        #s = self.getsession(domain)
        #if s: return s
        ### THIS IS FUCKING DANGEROUS!!!!!
        s = Session(socket.socket(socket.AF_INET, socket.SOCK_STREAM), self, NS_SERVER, domain)
        s.slave_session = slave_session
        if route_everything is True:
            self.sisters[domain + '_' + str(port)] = s
        s.ourname = ourname
        self.activatesession(s)
        self._connect_session(s, domain, port)
        return s

    def _connect_session(self, session, domain, port):
        print session.DEBUG(self._l(SERVER_S2S_ATTEMPT_CONNECTION) % {'server': domain}, 'info')
        if port is None:
            port = 5269
        else:
            print "s2s port set", port
        try:
            session._sock.connect((domain, port))
        except socket.error, err:
            print session.DEBUG(self._l(SERVER_S2S_THREAD_ERROR) % err, 'error')
            self.num_servers -= 1
            session.set_session_state(SESSION_BOUND)
            session.set_socket_state(SOCKET_DEAD)
            if err[0] == errno.ETIMEDOUT:
                failreason = ERR_REMOTE_SERVER_TIMEOUT
            elif err[0] == socket.EAI_NONAME:
                failreason = ERR_REMOTE_SERVER_NOT_FOUND
            else:
                failreason = ERR_UNDEFINED_CONDITION
            session.push_queue(failreason)
            session.terminate_stream(STREAM_REMOTE_CONNECTION_FAILED, unregister=0)
            return
        session.set_socket_state(SOCKET_ALIVE)
        session.push_queue()
        self.registersession(session)

    def Privacy(self, peer, stanza):
        self.DEBUG('server', self._l(SERVER_PVCY_ACTIVATED), 'warn')
        template_input = {'jid_from': unicode(peer.peer).encode('utf-8'), 'jid_to': unicode(stanza['to']).encode('utf-8')}
        split_jid = self.tool_split_jid(peer.peer)
        if split_jid is None:
            return
        self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_CHECK) % template_input, 'info')

        #Stanza Stuff
        to = stanza['to']
        if not to:
            return  # Not for us.
        to_node = to.getNode()
        if not to_node:
            return  # Yep, not for us.
        to_domain = to.getDomain()
        if to_domain in self.components.keys():
            component = True
        else:
            component = False
        if to_domain in self.servernames and to_domain != to:
            bareto = to_node + '@' + to_domain
            name = stanza.getName()
            typ = stanza.getType()
            to_roster = self.DB.get(to_domain, to_node, 'roster')

            if self.DB.get(to_domain, to_node, 'anon_allow') == 'yes':
                anon_allow = True
            else:
                anon_allow = False

            to_working_roster_item = None
            #Session stuff
            roster = peer.getRoster()
            node = split_jid[0]
            domain = split_jid[1]
            resource = split_jid[2]

            if name == 'presence':
                if stanza.getType() in ["subscribe", "subscribed", "unsubscribe", "unsubscribed"]:
                    self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_CLEAR_ONEWAY_PRESENCE) % template_input, 'info')
                    return

            if node + '@' + domain == bareto:
                self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_CLEAR_UNLIMITED) % template_input, 'info')
                return

            if to_roster is not None:
                for x, y in to_roster.iteritems():
                    if x == node + '@' + domain:
                        to_working_roster_item = y
                        break

            if to_working_roster_item is None and anon_allow is False:
                peer.send(Error(stanza, ERR_NOT_AUTHORIZED))
                self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_NOTCLEAR_DOUBLEFALSE) % template_input, 'error')
                raise NodeProcessed  # Take the blue pill
            elif to_working_roster_item is None and anon_allow is True:
                to_working_roster_item = {}
                to_working_roster_item['subscription'] = 'none'

            for z, a in roster.iteritems():
                if z == bareto:
                    if a['subscription'] == 'both' and 'subscription' in to_working_roster_item.keys() and to_working_roster_item['subscription'] == 'both':
                        self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_CLEAR_BIDIRECTIONAL) % template_input, 'info')
                        return
                    elif to_working_roster_item['subscription'] == 'from':
                        self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_CLEAR_ONEWAY) % template_input, 'info')
                        return
                    elif to_working_roster_item['subscription'] == 'to':
                        peer.send(Error(stanza, ERR_NOT_AUTHORIZED))
                        self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_NOTCLEAR_MODETO) % template_input, 'error')
                        raise NodeProcessed  # Take the blue pill

            if anon_allow is True or str(to) in self.servernames:
                return
            else:
                peer.send(Error(stanza, ERR_NOT_AUTHORIZED))
                self.DEBUG('server', self._l(SERVER_PVCY_ACCESS_NOTCLEAR_FALSEANON) % template_input, 'error')
                raise NodeProcessed  # Take the blue pill
        return

    def Dialback(self, session):
        session.terminate_stream(STREAM_UNSUPPORTED_VERSION)

    def pick_rand(self):
        "return random int from 7000 to 8999 -- used for random port"
        import random
        return random.randrange(7000, 8999)


def start_new_thread_fake(func, args):
    func(*args)


def testrun():
    thread.start_new_thread = start_new_thread_fake
    import modules
    modules.stream.thread.start_new_thread = start_new_thread_fake
    return Server()


class get_input(threading.Thread):
    def __init__(self, owner):
        self._owner = owner
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.setName("get_input " + str(owner))

    def run(self):
        global GLOBAL_TERMINATE
        while GLOBAL_TERMINATE is False:
            the_input = raw_input("")
            if the_input == 'restart':
                self._owner.DEBUG('server', 'Stand-by; Restarting entire server!', 'info')
                self._owner.shutdown(STREAM_SYSTEM_SHUTDOWN)
                self._owner.DEBUG('server', 'Server has been shutdown, restarting NOW!', 'info')
                GLOBAL_TERMINATE = False
                self._owner.__init__(['always'], True)

            elif the_input == 'sys_debug':
                print sys.exc_info()
                print traceback.print_exc()
            elif the_input.split(' ')[0] == 'restart':

                import modules
                reload(modules)
                for addon in modules.addons:
                    if addon().__class__.__name__.lower() == the_input.split(' ')[1].lower():
                        if issubclass(addon, PlugIn):
                            if addon().__class__.__name__ in self._owner.__dict__.keys():
                            #self.DEBUG('server','Plugging-out?','info')

                                self._owner.DEBUG('server', 'Plugging %s out of %s.' % (addon(), s), 'stop')
                                if addon().DBG_LINE in self._owner.debug_flags:
                                    self._owner.debug_flags.remove(addon().DBG_LINE)
                                if getattr(addon(), '_exported_methods', None) is not None:
                                    for method in addon()._exported_methods:
                                        del self._owner.__dict__[method.__name__]
                                if getattr(addon(), '_old_owners_methods', None) is not None:
                                    for method in addon()._old_owners_methods:
                                        self._owner.__dict__[method.__name__] = method
                                del self._owner.__dict__[addon().__class__.__name__]
                                if 'plugout' in addon().__class__.__dict__.keys():
                                    addon().plugout()
                                self._owner.unfeature(addon.NS)

                                addon().PlugIn(s)
                            else:
                                addon().PlugIn(s)
                        else:
                            self._owner.__dict__[addon.__class__.__name__] = addon()
                        self._owner.feature(addon.NS)

            elif the_input.split(' ')[0] == 'start':

                import modules
                reload(modules)
                for addon in modules.addons:
                    if addon().__class__.__name__.lower() == the_input.split(' ')[1].lower():
                        if issubclass(addon, PlugIn):
                            addon().PlugIn(s)
                        else:
                            self._owner.__dict__[addon.__class__.__name__] = addon()
                        self._owner.feature(addon.NS)

            elif the_input.split(' ')[0] == 'stop':

                import modules
                reload(modules)
                for addon in modules.addons:
                    if addon().__class__.__name__.lower() == the_input.split(' ')[1].lower():
                        if issubclass(addon, PlugIn):
                            if addon().__class__.__name__ in self._owner.__dict__.keys():
                                #self.DEBUG('server','Plugging-out?','info')

                                self._owner.DEBUG('server', 'Plugging %s out of %s.' % (addon(), s), 'stop')
                                if addon().DBG_LINE in self._owner.debug_flags:
                                    self._owner.debug_flags.remove(addon().DBG_LINE)
                                if getattr(addon(), '_exported_methods', None) is not None:
                                    for method in addon()._exported_methods:
                                        del self._owner.__dict__[method.__name__]
                                if getattr(addon(), '_old_owners_methods', None) is not None:
                                    for method in addon()._old_owners_methods:
                                        self._owner.__dict__[method.__name__] = method
                                del self._owner.__dict__[addon().__class__.__name__]
                                if 'plugout' in addon().__class__.__dict__.keys():
                                    addon().plugout()
                            else:
                                self._owner.DEBUG('server', 'Error: Could not un-plug %s' % addon().__class__.__name__, 'error')
                        else:
                            if getattr(addon(), '_exported_methods', None) is not None:
                                for method in addon()._exported_methods:
                                    del self._owner.__dict__[method.__name__]
                            if getattr(addon(), '_old_owners_methods', None) is not None:
                                for method in addon()._old_owners_methods:
                                    self._owner.__dict__[method.__name__] = method
                            del self._owner.__dict__[addon().__class__.__name__]
                            if 'plugout' in addon().__class__.__dict__.keys():
                                addon().plugout()
                        if addon().__class__.__name__ in self._owner.__dict__.keys():
                            self._owner.DEBUG('server', 'Error: Could not un-plug %s' % addon().__class__.__name__, 'error')
                        self._owner.unfeature(addon.NS)

            elif the_input == 'quit':
                GLOBAL_TERMINATE = True
                event.abort()
                break
            time.sleep(.01)

if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] [-l lang_code] [--hostname=HOST] [-s host[:ip]]", version="%%prog %s" % __version__)
    parser.add_option("-p", "--psyco",
                      action="store_true", dest="enable_psyco",
                      help="Enable PsyCo")

    parser.add_option("--nofallback",
                      action="store_true", dest="disable_fallback",
                      help="Disables fallback support (Upon a major error, the server will not try to restart itself.)")

    parser.add_option('-l', "--lang", metavar="lang_code", default='en', dest="language",
                      help="Used to explicitly set the daemon's default language.")

    parser.add_option("-d", "--debug",
                      action="store_true", dest="enable_debug",
                      help="Enables debug messaging to console")

    parser.add_option("--hostname", metavar="HOST", dest="hostname",
                      help="Used to explicitly set the hostname or IP of this daemon.")

    parser.add_option("--password", metavar="PASSWD", dest="password",
                      help="Sets the default password for this node/daemon."
                      "(The password is generated, otherwise.)")

    parser.add_option('-s', "--socker", metavar="host[:ip]", dest="socker_info",
                      help="Enables, and connects to the host:ip "
                      "of a socker(tm) socket multiplexor. [EXPERIMENTAL]")

    parser.add_option('-r', "--router", metavar="host[:ip]", dest="router_info",
                      help="Enables, and connects to an outside router @ host:ip [EXPERIMENTAL]")

    parser.add_option("-i",
                      action="store_true", dest="enable_interactive",
                      help="Enables Interactive mode, allowing a console user to interactively edit the server in realtime.")

    (cmd_options, cmd_args) = parser.parse_args()

    #Create the xmppd server
    s = Server()
    #s=Server(cmd_options=eval(str(cmd_options)))

    inpt_service = get_input(s)
    #inpt_service.setDaemon(True)

    if cmd_options.enable_interactive is True:
        inpt_service.start()
    print "Starting server . . ."

    while GLOBAL_TERMINATE is False:
        try:
            s.run()
            #s.DEBUG('server',s._l(SERVER_SHUTDOWN_MSG),'info')
            #s.shutdown(STREAM_SYSTEM_SHUTDOWN)
        except KeyboardInterrupt:
            s.DEBUG('server', s._l(SERVER_SHUTDOWN_MSG), 'info')
            s.shutdown(STREAM_SYSTEM_SHUTDOWN)
        except:
            if 'event' in globals().keys():
                event.abort()
            s.DEBUG("server", 'Check your traceback file, please!', 'warn')
            tbfd = file('xmppd.traceback', 'a')
            tbfd.write(str('\nTRACEBACK REPORT FOR XMPPD for %s\n' + '=' * 55 + '\n') % time.strftime('%c'))
            #write traceback
            traceback.print_exc(None, tbfd)
            tbfd.close()
            if cmd_options.disable_fallback is True:
                GLOBAL_TERMINATE = True
