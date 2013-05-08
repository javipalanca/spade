# -*- coding: utf-8 -*-
import Behaviour
import xmpp
import SocketServer
import pickle
import random
import thread
import time
import threading
import socket
import time
import itertools
from xmpp import Iq
from xmpp.protocol import NS_DISCO_INFO, NS_SI

class P2P(object):

    def __init__(self, agent, p2p=False):  # , msgrecv):
        self._client = agent.getAID().getName()
        #self.msgrecv = msgrecv
        self.myAgent = agent
        self._server = agent.server

        # Add Disco Behaviour
        agent.addBehaviour(DiscoBehaviour(), Behaviour.MessageTemplate(Iq(queryNS=NS_DISCO_INFO)))

        # Add Stream Initiation Behaviour
        iqsi = Iq()
        si = iqsi.addChild("si")
        si.setNamespace(NS_SI) #"http://jabber.org/protocol/si")
        agent.addBehaviour(StreamInitiationBehaviour(), Behaviour.MessageTemplate(iqsi))

        # Add P2P Behaviour
        self.p2p_ready = False  # Actually ready for P2P communication
        self.p2p = p2p
        self.p2p_routes = {}
        self.p2p_lock = thread.allocate_lock()
        self.p2p_send_lock = thread.allocate_lock()
        self._p2p_failures = 0  # Counter for failed attempts to send p2p messages
        if p2p:
            agent.registerLogComponent("p2p")
            self.P2PPORT = random.randint(70000, 80000)  # Random P2P port number
            p2pb = P2PBehaviour()
            agent.addBehaviour(p2pb)

    def register(self):
        NS_SPADE_P2P = 'http://jabber.org/protocol/si/profile/spade-p2p-messaging'
        for typ, ns in itertools.product(['set','get','result','error'],[NS_DISCO_INFO, NS_SI, NS_SPADE_P2P]):
            self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB, typ, ns)

    def isReady(self):
        return self.p2p_ready

    def getRoutes(self):
        return self.p2p_routes

    def getPort(self):
        return self.P2PPORT

    def acquire(self):
        self.p2p_send_lock.acquire()

    def release(self):
        self.p2p_send_lock.release()

    def send_p2p(self, jabber_msg=None, to="", method="p2ppy", ACLmsg=None):
        #Deprecated, please use 'send'
        return self.send(self, jabber_msg=jabber_msg, to=to, method=method, ACLmsg=ACLmsg)

    def send(self, jabber_msg=None, to="", method="p2ppy", ACLmsg=None):

        #If this agent supports P2P, wait for P2PBehaviour to properly start
        if self.p2p:
            counter = 50
            while not self.isReady() and counter > 0:
                time.sleep(0.1)
                counter -= 1
            if not self.isReady():
                self.myAgent.DEBUG("This agent could not activate p2p messages behaviour", "err")
                return False
        else:
            # send_p2p should not be called in a P2P-disabled agent !
            self.myAgent.DEBUG("This agent does not support sending p2p messages", "warn")
            return False

        #Get the address
        if not to:
            if not jabber_msg:
                return False
            else:
                to = str(jabber_msg.getTo())
        if jabber_msg:
            self.myAgent.DEBUG("Trying to send Jabber msg through P2P")
        elif ACLmsg:
            self.myAgent.DEBUG("Trying to send ACL msg through P2P")

        try:
            #Try to get the contact's url
            url = self.p2p_routes[to]["url"]
        except:
            #The contact is not in our routes
            self.myAgent.DEBUG("P2P: The contact " + str(to) + " is not in our routes. Starting negotiation", "warn")
            self.myAgent.initiateStream(to)
            if to in self.p2p_routes.keys() and 'p2p' in self.p2p_routes[to].keys():
                #If this p2p connection is marked as faulty,
                #check if enough time has passed to try again a possible p2p connection
                if not self.p2p_routes[to]['p2p']:
                    try:
                        t1 = time.time()
                        t = t1 - self.p2p_routes[to]['failed_time']
                        #If more than 10 seconds have passed . . .
                        if t > 10.0:
                            self.p2p_lock.acquire()
                            self.p2p_routes[to]['p2p'] = True
                            self.p2p_routes[to]['failed_time'] = 0.0
                            self.p2p_lock.release()
                    except:
                        #The p2p connection is really faulty
                        self.myAgent.DEBUG("P2P: The p2p connection is really faulty", "warn")
                        return False
                url = self.p2p_routes[to]["url"]
            else:
                #There is no p2p for this contact
                self.myAgent.DEBUG("P2P: There is no p2p support for this contact", "warn")
                return False

        #Check if there is already an open socket
        s = None
        if "socket" in self.p2p_routes[to].keys():
            s = self.p2p_routes[to]["socket"]
        if not s:
            #Parse url
            scheme, address = url.split("://", 1)
            if scheme == "spade":
                #Check for address and port number
                l = address.split(":", 1)
                if len(l) > 1:
                    address = l[0]
                    port = int(l[1])

            #Create a socket connection to the destination url
            connected = False
            tries = 2
            while not connected and tries > 0:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((address, port))
                    self.p2p_lock.acquire()
                    self.p2p_routes[to]["socket"] = s
                    self.p2p_lock.release()
                    connected = True
                except:
                    tries -= 1
                    _exception = sys.exc_info()
                    if _exception[0]:
                        self.myAgent.DEBUG("Error opening p2p socket " + '\n' + ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip(), "err")

            if not connected:
                self.myAgent.DEBUG("Socket creation failed", "warn")
                return False

        #Send length + message
        sent = False
        tries = 2
        while not sent and tries > 0:
            try:
                if method in ["p2p", "auto"]:
                    jabber_msg.attrs.update({"method": "p2p"})
                    length = "%08d" % (len(str(jabber_msg)))
                    #Send message through socket
                    s.send(length + str(jabber_msg))
                    self.myAgent.DEBUG("P2P message sent through p2p", "ok")
                elif method in ["p2ppy"]:
                    ACLmsg._attrs.update({"method": "p2ppy"})
                    ser = pickle.dumps(ACLmsg)
                    length = "%08d" % (len(str(ser)))
                    s.send(length + ser)
                    self.myAgent.DEBUG("P2P message sent through p2ppy", "ok")
                sent = True

            except Exception, e:
                self.myAgent.DEBUG("Socket: send failed, threw an exception: " + str(e), "err")
                self._p2p_failures += 1
                # Dispose of old socket
                self.p2p_lock.acquire()
                s.close()
                try:
                    del s
                    del self.p2p_routes[to]["socket"]
                except:
                    pass
                self.p2p_lock.release()
                #Get address and port AGAIN
                scheme, address = url.split("://", 1)
                if scheme == "spade":
                    #Check for address and port number
                    l = address.split(":", 1)
                    if len(l) > 1:
                        address = l[0]
                        port = int(l[1])
                    #Try again
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((address, port))
                    self.p2p_lock.acquire()
                    self.p2p_routes[to]["socket"] = s
                    self.p2p_lock.release()
                else:
                    return False
                tries -= 1
        if not sent:
            self.myAgent.DEBUG("Socket send failed", "warn")
            self.p2p_lock.acquire()
            self.p2p_routes[to]["p2p"] = False
            self.p2p_routes[to]["failed_time"] = time.time()
            self.p2p_lock.release()
            return False
        else:
            return True

class P2PBehaviour(Behaviour.OneShotBehaviour):
    class P2PRequestHandler(SocketServer.StreamRequestHandler):
        timeout = 5

        def handle(self):
            self.server.requests.append(self.request)
            data = ""
            close = False
            while not close and not self.server.closing:  # True:
                try:
                    #Read message length
                    length = self.rfile.read(8)
                    if not length:
                        #EOF
                        break
                    data = self.rfile.read(int(length))
                    self.server.owner.DEBUG("P2P message received.", "ok")
                    if data:
                        try:
                            #Try with a serialized message
                            ACLmsg = pickle.loads(data)
                            self.server.postMessage(ACLmsg)
                            self.server.owner.DEBUG("The p2p message is serialized.")
                        except:
                            #Try with a jabber message
                            n = xmpp.simplexml.XML2Node(str(data))
                            m = xmpp.Message(node=n)
                            self.server._jabber_messageCB(None, m, raiseFlag=False)
                            self.server.owner.DEBUG("The p2p message is XML:" + str(m))
                    data = ""
                except socket.timeout:
                    close = True
                    # handle timeout
                except Exception, e:
                    self.server.owner.DEBUG("P2P Socket Closed to " + str(self.client_address), "err")
                    close = True

    def kill(self):
        """
        stops the behavior
        """
        try:
            self._forceKill.set()
            self.myAgent.DEBUG("Stoping Behavior " + str(self), "info")
        except:
            #Behavior is already dead
            self.myAgent.DEBUG("Behavior " + str(self) + " is already dead", "warn")

        self.server.closing = True
        if self.server is not None:
            thread.start_new_thread(self.server.shutdown, ())

    def _process(self):
        try:
            self.server.serve_forever(poll_interval=0.5)  # handle_request()
        except Exception, e:
            self.myAgent.DEBUG("P2P server failed: " + str(e), "err")
            self.kill()

    def onEnd(self):
        self.myAgent._P2P.p2p_ready = False
        if self.server is not None:
            self.server.server_close()  # shutdown()
        if not self.finished:
            try:
                for sock in self.server.requests:
                    try:
                        sock.close()
                        del sock
                    except:
                        pass
                self.server.socket.close()
                #del self.server
            except:
                pass
            iq = Iq("result", queryNS=NS_DISCO_INFO)
            for to in self.myAgent._P2P.p2p_routes.keys():
                iq.setTo(to)
                self.myAgent.send(iq)
            self.finished = True

    def onStart(self):
        self.server = None
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        #SocketServer.TCPServer.timeout = 1
        count = 5
        while self.server is None and count > 0:
            try:
                self.server = SocketServer.ThreadingTCPServer(('', self.myAgent._P2P.P2PPORT), self.P2PRequestHandler)
                self.server.owner = self.myAgent
                self.server.timeout = 0.5
            except:
                self.myAgent._P2P.P2PPORT = random.randint(1025, 65535)
                self.myAgent.DEBUG("Changing P2P port to " + str(self.myAgent._P2P.P2PPORT))
            count -= 1

        if self.server is not None:
            self.server.closing = False
            self.server._jabber_messageCB = self.myAgent._jabber_messageCB
            self.server.postMessage = self.myAgent.postMessage
            self.server.requests = []
            self.myAgent.DEBUG(self.myAgent.getName() + ": P2P Behaviour Started at port " + str(self.myAgent._P2P.P2PPORT))
            self.finished = False  # Flag to mark (later) if we have passed through onEnd
            self.myAgent._P2P.p2p_ready = True
        else:
            self.myAgent.DEBUG("Could not start P2P Behaviour", "err")
            self.kill()


class StreamInitiationBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.msg = self._receive(False)
        if self.msg is not None:
            if self.msg.getType() == "set":
                if self.msg.getTag("si").getAttr("profile") == "http://jabber.org/protocol/si/profile/spade-p2p-messaging":
                    #P2P Messaging Offer
                    self.myAgent.DEBUG("P2P-Messaging offer from " + str(self.msg.getFrom()))
                    if self.myAgent._P2P.isReady():
                        #Take note of sender's p2p address if any
                        if self.msg.getTag("si").getTag("p2p"):
                            remote_address = str(self.msg.getTag("si").getTag("p2p").getData())
                            d = {"url": remote_address, "p2p": True}
                            self.myAgent._P2P.acquire()
                            if str(self.msg.getFrom().getStripped()) in self.myAgent._P2P.getRoutes():
                                self.myAgent._P2P.p2p_routes[str(self.msg.getFrom().getStripped())].update(d)
                                if "socket" in self.myAgent._P2P.p2p_routes[str(self.msg.getFrom().getStripped())]:
                                    self.myAgent._P2P.p2p_routes[str(self.msg.getFrom().getStripped())]["socket"].close()
                            else:
                                self.myAgent._P2P.p2p_routes[str(self.msg.getFrom().getStripped())] = d
                            self.myAgent._P2P.release()

                        #Accept offer
                        reply = self.msg.buildReply("result")
                        si = reply.addChild("si")
                        si.setNamespace("http://jabber.org/protocol/si")
                        p2p = si.addChild("p2p")
                        p2p.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
                        value = p2p.addChild("value")
                        value.setData(self.myAgent.getP2PUrl())
                        self.myAgent.DEBUG("P2P: Accept offer from " + str(self.msg.getFrom()) + "." + str(reply))
                    else:
                        #Refuse offer
                        reply = self.msg.buildReply("error")
                        err = reply.addChild("error", attrs={"code": "403", "type": "cancel"})
                        err.addChild("forbidden")
                        err.setNamespace("urn:ietf:params:xml:ns:xmpp-stanzas")
                        self.myAgent.DEBUG("P2P: Refuse offer from " + str(self.msg.getFrom()) + "." + str(reply))

                    self.myAgent.send(reply)


class DiscoBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.msg = self._receive(False)
        if self.msg is not None:
            if self.msg.getType() == "get":
                #Inform of services
                reply = self.msg.buildReply("result")
                if self.myAgent._P2P.isReady():
                    reply.getTag("query").addChild("feature", {"var": "http://jabber.org/protocol/si"})
                    reply.getTag("query").addChild("feature", {"var": "http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
                self.myAgent.send(reply)
                self.myAgent.DEBUG(self.myAgent.getName() + ": Sent Disco reply to " + str(reply.getTo()))
            elif self.msg.getType() == "result":
                services = []
                for child in self.msg.getQueryChildren():
                    services.append(str(child.getAttr("var")))
                if "http://jabber.org/protocol/si/profile/spade-p2p-messaging" not in services:
                    frm = str(self.msg.getFrom().getStripped())
                    if str(frm) in self.myAgent._P2P.getRoutes().keys():
                        #This agent does no longer support p2p
                        self.myAgent._P2P.acquire()
                        try:
                            self.myAgent.DEBUG("Deleting " + str(frm) + " from P2P routes: " + str(self.myAgent._P2P.getRoutes()), "warn")
                            del self.myAgent._P2P.p2p_routes[frm]
                        except:
                            pass
                        self.myAgent._P2P.release()
        else:
            self.myAgent.DEBUG("DiscoBehaviour returned with no message", "warn")


class SendStreamInitiationBehav(Behaviour.OneShotBehaviour):

    def __init__(self, to):
        Behaviour.OneShotBehaviour.__init__(self)

        self.to = to
        self.id = 'offer' + str(random.randint(1, 10000))
        self.temp_iq = xmpp.Iq(attrs={'id': self.id})

    def _process(self):
        self.result = False
        #Offer Stream Initiation
        self.myAgent.DEBUG("Offer StreamInitiation to" + str(self.to))
        iq = xmpp.Iq(attrs={'id': self.id})
        iq.setTo(self.to)
        iq.setType("set")
        si = xmpp.Node("si", {"profile": "http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
        si.setNamespace("http://jabber.org/protocol/si")
        if self.myAgent._P2P.isReady():
            p2pnode = xmpp.Node("p2p")
            p2pnode.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
            p2pnode.setData(self.myAgent.getP2PUrl())
            si.addChild(node=p2pnode)
        iq.addChild(node=si)
        self.myAgent.send(iq)

        msg = self._receive(True)
        if msg:
            self.result = False
            if msg.getType() == "result":
                self.myAgent.DEBUG("StreamRequest Agreed", "ok")
                try:
                    remote_address = str(msg.getTag("si").getTag("p2p").getTag("value").getData())
                    d = {"url": remote_address, "p2p": True}
                    if str(msg.getFrom().getStripped()) in self.myAgent._P2P.getRoutes():
                        self.myAgent._P2P.p2p_routes[str(msg.getFrom().getStripped())].update(d)
                        self.result = True
                    else:
                        self.myAgent._P2P.p2p_routes[str(msg.getFrom().getStripped())] = d
                except Exception, e:
                    self.myAgent.DEBUG("Malformed StreamRequest Answer: " + str(e), "err")
                    self.myAgent.P2P.p2p_routes[str(msg.getFrom().getStripped())] = {}
            elif msg.getType() == "error":
                self.myAgent.DEBUG("StreamRequest REFUSED", "warn")
                self.myAgent._P2P.p2p_routes[str(msg.getFrom().getStripped())] = {'p2p': False}
        else:
            #Not message, treat like a refuse
            self.myAgent.DEBUG("No msg received. StreamRequest REFUSED", "warn")
            self.myAgent._P2P.p2p_routes[str(iq.getTo().getStripped())] = {'p2p': False}


class RequestDiscoInfoBehav(Behaviour.OneShotBehaviour):

    def __init__(self, to):
        Behaviour.OneShotBehaviour.__init__(self)

        self.to = to
        self.id = 'nsdi' + str(random.randint(1, 10000))
        self.temp_iq = xmpp.Iq(queryNS=NS_DISCO_INFO, attrs={'id': self.id})
        self.temp_iq.setType("result")

    def _process(self):
        self.result = []
        iq = xmpp.Iq(queryNS=NS_DISCO_INFO, attrs={'id': self.id})
        iq.setTo(self.to)
        iq.setType("get")
        self.myAgent.DEBUG("Send IQ message: " + str(iq))

        self.myAgent.send(iq)
        #msg = self._receive(True, 10)
        msg = self._receive(True)
        if msg:
            if msg.getType() == "result":
                for child in msg.getQueryChildren():
                    self.result.append(str(child.getAttr("var")))
                self.myAgent.DEBUG("Retrieved services: " + str(self.result))
            else:
                self.myAgent.DEBUG("Disco Info returned no results from " + str(self.to), "warn")
        else:
            self.myAgent.DEBUG("No Disco Info retrieved from " + str(self.to), "warn")
