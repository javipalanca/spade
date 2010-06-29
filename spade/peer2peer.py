import Behaviour
import xmpp
import SocketServer
import pickle
import random

class P2PBehaviour(Behaviour.Behaviour):
    class P2PRequestHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            self.server.requests.append(self.request)
            try:
                data = ""
                while True:
                    #Read message length
                    length = self.rfile.read(8)
                    if not length:
                        #EOF
                        break
                    data = self.rfile.read(int(length))
                    self.server.owner.DEBUG("P2P message received.","ok")
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
                            self.server._jabber_messageCB(None,m,raiseFlag=False)
                            self.server.owner.DEBUG("The p2p message is XML:"+str(m))
                    data = ""
            except Exception, e:
                self.server.owner.DEBUG("P2P Socket Closed to "+ str(self.client_address),"err")  #,":",str(e),":",str(length),str(data)


    def _process(self):
        try:
            self.server.handle_request()
        except Exception,e:
            self.myAgent.DEBUG("P2P server failed: "+str(e),"err")

    def onEnd(self):
        self.myAgent.p2p_ready = False
        self.server.stop()
        if not self.finished:
            try:
                for sock in self.server.requests:
                    try:
                        sock.close()
                        del sock
                    except:
                        pass
                self.server.socket.close()
                del self.server
            except:
                pass
            iq = xmpp.Iq("result",queryNS=xmpp.NS_DISCO_INFO)
            for to in self.myAgent.p2p_routes.keys():
                iq.setTo(to)
                self.myAgent.send(iq)
            self.finished = True

    def onStart(self):
        open = False
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        while open == False:
            try:
                self.server = SocketServer.ThreadingTCPServer(('', self.myAgent.P2PPORT), self.P2PRequestHandler)
                self.server.owner = self.myAgent
                open = True
            except:
                self.myAgent.P2PPORT = random.randint(1025,65535)
                self.myAgent.DEBUG("Changing P2P port to " + str(self.myAgent.P2PPORT))

        self.server._jabber_messageCB = self.myAgent._jabber_messageCB
        self.server.postMessage = self.myAgent.postMessage
        self.server.requests = []
        self.myAgent.DEBUG(self.getName()+": P2P Behaviour Started at port "+ str(self.myAgent.P2PPORT))
        self.finished = False  #Flag to mark (later) if we have passed through onEnd
        self.myAgent.p2p_ready = True
        
class StreamInitiationBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "set":
                if self.msg.getTag("si").getAttr("profile") == "http://jabber.org/protocol/si/profile/spade-p2p-messaging":
                    #P2P Messaging Offer
                    self.myAgent.DEBUG("P2P-Messaging offer from " + str(self.msg.getFrom()))
                    if self.myAgent.p2p_ready:
                        #Take note of sender's p2p address if any
                        if self.msg.getTag("si").getTag("p2p"):
                            remote_address = str(self.msg.getTag("si").getTag("p2p").getData())
                            d = {"url":remote_address, "p2p":True}
                            self.myAgent.p2p_lock.acquire()
                            if self.myAgent.p2p_routes.has_key(str(self.msg.getFrom().getStripped())):
                                self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())].update(d)
                                if self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())].has_key("socket"):
                                    self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())]["socket"].close()
                            else:
                                self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())] = d
                            self.myAgent.p2p_lock.release()

                        #Accept offer
                        reply = self.msg.buildReply("result")
                        si = reply.addChild("si")
                        si.setNamespace("http://jabber.org/protocol/si")
                        p2p = si.addChild("p2p")
                        p2p.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
                        value = p2p.addChild("value")
                        value.setData(self.myAgent.getP2PUrl())
                        self.myAgent.DEBUG("P2P: Accept offer from "+str(self.msg.getFrom())+"."+str(reply) )
                    else:
                        #Refuse offer
                        reply = self.msg.buildReply("error")
                        err = reply.addChild("error", attrs={"code":"403","type":"cancel"})
                        err.addChild("forbidden")
                        err.setNamespace("urn:ietf:params:xml:ns:xmpp-stanzas")
                        self.myAgent.DEBUG("P2P: Refuse offer from "+str(self.msg.getFrom())+"."+str(reply))

                    self.myAgent.send(reply)


class DiscoBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "get":
                #Inform of services
                reply = self.msg.buildReply("result")
                if self.myAgent.p2p_ready:
                    reply.getTag("query").addChild("feature", {"var":"http://jabber.org/protocol/si"})
                    reply.getTag("query").addChild("feature", {"var":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
                self.myAgent.send(reply)
                self.myAgent.DEBUG(self.myAgent.getName()+": Sent Disco reply to "+ str(reply.getTo()))
            elif self.msg.getType() == "result":
                services = []
                for child in self.msg.getQueryChildren():
                    services.append(str(child.getAttr("var")))
                if "http://jabber.org/protocol/si/profile/spade-p2p-messaging" not in services:
                    frm = str(self.msg.getFrom().getStripped())
                    if str(frm) in self.myAgent.p2p_routes.keys():
                        #This agent does no longer support p2p
                        self.myAgent.p2p_lock.acquire()
                        try:
                            self.myAgent.DEBUG("Deleting "+str(frm)+" from P2P routes: "+ str(self.myAgent.p2p_routes),"warn")
                            del self.myAgent.p2p_routes[frm]
                        except:
                            pass
                        self.myAgent.p2p_lock.release()
        else:
            self.myAgent.DEBUG("DiscoBehaviour returned with no message", "warn")
                        
class SendStreamInitiationBehav(Behaviour.OneShotBehaviour):
    
    def __init__(self,to):
        Behaviour.OneShotBehaviour.__init__(self)

        self.to = to
        self.id = 'offer'+str(random.randint(1,10000))
        self.temp_iq = xmpp.Iq(attrs={'id':self.id})
        
    
    def _process(self):
        self.result = False
        #Offer Stream Initiation
        self.myAgent.DEBUG( "Offer StreamInitiation to" + str(self.to))
        iq = xmpp.Iq(attrs={'id':self.id})
        iq.setTo(self.to)
        iq.setType("set")
        si = xmpp.Node("si", {"profile":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
        si.setNamespace("http://jabber.org/protocol/si")
        if self.myAgent.p2p_ready:
            p2pnode = xmpp.Node("p2p")
            p2pnode.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
            p2pnode.setData(self.myAgent.getP2PUrl())
            si.addChild(node=p2pnode)
        iq.addChild(node=si)
        self.myAgent.send(iq)

        msg = self._receive(True, 4)
        if msg:
            self.result = False
            if msg.getType() =="result":
                self.myAgent.DEBUG("StreamRequest Agreed","ok")
                try:
                    remote_address = str(msg.getTag("si").getTag("p2p").getTag("value").getData())
                    d = {"url":remote_address, "p2p":True}
                    if self.myAgent.p2p_routes.has_key(str(msg.getFrom().getStripped())):
                        self.myAgent.p2p_routes[str(msg.getFrom().getStripped())].update(d)
                        self.result = True
                    else:
                        self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = d
                except Exception, e:
                    self.myAgent.DEBUG("Malformed StreamRequest Answer: "+ str(e),"err")
                    self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = {}
            elif msg.getType() == "error":
                self.myAgent.DEBUG("StreamRequest REFUSED","warn")
                self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = {'p2p':False}
        else:
            #Not message, treat like a refuse
            self.myAgent.DEBUG("StreamRequest REFUSED","warn")
            self.myAgent.p2p_routes[str(iq.getTo().getStripped())] = {'p2p':False}
            

class RequestDiscoInfoBehav(Behaviour.OneShotBehaviour):

    def __init__(self,to):
        Behaviour.OneShotBehaviour.__init__(self)
        
        self.to = to
        self.id = 'nsdi'+str(random.randint(1,10000))
        self.temp_iq = xmpp.Iq(queryNS=xmpp.NS_DISCO_INFO, attrs={'id':self.id})
        self.temp_iq.setType("result")
        

    def _process(self):
        self.result = []
        iq = xmpp.Iq(queryNS=xmpp.NS_DISCO_INFO, attrs={'id':self.id})
        iq.setTo(self.to)
        iq.setType("get")
        self.myAgent.DEBUG("Send IQ message: "+str(iq))
        
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

