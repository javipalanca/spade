# -*- coding: cp1252 -*-
import sys
import traceback
import xmpp
import threading
import thread
import Queue
import time
import MessageReceiver
import AID
import XMLCodec
import ACLParser
import Envelope
import ACLMessage
import BasicFipaDateTime
import Behaviour
import SL0Parser
import colors
import mutex
import types
import random
import string
import Organization
import Organization_new
import copy
import socket
import SocketServer
#from AMS import AmsAgentDescription

import DF

from xmpp import Iq, Presence,Protocol, NS_ROSTER, NS_DISCO_INFO

# Taken from xmpp debug
color_none         = chr(27) + "[0m"
color_black        = chr(27) + "[30m"
color_red          = chr(27) + "[31m"
color_green        = chr(27) + "[32m"
color_brown        = chr(27) + "[33m"
color_blue         = chr(27) + "[34m"
color_magenta      = chr(27) + "[35m"
color_cyan         = chr(27) + "[36m"
color_light_gray   = chr(27) + "[37m"
color_dark_gray    = chr(27) + "[30;1m"
color_bright_red   = chr(27) + "[31;1m"
color_bright_green = chr(27) + "[32;1m"
color_yellow       = chr(27) + "[33;1m"
color_bright_blue  = chr(27) + "[34;1m"
color_purple       = chr(27) + "[35;1m"
color_bright_cyan  = chr(27) + "[36;1m"
color_white        = chr(27) + "[37;1m"



class AbstractAgent(MessageReceiver.MessageReceiver):
    """
    Abstract Agent
    only for heritance
    Child classes: PlatformAgent, Agent
    """
    class P2PBehaviour(Behaviour.Behaviour):
        class P2PRequestHandler(SocketServer.StreamRequestHandler):
            def handle(self):
                try:
                    data = ""
                    while True:
                        # Read message length                        
                        length = self.rfile.read(8)
                        if length:
                            data = self.rfile.read(int(length))
                        #print "P2PBehaviour Received:", str(data)
                        if data:
                            n = xmpp.simplexml.XML2Node(str(data))
                            m = xmpp.Message(node=n)
                            self.server._jabber_messageCB(None,m,raiseFlag=False)
                        data = ""
                except Exception, e:
                    print "P2P Socket Closed to", str(self.client_address),":",str(e),":",str(data)
                
        def _process(self):
            self.server.handle_request()
        
        def onStart(self):
            open = False            
            while open == False:
                try:
                    self.server = SocketServer.ThreadingTCPServer(('', self.myAgent.P2PPORT), self.P2PRequestHandler)
                    open = True
                except:
                    self.myAgent.P2PPORT = random.randint(1025,65535)                
                
            self.server._jabber_messageCB = self.myAgent._jabber_messageCB            
            print self.getName(),": P2P Behaviour Started at port", str(self.myAgent.P2PPORT)

    
    class StreamInitiationBehaviour(Behaviour.EventBehaviour):
        def _process(self):
            self.msg = self._receive(False)
            if self.msg != None:
                #print "StreamInitiation Behaviour called"
                if self.msg.getType() == "set":
                    if self.msg.T.si.getAttr("profile") == "http://jabber.org/protocol/si/profile/spade-p2p-messaging":
                        # P2P Messaging Offer
                        print "P2P-Messaging offer from", str(self.msg.getFrom())
                        if self.myAgent.p2p:
                            # Take note of sender's p2p address if any
                            if self.msg.T.si.T.p2p:
                                remote_address = str(self.msg.T.si.T.p2p.getData())
                                d = {"url":remote_address, "p2p":True}
                                if self.myAgent.p2p_routes.has_key(str(self.msg.getFrom().getStripped())):
                                    self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())].update(d)
                                    if self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())].has_key("socket"):
                                        self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())]["socket"].close()
                                else:
                                    self.myAgent.p2p_routes[str(self.msg.getFrom().getStripped())] = d
                                #print "P2P ROUTES", str(self.myAgent.p2p_routes)
                            # Accept offer
                            reply = self.msg.buildReply("result")
                            si = reply.addChild("si")
                            si.setNamespace("http://jabber.org/protocol/si")
                            p2p = si.addChild("p2p")
                            p2p.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
                            value = p2p.addChild("value")
                            value.setData(self.myAgent.getP2PUrl())
                        else:
                            # Refuse offer
                            reply = self.msg.buildReply("error")
                            err = reply.addChild("error", attrs={"code":"403","type":"cancel"})
                            err.addChild("forbidden")
                            err.setNamespace("urn:ietf:params:xml:ns:xmpp-stanzas")
                        self.myAgent.jabber.send(reply)                        
                            
                
    class DiscoBehaviour(Behaviour.EventBehaviour):
        def _process(self):
            self.msg = self._receive(False)
            if self.msg != None:
                #print "DISCO Behaviour called"
                print "DISCO request from", str(self.msg.getFrom())
                # Inform of services
                reply = self.msg.buildReply("result")
                if self.myAgent.p2p:
                    reply.T.query.addChild("feature", {"var":"http://jabber.org/protocol/si"})
                    reply.T.query.addChild("feature", {"var":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
                self.myAgent.jabber.send(reply)
                #print "SENT DISCO REPLY", str(reply)

    

    def __init__(self, agentjid, serverplatform, p2p=True):
        """
        inits an agent with a JID (user@server) and a platform JID (acc.platformserver)
        """
        MessageReceiver.MessageReceiver.__init__(self)
        self._aid = AID.aid(name=agentjid, addresses=[ "xmpp://"+agentjid ])
        self._jabber = None
        self._serverplatform = serverplatform
        self._defaultbehaviour = None
        self._behaviourList = dict()
        self._alive = True
        self._alivemutex = mutex.mutex()
        self._forceKill = threading.Event()
        self._forceKill.clear()
        self.JID=agentjid
        self.setName(str(agentjid))

        self._friend_list = []  # Legacy
        self._muc_list= {}
        self._roster = {}
        self._socialnetwork = {}
        self._subscribeHandler   = lambda frm,typ,stat,show: False
        self._unsubscribeHandler = lambda frm,typ,stat,show: False
        self._jabber_mailbox = {}

        self._waitingForRoster = False  # Indicates that a request for the roster is in progress

        self._running = False
        
        # Add Disco Behaviour
        self.addBehaviour(Agent.DiscoBehaviour(), Behaviour.MessageTemplate(Iq("get",queryNS=NS_DISCO_INFO)))

        # Add Stream Initiation Behaviour
        iqsi = Iq()
        si = iqsi.addChild("si")
        si.setNamespace("http://jabber.org/protocol/si")
        self.addBehaviour(Agent.StreamInitiationBehaviour(), Behaviour.MessageTemplate(iqsi))

        # Add P2P Behaviour
        self.p2p = p2p
        self.p2p_routes = {}
        self.p2p_lock = thread.allocate_lock()        
        if p2p:
            self.P2PPORT = random.randint(1025,65535)  # Random P2P port number
            self.addBehaviour(Agent.P2PBehaviour())


    """
    def _receive(self, block = False, timeout = None, template = None):
        try:
            if not template: return MessageReceiver.MessageReceiver._receive(self, block, timeout)
            elif template and block and timeout:
                i = timeout
                while i > 0:
                    #timeout becomes the amount of 'tries' to receive a message
                    msg = self._receive(block=True, timeout=timeout, template=None)
                    if msg:
                        print "_RECEIVE HAS A MSG:", str(msg)
                        if template.match(msg):
                            print "_RECEIVE HAS MADE A MATCH"
                            return msg
                        else:
                            print "_RECEIVE NO MATCH"
                            self.postMessage(msg)
                    i -= 1
                return None
            else:
                while True:
                    msg = MessageReceiver.MessageReceiver._receive(self, True, 0.1)
                    if msg:
                        if template.match(msg): return msg
                        else: #self.postMessage(msg)
                            pass

        except:
            _exception = sys.exc_info()
            if _exception[0]:
                print '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
    """



    def _jabber_presenceCB(self, conn, mess):
	"""
	presence callback
	manages jabber stanzas of the 'presence' protocol
	"""

	#frm=None

	frm = mess.getFrom()
        #frm = AID.aid(str(mess.getFrom()), ['xmpp://'+str(mess.getFrom())])
        typ = str(mess.getType())
        status = str(mess.getStatus())
        show = str(mess.getShow())
        role = None
        affiliation = None

        children = mess.getTags(name='x',namespace='http://jabber.org/protocol/muc#user')
        for x in children:
            for item in x.getTags(name='item'):
                role = item.getAttr('role')
                affiliation = item.getAttr('affiliation')
#
#        #check for MUC presence
#		if ifrm.getDomain() == self.getMUC():
#			if self._muc_list.has_key(str(ifrm.getNode())):
#				self._muc_list[ifrm.getNode()].presenceCB(mess)
#
#		else:
#
#
#        if typ in ['subscribe']:
#		# Call the subscribe handler
#		if self._subscribeHandler(frm, typ, status, show):
#			reply = xmpp.Presence(mess.getFrom(), 'subscribed')
#			conn.send(reply)
#			return
#	elif typ in ['subscribed']:
#		# Subscription confirmation
#		print color_green + "Subscription to " + color_yellow + str(ifrm) + color_green  +" resolved" + color_none
#		return
#	elif typ in ['unsubscribe']:
#		# Call the unsubscribe handler
#		if self._unsubscribeHandler(frm, typ, status, show):
#			reply = xmpp.Presence(mess.getFrom(), 'unsubscribed')
#			conn.send(reply)
#		return
#	elif typ in ['unsubscribed']:
#		# Subscription denial
#		print color_red + "WARNING: Subscription to " + color_yellow + str(ifrm) + color_red  +" denied or cancelled" + color_none
#		return
#
#
#        else:
#			# Unsupported presence message
#			print color_yellow + "Unsupported presence message: " + str(mess.getType()) + color_none
#			return

        try:
	 	# Pass the FIPA-message to the behaviours
		#print "BEHAVIOURLIST: ", str(self._behaviourList)
		for b in self._behaviourList.keys():
		       #print "BEHAVIOUR LIST", str(b)
		       b.managePresence(frm, typ, status, show, role, affiliation)

		self._defaultbehaviour.managePresence(frm, typ, status, show, role, affiliation)
	except Exception, e:
	 	#There is not a default behaviour yet
		print "EXCEPTION: ", str(e)

	#self._roster = conn.getRoster()

    def _jabber_messageCB(self, conn, mess, raiseFlag=True):
        """
        message callback
        read the message envelope and post the message to the agent
        """        
        for child in mess.getChildren():
            if (child.getNamespace() == "jabber:x:fipa") or (child.getNamespace() == u"jabber:x:fipa"):
                # It is a jabber-fipa message
                ACLmsg = ACLMessage.ACLMessage()
                ACLmsg._attrs.update(mess.attrs)
                try:
                    # Clean
                    del ACLmsg._attrs["from"]
                except:
                    pass
                try:
                    # Clean
                    del ACLmsg._attrs["to"]
                except:
                    pass
                ACLmsg.setContent(mess.getBody())
                # Rebuild sender and receiver
                ACLmsg.setSender(AID.aid(str(mess.getFrom()), ["xmpp://"+str(mess.getFrom())]))
                ACLmsg.addReceiver(AID.aid(str(mess.getTo()), ["xmpp://"+str(mess.getTo())]))
                self.postMessage(ACLmsg)
                if raiseFlag: raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
                return True

        # Not a jabber-fipa message
        # Check wether is an offline action
        if not self._running:
            if mess.getName() == "iq":
                # Check if it's an offline disco info request
                if mess.getAttr("type") == "get":
                    q = mess.getTag("query")
                    if q and q.getNamespace() == NS_DISCO_INFO:
                        print "DISCO Behaviour called (offline)"
                        # Inform of services
                        reply = mess.buildReply("result")
                        if self.p2p:
                            reply.T.query.addChild("feature", {"var":"http://jabber.org/protocol/si"})
                            reply.T.query.addChild("feature", {"var":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
                        self.jabber.send(reply)
                        if raiseFlag: raise xmpp.NodeProcessed
                        return True
                # Check if it's an offline stream initiation request
                if mess.getAttr("type") == "set":
                    q = mess.getTag("si")
                    if q:                    
                        print "StreamInitiation Behaviour called (offline)"
                        if mess.getType() == "set":
                            if mess.T.si.getAttr("profile") == "http://jabber.org/protocol/si/profile/spade-p2p-messaging":
                                # P2P Messaging Offer
                                if self.p2p:
                                    # Take note of sender's p2p address if any
                                    if mess.T.si.T.p2p:
                                        remote_address = str(mess.T.si.T.p2p.getData())
                                        d = {"url":remote_address, "p2p":True}
                                        if self.p2p_routes.has_key(str(mess.getFrom().getStripped())):
                                            self.p2p_routes[str(mess.getFrom().getStripped())].update(d)
                                            if self.p2p_routes[str(mess.getFrom().getStripped())].has_key("socket"):
                                                self.p2p_routes[str(mess.getFrom().getStripped())]["socket"].close()
                                        else:
                                            self.p2p_routes[str(mess.getFrom().getStripped())] = d
                                        #print "P2P ROUTES", str(self.p2p_routes)
                                    # Accept offer
                                    reply = mess.buildReply("result")
                                    si = reply.addChild("si")
                                    si.setNamespace("http://jabber.org/protocol/si")
                                    p2p = si.addChild("p2p")
                                    p2p.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
                                    value = p2p.addChild("value")
                                    value.setData(self.getP2PUrl())
                                else:
                                    # Refuse offer
                                    reply = mess.buildReply("error")
                                    err = reply.addChild("error", attrs={"code":"403","type":"cancel"})
                                    err.addChild("forbidden")
                                    err.setNamespace("urn:ietf:params:xml:ns:xmpp-stanzas")
                                self.jabber.send(reply)
                                if raiseFlag: raise xmpp.NodeProcessed
                                return True
        
        self.postMessage(mess)
        if raiseFlag: raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
        return True


    def _other_messageCB(self, conn, mess):
	"""
	non jabber:x:fipa chat messages callback
	"""
        #if there is a mailbox with type and id registered. we store the message
        typ = mess.getType()
        id  = mess.getID()
        if self._jabber_mailbox.has_key(typ):
            if self._jabber_mailbox[typ].has_key(id):
                self._jabber_mailbox[typ][id].append(mess)

    def _jabber_iqCB(self, conn, mess):
        """
        IQ callback
        manages jabber stanzas of the 'iq' protocol
        """
	# We post every jabber iq
	self.postMessage(mess)
	print "Jabber Iq posted to agent ", str(self.getAID().getName())
        #self._other_messageCB(conn,mess)


    def register_mailbox(self,typ,id):
        """
        Registers a jabber mailbox with type and id
        """
        if self._jabber_mailbox.has_key(typ):
            if not self._jabber_mailbox[typ].has_key(id):
                self._jabber_mailbox[typ][id]=[]
        else:
            self._jabber_mailbox[typ]={}
            self._jabber_mailbox[typ][id]=[]

    def unregister_mailbox(self,typ,id):
        """
        Unregisters a jabber mailbox with type and id
        """
        if self._jabber_mailbox.has_key(typ):
            if self._jabber_mailbox[typ].has_key(id):
                del self._jabber_mailbox[typ][id]

    def jabber_receive(self, typ, id):
        """
        Returns a jabber message from the mailbox with type and id
        """
        if self._jabber_mailbox.has_key(typ) and self._jabber_mailbox[typ].has_key(id):
            if len(self._jabber_mailbox[typ][id])>0:
                return self._jabber_mailbox[typ][id].pop()
        return None

    def getAID(self):
	"""
	returns AID
	"""
        return self._aid

    def getName(self):
	return self._aid.getName()

    def getAMS(self):
	"""
	returns the AMS aid
	"""
        return AID.aid(name="ams." + self._serverplatform, addresses=[ "xmpp://ams."+self._serverplatform ])

    def getDF(self):
	"""
	returns the DF aid
	"""
        return AID.aid(name="df." + self._serverplatform, addresses=[ "xmpp://df."+self._serverplatform ])

    def getMUC(self):
	"""
	returns the MUC JID
	"""
	return "muc." + self._serverplatform

    def getSpadePlatformJID(self):
	"""
	returns the SPADE JID (string)
	"""
        return "acc." + self._serverplatform

    def getDomain(self):
        """
        returns the SPADE server domain
        """
        return self._serverplatform
    
    def getP2PUrl(self):
        return str("spade://"+socket.gethostname()+":"+str(self.P2PPORT))
    

    def requestDiscoInfo(self, to):
        class RequestDiscoInfoBehav(Behaviour.OneShotBehaviour):
            def _process(self):
                self.result = []
                self.myAgent.jabber.send(self.iq)
                msg = self._receive(True, 3)
                if msg:
                    if msg.getType() == "result":
                        services = []
                        for child in msg.T.query.getChildren():
                            services.append(str(child.getAttr("var")))
                        #print "RETRIEVED SERVICES:", services
                        self.result = services
                    
        #print "REQUEST DISCO INFO CALLED BY", str(self.getName())
        id = 'nsdi'+str(random.randint(1,10000))
        temp_iq = xmpp.Iq(queryNS=xmpp.NS_DISCO_INFO, attrs={'id':id})
        temp_iq.setType("result")
        t = Behaviour.MessageTemplate(temp_iq)
        iq = xmpp.Iq(queryNS=xmpp.NS_DISCO_INFO, attrs={'id':id})
        iq.setTo(to)
        iq.setType("get")
        if self._running:
            # Online way
            rdif = RequestDiscoInfoBehav()
            rdif.iq = iq
            self.addBehaviour(rdif, t)
            rdif.join()
            return rdif.result
        else:
            # Offline way
            print "RDI OFFLINE"
            self.jabber.send(iq)
            msg = self._receive(True, 20, template=t)
            if msg:
                if msg.getType() == "result":
                    services = []
                    for child in msg.T.query.getChildren():
                        services.append(str(child.getAttr("var")))
                    print "RETRIEVED SERVICES:", services
                    return services
            return []


    def initiateStream(self, to):
        """
        Perform a Stream Initiation with another agent
        in order to stablish a P2P communication channel
        """
        class StreamInitiationBehav(Behaviour.OneShotBehaviour):
            def _process(self):
                self.result = False
                self.myAgent.jabber.send(self.iq)
                #print "SIB SENT:", str(self.iq)
                msg = self._receive(True, 4)
                if msg:
                    self.result = False
                    if msg.getType() =="result":
                        print "StreamRequest Agreed"
                        #print msg
                        try:
                            remote_address = str(msg.T.si.T.p2p.T.value.getData())
                            d = {"url":remote_address, "p2p":True}
                            if self.myAgent.p2p_routes.has_key(str(msg.getFrom().getStripped())):
                                self.myAgent.p2p_routes[str(msg.getFrom().getStripped())].update(d)
                                self.result = True
                            else:
                                self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = d
                            #print "P2P ROUTES", str(self.myAgent.p2p_routes)
                        except Exception, e:
                            print "Malformed StreamRequest Answer", str(e)
                            self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = {}
                    elif msg.getType() == "error":
                        print "StreamRequest REFUSED"
                        self.myAgent.p2p_routes[str(msg.getFrom().getStripped())] = {'p2p':False}
                else:
                    # Not message, treat like a refuse
                    print "StreamRequest REFUSED"
                    self.myAgent.p2p_routes[str(iq.getTo().getStripped())] = {'p2p':False}

        #print "INITIATE STREAM CALLED BY", str(self.getName())
        # First deal with Disco Info request
        services = self.requestDiscoInfo(to)
        if "http://jabber.org/protocol/si/profile/spade-p2p-messaging" in services:
            # Offer Stream Initiation
            print "Offer StreamInitiation to", str(to)
            id = 'offer'+str(random.randint(1,10000))
            temp_iq = xmpp.Iq(attrs={'id':id})
            t = Behaviour.MessageTemplate(temp_iq)
            iq = xmpp.Iq(attrs={'id':id})
            iq.setTo(to)
            iq.setType("set")
            si = xmpp.Node("si", {"profile":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
            si.setNamespace("http://jabber.org/protocol/si")
            if self.p2p:
                p2p = xmpp.Node("p2p")
                p2p.setNamespace('http://jabber.org/protocol/si/profile/spade-p2p-messaging')
                p2p.setData(self.getP2PUrl())
                si.addChild(node=p2p)
            iq.addChild(node=si)
            if self._running:
                # Online way
                sib = StreamInitiationBehav()
                sib.iq = iq
                self.addBehaviour(sib, t)
                sib.join()
                return sib.result
            else:
                # Offline way
                print "I.S. OFFLINE"
                result = False
                self.jabber.send(iq)
                #print "SIB SENT:", str(self.iq)
                msg = self._receive(True, 10, template=t)
                if msg:
                    result = False
                    if msg.getType() =="result":
                        print "StreamRequest Agreed"
                        #print msg
                        try:
                            remote_address = str(msg.T.si.T.p2p.T.value.getData())
                            d = {"url":remote_address, "p2p":True}
                            if self.p2p_routes.has_key(str(msg.getFrom().getStripped())):
                                self.p2p_routes[str(msg.getFrom().getStripped())].update(d)
                                result = True
                            else:
                                self.p2p_routes[str(msg.getFrom().getStripped())] = d
                            #print "P2P ROUTES", str(self.p2p_routes)
                        except Exception, e:
                            print "Malformed StreamRequest Answer", str(e)
                            self.p2p_routes[str(msg.getFrom().getStripped())] = {}
                    elif msg.getType() == "error":
                        print "StreamRequest REFUSED"
                        self.p2p_routes[str(msg.getFrom().getStripped())] = {'p2p':False}
                return result


    def send(self, ACLmsg, method="auto"):
	"""
	sends an ACLMessage
	"""
        #self._sendTo(ACLmsg, self.getSpadePlatformJID())
        self._sendTo(ACLmsg, ACLmsg.getReceivers(), method=method)

    def _sendTo(self, ACLmsg, tojid, method):
        """
        sends an ACLMessage to a specific JabberID
        """
        """
        if (ACLmsg.getSender() == None):
            ACLmsg.setSender(self.getAID())

        content = ACLmsg.getContent()
        comillas_esc = '\\"'
        barrainv_esc = '\\\\'
        mtmp1 = barrainv_esc.join(content.split('\\'))
        mtmp2 = comillas_esc.join(mtmp1.split('"'))
        payload_esc = mtmp2
        ACLmsg.setContent(payload_esc)

        ap = ACLParser.ACLxmlParser()
        payload = ap.encodeXML(ACLmsg)

        envelope = Envelope.Envelope()
        envelope.setFrom(ACLmsg.getSender())
        for i in ACLmsg.getReceivers():
            envelope.addTo(i)
        envelope.setAclRepresentation("fipa.acl.rep.xml.std")
        envelope.setPayloadLength(len(payload))
        envelope.setPayloadEncoding("US-ASCII")
        envelope.setDate(BasicFipaDateTime.BasicFipaDateTime())

        xc = XMLCodec.XMLCodec()
        envxml = xc.encodeXML(envelope)

        xenv = xmpp.protocol.Node('jabber:x:fipa x')
        xenv['content-type']='fipa.mts.env.rep.xml.std'
        xenv.addData(envxml)
        """
        xenv = xmpp.protocol.Node('jabber:x:fipa x')

        #to = tojid[0]
        # For each of the receivers, try to send the message
        for to in tojid:
            isjabber = False
            for address in to.getAddresses():
                if "xmpp://" in address:
                    # If there is a jabber address for this receiver, send the message directly to it
                    jabber_id = address.split("://")[1]
                    isjabber = True
                    break
            if isjabber and str(self.getDomain()) in jabber_id:
                #jabber_msg = xmpp.protocol.Message(jabber_id, payload, xmlns="")
                jabber_msg = xmpp.protocol.Message(jabber_id, xmlns="")
                jabber_msg.attrs.update(ACLmsg._attrs)
                jabber_msg.addChild(node=xenv)
                jabber_msg["from"]=self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())
            else:
                # I don't understand this address, relay the message to the platform
                #jabber_msg = xmpp.protocol.Message(self.getSpadePlatformJID(),payload, xmlns="")
                jabber_msg = xmpp.protocol.Message(self.getSpadePlatformJID(),payload, xmlns="")
                jabber_msg.attrs.update(ACLmsg._attrs)
                jabber_msg.addChild(node=xenv)
                jabber_msg["from"]=self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())

            if (not self._running and method=="auto") or method=="jabber":
                self.jabber.send(jabber_msg)
                #return
                continue
            
            # If the receiver is one of our p2p contacts, send the message through p2p.
            # If it's not or it fails, send it through the jabber server
            # We suppose method=="p2p"
            jabber_id = xmpp.JID(jabber_id).getStripped()
            if self.p2p and jabber_id not in self.p2p_routes.keys():
                self.initiateStream(jabber_id)
            if self.p2p and self.p2p_routes.has_key(jabber_id) and self.p2p_routes[jabber_id].has_key('p2p') and self.p2p_routes[jabber_id]['p2p'] and self.p2p_routes[jabber_id]['url']:
                try:
                    self.p2p_lock.acquire()
                    self.send_p2p(jabber_msg, jabber_id)
                except Exception, e:
                    #print "Exception in send_p2p", str(e), e                    
                    print "P2P Connection to",jabber_id,"prevented. Falling back"
                    del self.p2p_routes[jabber_id]
                    if method=="auto": self.jabber.send(jabber_msg)
                self.p2p_lock.release()
            else:
                if method=="auto": self.jabber.send(jabber_msg)

    def send_p2p(self, jabber_msg, to=""):
        #print "SENDING ",str(jabber_msg), "THROUGH P2P"
        # Get the address
        if not to: to = str(jabber_msg.getTo())
        url = self.p2p_routes[to]["url"]
        
        # Check if there is already an open socket
        s = None
        if self.p2p_routes[to].has_key("socket"):
            s = self.p2p_routes[to]["socket"]
        if not s:        
            # Parse url
            scheme, address = url.split("://",1)
            if scheme == "spade":
                # Check for address and port number
                l = address.split(":",1)
                if len(l) > 1:
                    address = l[0]
                    port = int(l[1])
            
            # Create a socket connection to the destination url
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            self.p2p_routes[to]["socket"] = s
            if not s:
                # Socket creation failed, throw a exception
                raise socket.error

        # Send message length
        length = "%08d"%(len(str(jabber_msg)))
        s.send(length)
        # Send message through socket
        s.send(str(jabber_msg))
        # Close socket
        #s.close()
        return True

    def _kill(self):
	"""
	kills the agent
	"""
        #self._alive = False
	self._forceKill.set()

    def isRunning(self):
	"""
	returns wether an agent is running or not
	"""
	return self._alive

    def stop(self, timeout=0):
	"""
	Stops the agent execution and blocks until the agent dies
	"""
	self._kill()
	if timeout > 0:
		to = time.now() + timeout
		while self._alive and time.now() < to:
			time.sleep(0.1)
	# No timeout (true blocking)
	else:
		while self._alive:
			time.sleep(0.1)
	return True

    def forceKill(self):
            return self._forceKill.isSet()

    def _setup(self):
	"""
	setup agent method. configures the agent
	must be overridden
        """
        pass

    def takeDown(self):
	"""
	stops the agent
	must be overridden
    (kind of a "onEnd" for the agent)
        """
        pass


    def run(self):
        """
        periodic agent execution
        """
        #Init The agent
        self._setup()
        #Start the Behaviours
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.start()

        #Main Loop
        self._running = True
        while not self.forceKill():
            try:
                #Check for queued messages
                proc = False
                toRemove = []  # List of behaviours to remove after this pass
                msg = self._receive(block=True, timeout=0.01)
                if msg != None:
                    bL = copy.copy(self._behaviourList)
                    for b in bL:
                        t = bL[b]
                        if (t != None):
                            if (t.match(msg) == True):
                                if type(b) == types.ClassType or type(b) == types.TypeType:
                                    #print "Class or Type DETECTED"
                                    #if issubclass(b, Behaviour.EventBehaviour):
                                    #print "EventBehaviour DETECTED"
                                    if b.onetime:
                                        toRemove.append(b)
                                    b = b()
                                    b.setAgent(self)
                                    b.postMessage(msg)
                                    b.start()
                                else:
                                    b.postMessage(msg)
                                proc = True
                                #print ">>>>>>MESSAGE " + str(msg) + " POSTEADO A BEHAV " + str(b)

                    if (proc == False):
                        #print ">>>MESSAGE", str(msg), " DOES NOT MATCH BEHAVIOUR ", str(b)
                        if (self._defaultbehaviour != None):
                               self._defaultbehaviour.postMessage(msg)
                    for beh in toRemove:
                        self._behaviourList.remove(beh)

            except Exception, e:
                print "Agent", self.getName(), "Exception in run:", str(e)
                self._kill()

        self._shutdown()

    def setDefaultBehaviour(self, behaviour):
	"""
	sets a Behavior as Default
	"""
        class NotAllowed(Exception):
            """
            Not Allowed Exception: an EventBehaviour cannot be a default behaviour
            """
            def __init__(self): pass
            def __str__(self): return "an EventBehaviour cannot be a default behaviour"

        if behaviour.__class__ == Behaviour.EventBehaviour:
            raise NotAllowed
        self._defaultbehaviour = behaviour
        behaviour.setAgent(self)

    def getDefaultBehaviour(self):
	"""
	returns the default behavior
	"""
        return self._defaultbehaviour

    def addBehaviour(self, behaviour, template=None):
	"""
	adds a new behavior to the agent
	"""

        if not issubclass(behaviour.__class__, Behaviour.EventBehaviour):  #and type(behaviour) != types.TypeType:
            #ï¿½Event behaviour do not start inmediately
            self._behaviourList[behaviour] = copy.copy(template)
            behaviour.setAgent(self)
            behaviour.start()
        else:
            self._behaviourList[behaviour.__class__] = copy.copy(template)



    def removeBehaviour(self, behaviour):
	"""
	removes a behavior from the agent
	"""
        if not issubclass(behaviour.__class__, Behaviour.EventBehaviour):
            behaviour.kill()
        try:
            self._behaviourList.pop(behaviour)
        except KeyError:
	    #print "removeBehaviour: KeyError"
            pass

    def subscribeToFriend(self, aid):
	"""
	presence subscription to another agent
	"""
        pass

    def unsubscribeToFriend(self, aid):
	"""
	presence unsubscription to another agent
	"""
        pass

    def getSocialNetwork(self, nowait=False):
        """
        get list of social agents which have some relation with the agent
        """
        self._waitingForRoster = True
        iq = Iq("get", NS_ROSTER)
        self.jabber.send(iq)
        if not nowait:
            while self._waitingForRoster:
                time.sleep(0.3)
            return self._roster

    def printSocialNetwork(self):
        s = "{"
        for j, v in self._socialnetwork.items():
            s = s + str(j) + ": " + str(v)
        s = s + "}"
        print s

    def createOrganization(self,organization):
        """
        Creates an organization.
        Returns an instance of AgentOrganization.
        """
        organization.create=True
        self.addBehaviour(organization)

    def joinOrganization(self, organization):
        """
        Joins an agent organization
        """
        if organization.name not in self.getOrganizationList():
            print "The Organization does not exist"
            return
        organization.create=False
        self.addBehaviour(organization)



    def getOrganizationInfo(self,OrgName):
        #en el df comprobar que se trata de una organizaciï¿½n
        if OrgName not in self.getOrganizationList():
            print "The Organization does not exist"
            return {}
        #consultar la informaciï¿½n
        ID="".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(5)])
        iq = Iq(frm=OrgName+"@"+self.getMUC(),typ='result', attrs={"id":ID})
        t1 = Behaviour.MessageTemplate(iq)
        b=self.GetOrganizationInfoBehaviour(self.getMUC(),OrgName,ID)
        self.addBehaviour(b, t1)
        b.join()
        return b.dir


    class GetOrganizationInfoBehaviour(Behaviour.OneShotBehaviour):
            def __init__(self,muc_name,roomname,ID):
                Behaviour.OneShotBehaviour.__init__(self)
                self.ID=ID
                self.dir = {}
                self.muc_name=muc_name
                self.roomname=roomname

            def _process(self):
                iq = Iq(to=self.roomname+"@"+self.muc_name,typ='get', attrs={"id":self.ID})
                query = Protocol('query',xmlns="http://jabber.org/protocol/disco#info ")
                iq.addChild(node=query)
                self.myAgent.jabber.send(iq)
                msg = self._receive(True,10)
                if msg:
                    query = msg.getTag("query")
                    if query:
                        x = query.getTag("x")
                        if x:
                            items =x.getChildren()
                            for item in items:
                                if item.getAttr("var")=="muc#roominfo_subject":
                                    val=item.getTags("value")[0].getData()
                                    self.dir["goal"]=str(val)
                                if item.getAttr("var")=="muc#roominfo_description":
                                    val=item.getTags("value")[0].getData()
                                    self.dir["type"]=str(val)
                                if item.getAttr("var")=="muc#roominfo_lang":
                                    val=item.getTags("value")[0].getData()
                                    self.dir["contentLanguage"]=str(val)
                else:
                    print "Error"




    def getOrganizationList(self):
      ID="".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(5)])
      iq = Iq(frm=self.getMUC(), attrs={"id":ID})
      t = Behaviour.MessageTemplate(iq)
      b=self.GetOrganizationList(ID,self.getMUC())
      self.addBehaviour(b, t)
      b.join()
      return b.result





    class GetOrganizationList(Behaviour.OneShotBehaviour):
        def __init__(self,ID,muc_name):
            Behaviour.OneShotBehaviour.__init__(self)
            self.ID=ID
            self.result = []
            self.muc_name=muc_name

        def _process(self):
           self.result=[]
           iq = Iq(to=self.muc_name,typ='get', attrs={"id":self.ID})
           query = Protocol('query',xmlns="http://jabber.org/protocol/disco#items")
           iq.addChild(node=query)
           self.myAgent.jabber.send(iq)
           msg = self._receive(True,10)
           if msg:
                   items = msg.getQueryChildren()
                   for item in items:
                       if item.getAttr("jid"):
                            template= Iq(frm=item.getAttr("jid"),typ="result", attrs={"id":self.ID})
                            t = Behaviour.MessageTemplate(template)
                            self.setTemplate(t)
                            iq = Iq(to=item.getAttr("jid"),typ='get', attrs={"id":self.ID})
                            query = Protocol('query',xmlns="http://jabber.org/protocol/disco#info")
                            iq.addChild(node=query)
                            self.myAgent.jabber.send(iq)
                            msg = self._receive(True,10)
                            if msg:
                                query = msg.getTag("query")
                                if query:
                                    x = query.getTag("x")
                                    if x:
                                        items =x.getChildren()
                                        for item2 in items:
                                            if item2.getAttr("var") == "muc#roominfo_type":
                                                if item2.getTags("value"):
                                                    value=str(item2.getTags("value")[0].getData())
                                                    if value=="Organization":
                                                        self.result.append(str(item.getAttr("name")))


    def registerSubscribeHandler(self, handler):
	"""
	register the handler that will manage incoming presence subscriptions (agent level)
	"""
	self._subscribeHandler = handler

    def registerUnsubscribeHandler(self, handler):
	"""
	register the handler that will manage incoming presence unsubscriptions (agent level)
	"""
	self._unsubscribeHandler = handler






    class SearchAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, AAD, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self.AAD = AAD
            self.debug = debug
            self.result = None
            self.finished = False
            self._msg = msg

        def _process(self):
            p = SL0Parser.SL0Parser()
            self._msg.addReceiver( self.myAgent.getAMS() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(search "+ str(self.AAD) +")"
            content +=" ))"

            self._msg.setContent(content)
            self.myAgent.send(self._msg)
            msg = self._receive(True,10)
            if msg == None or str(msg.getPerformative()) != 'agree':
                print "There was an error searching the Agent. (not agree)"
                if self.debug:
                    print str(msg)
                self.finished = True
                return None
            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error searching the Agent. (not inform)"
                if self.debug:
                    print str(msg)
                self.finished = True
                return None
            else:
                content = p.parse(msg.getContent())
                if self.debug:
                    print str(msg)
                self.result = [] #content.result.set
		for i in content.result.set:
			#self.result.append(AmsAgentDescription(i)) #TODO: no puedo importar AMS :(
			#print str(i[1])
			self.result.append(i[1])
            self.finished = True

    def searchAgent(self, AAD, debug=False):
	"""
	searches an agent in the AMS
	the search template is an AmsAgentDescription class
	"""
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.SearchAgentBehaviour(msg, AAD, debug)

        self.addBehaviour(b,t)
        b.join()
        return b.result


    class ModifyAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, AAD, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self.AAD = AAD
            self.debug = debug
            self.result = None
            self.finished = False
            self._msg = ACLMessage()

        def _process(self):
            p = SL0Parser.SL0Parser()
            self._msg.addReceiver( self.myAgent.getAMS() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(modify "+ str(self.AAD) + ")"
            content +=" ))"

            self._msg.setContent(content)

            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'agree':
                print "There was an error modifying the Agent. (not agree)"
                if self.debug:
                    print str(msg)
                self.result = False
                return -1
            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error modifying the Agent. (not inform)"
                if self.debug:
                    print str(msg)
                self.result = False
                return -1
            self.result = True
            return 1

    def modifyAgent(self, AAD, debug=False):
	"""
	modifies the AmsAgentDescription of an agent in the AMS
	"""
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.ModifyAgentBehaviour(msg, AAD, debug)

        self.addBehaviour(b,t)
        b.join()
        return b.result


    class getPlatformInfoBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
            self.debug = debug
            self.result = None
            self.finished = False

	def _process(self):
		msg = self._msg
		msg.addReceiver( self.myAgent.getAMS() )
		msg.setPerformative('request')
		msg.setLanguage('fipa-sl0')
		msg.setProtocol('fipa-request')
		msg.setOntology('FIPA-Agent-Management')

		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(get-description platform)"
		content +=" ))"

		msg.setContent(content)

		self.myAgent.send(msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error modifying the Agent. (not agree)"
			if self.debug:
				print str(msg)
			return -1
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error modifying the Agent. (not inform)"
			if self.debug:
				print str(msg)
			return -1

		self.result = msg.getContent()

    def getPlatformInfo(self, debug=False):
	"""
	returns the Plarform Info
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.getPlatformInfoBehaviour(msg, debug)

        self.addBehaviour(b,t)
        b.join()
        return b.result


	##################################

    class registerServiceBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, DAD, debug = False, otherdf = None):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
            self.DAD = DAD
            self.debug = debug
            self.result = None
            self.finished = False
            self.otherdf = otherdf

        def _process(self):
            if self.otherdf and isinstance(self.otherdf, AID.aid):
                self._msg.addReceiver( self.otherdf )
            else:
                self._msg.addReceiver( self.myAgent.getDF() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(register " + str(self.DAD) + ")"
            content +=" ))"

    #        print "#################"
    #        print str(content)
    #        print "#################"

            self._msg.setContent(content)

            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() not in ['agree', 'inform']:
            #if msg == None or msg.getPerformative() != 'agree':
                print "There was an error registering the Service. (not agree)"
                self.result = False
                return
            elif msg == None or msg.getPerformative() == 'agree':
                msg = self._receive(True,20)
                if msg == None or msg.getPerformative() != 'inform':
                    print "There was an error registering the Service. (not inform)"
                    self.result = False
                    return

            if self.debug:
                print str(msg)
            self.result = True

    def registerService(self, DAD, debug=False, otherdf=None):
        """
        registers a service in the DF
        the service template is a DfAgentDescriptor
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        if otherdf and isinstance(otherdf, AID.aid):
            template.setSender(otherdf)
        else:
            template.setSender(self.getDF())
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        if self._running:
         	b = AbstractAgent.registerServiceBehaviour(msg=msg, DAD=DAD, debug=debug, otherdf=otherdf)
          	self.addBehaviour(b,t)
           	b.join()
        	return b.result
        else:
            # Inline operation, done when the agent is starting
            if otherdf and isinstance(otherdf, AID.aid):
                smsg.addReceiver( otherdf )
            else:
                msg.addReceiver( self.getDF() )
            msg.setPerformative('request')
            msg.setLanguage('fipa-sl0')
            msg.setProtocol('fipa-request')
            msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.getAID())
            content += "(register " + str(DAD) + ")"
            content +=" ))"

            msg.setContent(content)
            self.send(msg)

	    # EYE! msg becomes the reply
            msg = self._receive(block=True, timeout=20, template=t)
            if msg == None or msg.getPerformative() not in ['agree', 'inform']:
                print "There was an error registering the Service. (not agree)", str(msg)
                return False

            elif msg == None or msg.getPerformative() == 'agree':
                msg = self._receive(block=True, timeout=20, template=t)
                if msg == None or msg.getPerformative() != 'inform':
                    print "There was an error registering the Service. (not inform)"
                    return False

            return True


    class deregisterServiceBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, DAD, debug=False, otherdf=None):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
            self.DAD = DAD
            self.debug = debug
            self.result = None
            self.finished = False
            self.otherdf = otherdf

        def _process(self):
            if self.otherdf and isinstance(self.otherdf, AID.aid):
                self._msg.addReceiver( self.otherdf )
            else:
                self._msg.addReceiver( self.myAgent.getDF() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(deregister " + str(self.DAD) + ")"
            content +=" ))"

            self._msg.setContent(content)

            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() not in ['agree', 'inform']:
                print "There was an error deregistering the Service. (not agree)"
                if self.debug:
                    print str(msg)
                self.result = False
                return
            elif msg == None or msg.getPerformative() == 'agree':
                msg = self._receive(True,20)
                if msg == None or msg.getPerformative() != 'inform':
                    print "There was an error deregistering the Service. (not inform)"
                    if self.debug:
                        print str(msg)
                    self.result = False
                    return

            if self.debug:
                print str(msg)
            self.result = True
            return

    def deregisterService(self, DAD, debug=False, otherdf=None):
        """
        deregisters a service in the DF
        the service template is a DfAgentDescriptor
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        if self.forceKill():

            if otherdf and isinstance(otherdf, AID.aid):
                msg.addReceiver( otherdf )
            else:
                msg.addReceiver( self.getDF() )
            msg.setPerformative('request')
            msg.setLanguage('fipa-sl0')
            msg.setProtocol('fipa-request')
            msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.getAID())
            content += "(deregister " + str(DAD) + ")"
            content +=" ))"

            msg.setContent(content)
            self.send(msg)

            # EYE! from here, msg becomes the reply
            msg = self._receive(True, 20, t)
            if msg == None or msg.getPerformative() not in ['agree', 'inform']:
                print "There was an error deregistering the Service. (not agree)"
                #if self.debug:
                #    print str(msg)
                return False

            elif msg == None or msg.getPerformative() == 'agree':
                msg = self._receive(True, 20, t)
                if msg == None or msg.getPerformative() != 'inform':
                    print "There was an error deregistering the Service. (not inform)"
                    #if self.debug:
                    #    print str(msg)
                    return False

            return True

        else:
            # The agent is alive and kicking. We must launch a behaviour to perform the deregister
            msg = ACLMessage.ACLMessage()
            template = Behaviour.ACLTemplate()
            template.setConversationId(msg.getConversationId())
            t = Behaviour.MessageTemplate(template)
            b = AbstractAgent.deregisterServiceBehaviour(msg, DAD, debug, otherdf)

            self.addBehaviour(b,t)
            b.join()
            return b.result

    class searchServiceBehaviour(Behaviour.OneShotBehaviour):

    	def __init__(self, msg, DAD, debug=False):
                Behaviour.OneShotBehaviour.__init__(self)
                self._msg = msg
    	        self.DAD = DAD
                self.debug = debug
                self.result = None
                self.finished = False


        def _process(self):

            self._msg.addReceiver( self.myAgent.getDF() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(search "+ str(self.DAD) +")"
            content +=" ))"

            self._msg.setContent(content)

            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'agree':
                print "There was an error searching the Agent. (not agree)"
                #if self.debug:
                #    print str(msg)
                return
            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error searching the Agent. (not inform)"
                #if self.debug:
                #    print str(msg)
                return

            else:
                try:
                    p = SL0Parser.SL0Parser()
                    content = p.parse(msg.getContent())
                    #if self.debug:
                    #    print str(msg)
                    self.result = []
                    for dfd in content.result.set:  #[0]#.asList()
                        d = DF.DfAgentDescription()
                        d.loadSL0(dfd[1])
                        self.result.append(d)
                except:
                    return


    def searchService(self, DAD, debug=True):
    	"""
    	search a service in the DF
    	the service template is a DfAgentDescriptor
        
    	"""
        a=2
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        if self._running:
            b = AbstractAgent.searchServiceBehaviour(msg, DAD, debug)
            self.addBehaviour(b,t)
            b.join()
            return b.result
        else:
            # Inline operation (done when the agent is starting)
            result = []
            try:
                msg.addReceiver( self.getDF() )
                msg.setPerformative('request')
                msg.setLanguage('fipa-sl0')
                msg.setProtocol('fipa-request')
                msg.setOntology('FIPA-Agent-Management')

                content = "((action "
                content += str(self.getAID())
                content += "(search "+ str(DAD) +")"
                content +=" ))"

                msg.setContent(content)
                self.send(msg)

                # EYE! msg becomes the reply
                #time.sleep(0.5)
                msg = self._receive(block=True, timeout=10, template=t)

                if msg == None or msg.getPerformative() not in ['agree', 'inform']:
                    #if msg == None or msg.getPerformative() != 'agree':
                    print "There was an error searching the Service. (not agree)", str(msg)
                    return result

                elif msg == None or msg.getPerformative() == 'agree':
                    msg = self._receive(True, 10, t)

                    if msg == None or msg.getPerformative() != 'inform':
                        print "There was an error searching the Service. (not inform)"
                        return result

                p = SL0Parser.SL0Parser()
                content = p.parse(msg.getContent())
                for dfd in content.result.set:  #[0]#.asList()
                    d = DF.DfAgentDescription()
                    d.loadSL0(dfd[1])
                    result.append(d)
                return result
            except:
                _exception = sys.exc_info()
                if _exception[0]:
                    print '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                #print "EXCEPTION IN SEARCHSERVICE", str(e)
                return result



    class modifyServiceBehaviour(Behaviour.OneShotBehaviour):
	def __init__(self, msg, DAD, debug=False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
	    self.DAD = DAD
            self.debug = debug
            self.result = None

	def _process(self):

		#p = SL0Parser.SL0Parser()

		self._msg = ACLMessage.ACLMessage()
		self._msg.addReceiver( self.myAgent.getDF() )
		self._msg.setPerformative('request')
		self._msg.setLanguage('fipa-sl0')
		self._msg.setProtocol('fipa-request')
		self._msg.setOntology('FIPA-Agent-Management')

		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(modify "+ str(self.DAD) + ")"
		content +=" ))"

		self._msg.setContent(content)

		self.myAgent.send(self._msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error modifying the Service. (not agree)"
			if self.debug:
				print str(msg)
			self.result=False
			return
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error modifying the Service. (not inform)"
			if self.debug:
				print str(msg)
			self.result = False
			return

		self.result = True
		return
    def modifyService(self, DAD, debug=False):
	"""
	modifies a service in the DF
	the service template is a DfAgentDescriptor
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.modifyServiceBehaviour(msg, DAD, debug)

        self.addBehaviour(b,t)
        b.join()
        return b.result


	##################################

# Changed to be a 'daemonic' python Thread
class jabberProcess(threading.Thread):

	def __init__(self, socket, owner):
		self.jabber = socket
		#self._alive = True
		self._forceKill = threading.Event()
		self._forceKill.clear()
		threading.Thread.__init__(self)
		self.setDaemon(False)
		self._owner = owner

	def _kill(self):
		try:
			self._forceKill.set()
		except:
			#Agent is already dead
			pass

	def forceKill(self):
		return self._forceKill.isSet()

	def run(self):
		"""
		periodic jabber update
		"""
		while not self.forceKill():
		    try:
			err = self.jabber.Process(0.4)
			#print "Process returns " + str(err) + " " + str(type(err))
		    except Exception, e:
			_exception = sys.exc_info()
			if _exception[0]:
			    print '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
			    print "Exception in jabber process: ", str(e)
			    print color_red + "Jabber connection failed: " + color_yellow + str(self._owner.getAID().getName()) + color_red + " (dying)" + color_none
			    self._kill()
			    self._owner.stop()
			    err = None

		    if err == None or err == 0:  # None or zero the integer, socket closed
			print color_red + "Agent disconnected: " + color_yellow + str(self._owner.getAID().getName()) + color_red + " (dying)" + color_none
			self._kill()
			self._owner.stop()



class PlatformAgent(AbstractAgent):
    """
    A PlatformAgent is a SPADE component.
    Examples: AMS, DF, ACC, ...
    """
    def __init__(self, node, password, server="localhost", port=5347, config=None ,debug = [], p2p=False):
        AbstractAgent.__init__(self, node, server, p2p=p2p)
        self.config = config
        self.debug = debug
        self.jabber = xmpp.Component(server=server, port=port, debug=self.debug)
        self._register(password)

    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        #TODO: Que pasa si no conectamos? Hay que controlarlo!!!
        while not self.jabber.connect():
              time.sleep(0.005)


        if (self.jabber.auth(name=name,password=password) == None):
              raise NotImplementedError

        #print "Auth ok", name
        self.jabber.RegisterHandler('message',self._jabber_messageCB)
        self.jabber.RegisterHandler('presence',self._jabber_messageCB)
        self.jabber.RegisterHandler('iq',self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence',self._jabber_presenceCB)
        #self.jabber.RegisterHandler('iq',self._jabber_iqCB)

        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()
        #thread.start_new_thread(self._jabber_process, tuple())

    def _shutdown(self):

        self._kill()  # Doublecheck death
        self.jabber_process._kill()

        #Stop the Behaviours
        for b in self._behaviourList:
            b.kill()
            #self.removeBehaviour(b)
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.kill()
        #DeInit the Agent
        self.takeDown()

        self._alive = False

class Agent(AbstractAgent):
    """
    This is the main class which may be inherited to build a SPADE agent
    """
           
    class OutOfBandBehaviour(Behaviour.EventBehaviour):
        def openP2P(self, url):
            """
            Open a P2P connection with a remote agent
            """

            # Parse url
            scheme, address = url.split("://",1)
            if scheme == "spade":
                # Check for address and port number
                l = address.split(":",1)
                if len(l) > 1:
                    address = l[0]
                    port = l[1]
                else:
                    port = self.myAgent.P2PPORT
            """
            NOT FOR THE MOMENT    
            # Create a socket connection to the destination url
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            if not s:
                # Socket creation failed, throw a exception
                raise socket.error
                
            # Return socket
            return s
            """
            return None
	    		
    		
        def _process(self):
            self.msg = self._receive(False)
            if self.msg != None:
                print "OOB IQ RECEIVED"
                # Check type of oob iq
                if self.msg.getType() == "error":
                    # Check error code
                    try:
                        if self.msg.getTag('error').getAttr("code") == "404":
                            pass
                        elif self.msg.getTag('error').getAttr("code") == "406":
                            pass
                    except:
                        # WTF
                        pass
                elif self.msg.getType() == "set":
                    # OOB proposal
                    if self.myAgent.p2p:
                        # Accept p2p proposal
                        try:
                            # Add remote oob data to p2p routes
                            url = msg.T.query.T.url.getData()
                            remote = {'url':url, 'socket':self.openP2P(url)}
                            d = {self.msg.getSender().getName():remote}
                            self.myAgent.p2p_routes.update(d)
                            # Send result INCLUDING our own p2p url
                            reply = msg.buildReply("result")
                            reply.T.query.delChild("url")
                            reply.T.query.addChild("url")
                            reply.T.query.T.url.setData(self.myAgent.getP2PUrl())
                            self.myAgent.jabber.send(reply)
                        except:
                            # The oob-iq was not well formed. Send 404
                            reply = self.msg.buildReply("error")
                            err = Node("error", {'code':'404', 'type':'cancel'})
                            err.addChild("not-found")
                            err.setNamespace('urn:ietf:params:xml:ns:xmpp-stanzas')
                            reply.addChild(err)
                            self.myAgent.jabber.send(reply)
                    else:
                        # Reject p2p proposal
                        reply = self.msg.buildReply("error")
                        err = xmpp.Node("error", {'code':'406', 'type':'modify'})
                        err.addChild("not-acceptable")
                        err.setNamespace('urn:ietf:params:xml:ns:xmpp-stanzas')
                        reply.addChild(err)
                        self.myAgent.jabber.send(reply)
                elif self.msg.getType() == "result":
                    # Check for remote P2P url
                    try:
                        url = msg.T.query.T.url.getData()
                        remote = {'url':url, 'socket':self.openP2P(url)}
                        d = {self.msg.getSender().getName():remote}
                        self.myAgent.p2p_routes.update(d)
                    except:
                        # No url info came
                        pass




    class PresenceBehaviour(Behaviour.EventBehaviour):
        def _process(self):
            self.msg = self._receive(False)
            if self.msg != None:
                #print "PRESENCEBEHAVIOUR CALLED WITH", self.msg
                if self.msg.getType() == "subscribe":
                    # Subscribe petition
                    # Answer YES
                    rep = Presence(to=self.msg.getFrom())
                    rep.setType("subscribed")
                    self.myAgent.jabber.send(rep)
                    print color_yellow + str(self.msg.getFrom()) + color_green + " subscribes to me" + color_none
                    rep.setType("subscribe")
                    self.myAgent.jabber.send(rep)
                    print "Subscription request sent in return"
                if self.msg.getType() == "subscribed":
                    if self.msg.getFrom() == self.myAgent.getAMS().getName():
                        # Subscription confirmation from AMS
                        print color_green + "Agent: " + color_yellow + str(self.myAgent.getAID().getName()) + color_green + " registered correctly (inform)" + color_none
                    else:
                        print color_yellow + str(self.msg.getFrom()) + color_green + " has subscribed me" + color_none
                elif self.msg.getType() == "unsubscribed":
                    # Unsubscription from AMS
                    if self.msg.getFrom() == self.myAgent.getAMS().getName():
                        print color_red + "There was an error registering in the AMS: " + color_yellow + str(self.getAID().getName()) + color_none
                    else:
                        print color_yellow + str(self.msg.getFrom()) + color_green + " has unsubscribed me" + color_none
                elif self.msg.getType() in ["available", ""]:
                    print "Agent " + str(self.msg.getFrom()) + " is online"
                    self.myAgent.setSocialItem(self.msg.getFrom(), "available")
                elif self.msg.getType() == "unavailable":
                    print "Agent " + str(self.msg.getFrom()) + " is offline"
                    self.myAgent.setSocialItem(self.msg.getFrom(), "unavailable")

                self.myAgent.getSocialNetwork()
                #self.myAgent.printSocialNetwork()


    class RosterBehaviour(Behaviour.EventBehaviour):
        def _process(self):
            stanza = self._receive(False)
            if stanza != None:
                #print "ROSTERBEHAV LLAMADO"
                for item in stanza.getTag('query').getTags('item'):
                    jid=item.getAttr('jid')
                    if item.getAttr('subscription')=='remove':
                        if self.myAgent._roster.has_key(jid): del self.myAgent.roster[jid]
                    elif not self.myAgent._roster.has_key(jid): self.myAgent._roster[jid]={}
                    self.myAgent._roster[jid]['name']=item.getAttr('name')
                    self.myAgent._roster[jid]['ask']=item.getAttr('ask')
                    self.myAgent._roster[jid]['subscription']=item.getAttr('subscription')
                    self.myAgent._roster[jid]['groups']=[]
                    if not self.myAgent._roster[jid].has_key('resources'): self.myAgent._roster[jid]['resources']={}
                    for group in item.getTags('group'): self.myAgent._roster[jid]['groups'].append(group.getData())
                #self.myAgent._roster[self._owner.User+'@'+self._owner.Server]={'resources':{},'name':None,'ask':None,'subscription':None,'groups':None,}
                self.myAgent._waitingForRoster = False
                #print "TENGO UN ROSTER", str(self.myAgent._roster)
                #self.myAgent.printSocialNetwork()


    class SocialItem:
        """
        A member of an agent's Social Network
        AID, presence & subscription
        """
        def __init__(self, agent, jid, presence=""):
            self.presence = ""

            # Generate AID
            self._aid = AID.aid(name=jid, addresses=["xmpp://"+str(jid)])

            # Get subscription from roster
            roster = agent._roster
            if roster.has_key(jid):
                if roster[jid].has_key("subscription"):
                    self._subscription = roster[jid]["subscription"]
                else:
                    self._subscription = "none"
            else:
                self._subscription = "none"

            if presence:
                self._presence = presence

        def setPresence(self, presence):
            self._presence = presence

        def getPresence(self):
            return self._presence


    def __init__(self, agentjid, password, port=5222, debug=[]):
        jid = xmpp.protocol.JID(agentjid)
        self.server = jid.getDomain()
        self.port = port
        self.debug = debug
        AbstractAgent.__init__(self, agentjid, self.server)
        self.jabber = xmpp.Client(self.server, self.port, self.debug)
        
        self.remote_services = {}  # Services of remote agents
        
        # Try to register
        try:
            #print "### Trying to register agent %s"%(agentjid)
            self._register(password)
        except NotImplementedError:
            #print "### NotImplementedError: Could not register agent %s"%(agentjid)
            self.stop()
            return
        except:
            #print "### Could not register agent %s"%(agentjid)
            self.stop()
            return

        # Add Presence Control Behaviour
        self.addBehaviour(Agent.PresenceBehaviour(), Behaviour.MessageTemplate(Presence()))

        # Add Roster Behaviour
        self.addBehaviour(Agent.RosterBehaviour(), Behaviour.MessageTemplate(Iq(queryNS=NS_ROSTER)))

        

        #print "### Agent %s registered"%(agentjid)

        if not self.__register_in_AMS():
            print "Agent " + str(self.getAID().getName()) + " dying ..."
            sys.exit(-1)

        # Ask for roster
        self.getSocialNetwork(nowait=True)

    def setSocialItem(self, jid, presence=""):
        if self._socialnetwork.has_key(jid):
            if not self._socialnetwork[jid].getPresence():
                # If we have no previous presence information, update it
                self._socialnetwork[jid].setPresence(presence)
        else:
            self._socialnetwork[jid] = Agent.SocialItem(self, jid, presence)


        





    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        c = ''
        while not self.jabber.connect(use_srv=None): time.sleep(0.005)
        #print "### Agent %s got connected to the server"%(self._aid.getName())

        #TODO:  Que pasa si no nos identificamos? Hay que controlarlo!!!
        #       Registrarse automaticamente o algo..
        if (self.jabber.auth(name,password,"spade") == None):
            #raise NotImplementedError

        #print "### Agent %s: First auth attempt failed"%(self._aid.getName())

            if (autoregister == True):
                xmpp.features.getRegInfo(self.jabber,jid.getDomain())
                xmpp.features.register(self.jabber,jid.getDomain(),\
                {'username':name, 'password':str(password), 'name':name})

                """
                self.jabber.disconnect()

                del self.jabber
                self.jabber = xmpp.Client(self.server, self.port, self.debug)

                self.jabber.connect(use_srv=False)
                """

                if not self.jabber.reconnectAndReauth():
                    #if (self.jabber.auth(name,password,"spade") == None):
                    print "### Agent %s: Second auth attempt failed"%(self._aid.getName())
                    raise NotImplementedError
            else:
                    raise NotImplementedError

        #print "### Agent %s got authed"%(self._aid.getName())

        self.jabber.RegisterHandler('message',self._jabber_messageCB)
        self.jabber.RegisterHandler('presence',self._jabber_messageCB)
        self.jabber.RegisterHandler('iq',self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence',self._jabber_presenceCB)

        #thread.start_new_thread(self._jabber_process, tuple())
        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()
        #print "### Agent %s: Started jabber process"%(self._aid.getName())

        # Request roster and send initial presence

        self.jabber.sendInitPresence()

        #print "ROSTER: ", str(self._roster.getItems())


    def _shutdown(self):
        #Stop the Behaviours
        for b in self._behaviourList:
            if type(b) == types.InstanceType:
                b.kill()
            #self.removeBehaviour(b)
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.kill()

        #DeInit the Agent
        self.takeDown()

        if self._alivemutex.testandset():
            if not self.jabber_process.forceKill():
                if not self.__deregister_from_AMS():
                    print "Agent " + str(self.getAID().getName()) + " dying without deregistering itself ..."
                self.jabber_process._kill()  # Kill jabber thread
            self._alive = False
        self._alivemutex.unlock()

        self._kill()  # Doublecheck death



    def __register_in_AMS(self, state='active', ownership=None, debug=False):

        #presence = xmpp.Presence(to=self.getAMS().getName(),frm=self.getName(),typ='subscribed')
        # Let's change it to "subscribe"
        presence = xmpp.Presence(to=self.getAMS().getName(),frm=self.getName(),typ='subscribe')

        self.jabber.send(presence)

        #print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " registered correctly (inform)" + color_none
        return True

    def __register_in_AMS_with_ACL(self, state='active', ownership=None, debug=False):

        self._msg = ACLMessage.ACLMessage()
        self._msg.addReceiver( self.getAMS() )
        self._msg.setPerformative('request')
        self._msg.setLanguage('fipa-sl0')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        content = "((action "
        content += str(self.getAID())
        content += "(register (ams-agent-description "
        content += ":name " + str(self.getAID())
        content += ":state "+state
        if ownership:
            content += ":ownership " + ownership
        content +=" ) ) ))"

        self._msg.setContent(content)

        self.send(self._msg)

        # We expect the initial answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (str(msg.getPerformative()) == 'refuse'):
            print color_red + "There was an error initiating the register of agent: " + color_yellow + str(self.getAID().getName()) + color_red + " (refuse)" + color_none
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
            print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " initiating registering process (agree)" + color_none
        else:
            # There was no answer from the AMS or it answered something weird, so error
            print color_red + "There was an error initiating the register of agent: " + color_yellow + str(self.getAID().getName()) + color_none
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (msg.getPerformative() == 'failure'):
            print color_red + "There was an error with the register of agent: " + color_yellow + str(self.getAID().getName()) + color_red + " (failure)" + color_none
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
            print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " registered correctly (inform)" + color_none
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            print color_red + "There was an error with the register of agent: " + color_yellow + str(self.getAID().getName()) + color_none
            return False

        return True


    def __deregister_from_AMS(self, state=None, ownership=None, debug=False):

        presence = xmpp.Presence(to=self.getAMS().getName(),frm=self.getName(),typ='unsubscribed')

        self.jabber.send(presence)
        print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " deregistered correctly (inform)" + color_none

        return True


    def __deregister_from_AMS_with_ACL(self, state=None, ownership=None, debug=False):

        _msg = ACLMessage.ACLMessage()
        _msg.addReceiver( self.getAMS() )
        _msg.setPerformative('request')
        _msg.setLanguage('fipa-sl0')
        _msg.setProtocol('fipa-request')
        _msg.setOntology('FIPA-Agent-Management')

        content = "((action "
        content += str(self.getAID())
        content += "(deregister (ams-agent-description "
        content += " :name " + str(self.getAID())
        if state:
            content += " :state "+state
        if ownership:
            content += " :ownership " + ownership
        content +=" ) ) ))"

        _msg.setContent(content)

        self.send(_msg)

        # We expect the initial answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (str(msg.getPerformative()) == 'refuse'):
            print colors.color_red + "There was an error initiating the deregister of agent: " + colors.color_yellow + str(self.getAID().getName()) + colors.color_red + " (refuse)" + colors.color_none
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
            print colors.color_green + "Agent: " + colors.color_yellow + str(self.getAID().getName()) + colors.color_green + " initiating deregistering process (agree)" + colors.color_none
        else:
            # There was no answer from the AMS or it answered something weird, so error
            print colors.color_red + "There was an error deregistering of agent: " + colors.color_yellow + str(self.getAID().getName()) + colors.color_none
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (msg.getPerformative() == 'failure'):
            print "There was an error with the deregister of agent: " + str(self.getAID().getName()) + " (failure)"
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
            print "Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)"
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            print "There was an error with the deregister of agent: " + str(self.getAID().getName())
            return False

        return True
