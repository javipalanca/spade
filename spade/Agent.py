# -*- coding: cp1252 -*-

try:
    import psyco
    psyco.full()
except ImportError:
    pass #self.DEBUG("Psyco optimizing compiler not found","warn")

import sys
import xml.dom.minidom
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
import fipa
import peer2peer as P2P
import socialnetwork
import RPC

import mutex
import types
import random
import string
import copy
import socket
import SocketServer
import colors
import cPickle as pickle


import DF
from content import ContentObject
from wui import *

from xmpp import *

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

try:
    threading.stack_size(64 * 1024)  # 64k compo
except: pass

class AbstractAgent(MessageReceiver.MessageReceiver):
    """
    Abstract Agent
    only for heritance
    Child classes: PlatformAgent, Agent
    """

    def __init__(self, agentjid, serverplatform, p2p=False):
        """
        inits an agent with a JID (user@server) and a platform JID (acc.platformserver)
        """
        MessageReceiver.MessageReceiver.__init__(self)
        self._agent_log = {}  # Log system
        self._aid = AID.aid(name=agentjid, addresses=["xmpp://"+agentjid])
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
        
        self._debug = False
        self._debug_filename = ""
        self._debug_file = None
        
        self._messages={}
        self._messages_mutex = thread.allocate_lock()
        
        self.wui = WUI(self)
        self.wui.registerController("admin", self.WUIController_admin)
        self.wui.registerController("log", self.WUIController_log)
        self.wui.registerController("messages",self.WUIController_messages)
        self._aclparser = ACLParser.ACLxmlParser()

        #self._friend_list = []  # Legacy
        #self._muc_list= {}
        self._roster = {}
        self._socialnetwork = {}
        self._subscribeHandler   = lambda frm,typ,stat,show: False
        self._unsubscribeHandler = lambda frm,typ,stat,show: False

        self._waitingForRoster = False  # Indicates that a request for the roster is in progress

        self.behavioursGo = threading.Condition()  # Condition to synchronise behaviours
        self._running = False

        # Add Disco Behaviour
        self.addBehaviour(P2P.DiscoBehaviour(), Behaviour.MessageTemplate(Iq(queryNS=NS_DISCO_INFO)))

        # Add Stream Initiation Behaviour
        iqsi = Iq()
        si = iqsi.addChild("si")
        si.setNamespace("http://jabber.org/protocol/si")
        self.addBehaviour(P2P.StreamInitiationBehaviour(), Behaviour.MessageTemplate(iqsi))

        # Add P2P Behaviour
        self.p2p_ready = False  # Actually ready for P2P communication
        self.p2p = p2p
        self.p2p_routes = {}
        self.p2p_lock = thread.allocate_lock()
        self.p2p_send_lock = thread.allocate_lock()
        self._p2p_failures = 0  # Counter for failed attempts to send p2p messages
        if p2p:
            self.registerLogComponent("p2p")
            self.P2PPORT = random.randint(1025,65535)  # Random P2P port number
            p2pb = P2P.P2PBehaviour()
            self.addBehaviour(p2pb)
            
        #Remote Procedure Calls support
        self.RPC = {}
        self.addBehaviour(RPC.RPCServerBehaviour(), Behaviour.MessageTemplate(Iq(typ='set',queryNS=NS_RPC)))

    def WUIController_admin(self):
        import types
        behavs = {}
        attrs = {}
        sorted_attrs = []	
        for k in self._behaviourList.keys():
            behavs[id(k)]=k
        for attribute in self.__dict__:
            if eval( "type(self."+attribute+") not in [types.MethodType, types.BuiltinFunctionType, types.BuiltinMethodType, types.FunctionType]" ):
                if attribute not in ["_agent_log"]:
		    attrs[attribute] = eval( "str(self."+attribute+")" )
        sorted_attrs = attrs.keys()
        sorted_attrs.sort()
	import pygooglechart
	chart=pygooglechart.QRChart(125,125)
	chart.add_data(self.getAID().asXML())
	chart.set_ec('H',0)
        return "admin.pyra", {"name":self.getName(),"aid":self.getAID(), "qrcode":chart.get_url(), "defbehav":(id(self._defaultbehaviour),self._defaultbehaviour), "behavs":behavs, "p2pready":self.p2p_ready, "p2proutes":self.p2p_routes, "attrs":attrs, "sorted_attrs":sorted_attrs}
        
    def WUIController_log(self):
        return "log.pyra", {"name":self.getName(), "log":self.getLog()}

    def WUIController_messages(self):
        index=0
        mess = {}
        msc = ""
        for ts,m in self._messages.items():
            if isinstance(m,ACLMessage.ACLMessage):
                strm=self._aclparser.encodeXML(m)
                x = xml.dom.minidom.parseString(strm)
                strm = x.toprettyxml()
                frm = m.getSender()
                if frm!=None: frm = str(frm.getName())
                else: frm = "Unknown"
                if "/" in frm: frm=frm.split("/")[0]
                r = m.getReceivers()
                if len(r)>=1:
                    to = r[0].getName()
                else:
                    to = "Unknown"
                if "/" in to: to=to.split("/")[0]
                msc += frm+"->"+to+':'+str(index)+" "+str(m.getPerformative())+'\n'
            else:
                strm=str(m)
                strm = strm.replace("&gt;",">")
                strm = strm.replace("&lt;","<")
                strm = strm.replace("&quot;",'"')
                x = xml.dom.minidom.parseString(strm)
                strm = x.toprettyxml()
                frm = m.getFrom()
                if frm==None: frm = "Unknown"
                else: frm = str(frm)
                if "/" in frm: frm=frm.split("/")[0]
                to = m.getTo()
                if to==None: to = "Unknown"
                else: to = str(to)
                if "/" in to: to=to.split("/")[0]
                msc += frm+"-->"+to+':'+str(index)+' '+str(m.getName())
                if m.getType(): msc+=" " + str(m.getType())+'\n'
                elif m.getName()=="message":
                    if m.getAttr("performative"): msc+=" " + str(m.getAttr("performative"))+'\n'
                    else: msc+='\n'
                else: msc+='\n'

            mess[index]=(ts,strm)
            index+=1

        try:
            import diagram
            self.DEBUG("Generating diagram with: " + msc)
            url = diagram.getSequenceDiagram(msc,style="napkin")
        except:
            url=False
        
        return "messages.pyra", {"name":self.getName(), "messages":mess, "diagram": url}

    def registerLogComponent(self, component):
        #self._agent_log[component] = {}
        pass

    def DEBUG(self, dmsg, typ="info", component="spade"):
        # Record at log
        t = time.time()
        dmsg = dmsg.replace("&gt;",">")
        dmsg = dmsg.replace("&lt;","<")
        dmsg = dmsg.replace("&quot;",'"')

        self._agent_log[t] = (typ,dmsg,component,time.ctime(t))

        if self._debug:
            # Print on screen
            if typ == "info":
                print colors.color_none + "DEBUG:[" + component + "] " + dmsg + " , info" + colors.color_none
            elif typ == "err":
                print colors.color_none + "DEBUG:[" + component + "] " + color_red + dmsg + " , error" + colors.color_none
            elif typ == "ok":
                print colors.color_none + "DEBUG:[" + component + "] " + colors.color_green + dmsg + " , ok" + colors.color_none
            elif typ == "warn":
                print colors.color_none + "DEBUG:[" + component + "] " + colors.color_yellow + dmsg + " , warn" + colors.color_none

        # Log to file
        if self._debug_file:
            if typ == "info":
                self._debug_file.write( self._agent_log[t][3] + ": [" + component + "] " + dmsg + " , info\n")
            elif typ == "err":
                self._debug_file.write( self._agent_log[t][3] + ": [" + component + "] " + dmsg + " , error\n")
            elif typ == "ok":
                self._debug_file.write( self._agent_log[t][3] + ": [" + component + "] " + dmsg + " , ok\n")
            elif typ == "warn":
                self._debug_file.write( self._agent_log[t][3] + ": [" + component + "] " + dmsg + " , warn\n")
            self._debug_file.flush()

    def setDebug(self, activate = True):
        self.setDebugToScreen(activate)
        self.setDebugToFile(activate)

    def setDebugToScreen(self, activate = True):
        self._debug = activate

    def setDebugToFile(self, activate = True, fname = "" ):
        if not fname:
            self._debug_filename = self.getName() + ".log"
        else:
            self._debug_filename = fname

        try:
            if self._debug_file:
                self._debug_file.close()
            self._debug_file = open(self._debug_filename, "a+")
        except:
            self.DEBUG("Could not open file " + self._debug_filename + " as log file", "err")

    def getLog(self):
        keys = self._agent_log.keys()
        keys.sort()
        keys.reverse()
        l = list()
        for k in keys:
            l.append(self._agent_log[k])
        return l

    def newMessage(self):
        """Creates and returns an empty ACL message"""
        return ACLMessage.ACLMessage()

    def newContentObject(self):
        """Creates and returns an empty Content Object"""
        return ContentObject()

    def _jabber_presenceCB(self, conn, mess):
        """
        presence callback
        manages jabber stanzas of the 'presence' protocol
        """

        frm = mess.getFrom()
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

        try:
            # Pass the FIPA-message to the behaviours
            for b in self._behaviourList.keys():
                b.managePresence(frm, typ, status, show, role, affiliation)

            self._defaultbehaviour.managePresence(frm, typ, status, show, role, affiliation)
        except Exception, e:
            #There is not a default behaviour yet
            self.DEBUG(str(e),"err")

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

                # Check wether there is an envelope
                if child.getTag("envelope"):
                    # There is an envelope; use it to build sender and receivers
                    xc = XMLCodec.XMLCodec()
                    envelope = xc.parse(str(child.getTag("envelope")))
                    if envelope.getFrom():
                        try:
                            ACLmsg.setSender(envelope.getFrom().getStripped())
                        except:
                            ACLmsg.setSender(envelope.getFrom())
                    else:
                        ACLmsg.setSender(AID.aid(str(mess.getFrom().getStripped()), ["xmpp://"+str(mess.getFrom().getStripped())]))
                    if envelope.getIntendedReceiver():
                        for ir in envelope.getIntendedReceiver():
                            ACLmsg.addReceiver(ir)
                    else:
                        ACLmsg.addReceiver(AID.aid(str(mess.getTo().getStripped()), ["xmpp://"+str(mess.getTo())]))
                else:
                    ACLmsg.setSender(AID.aid(str(mess.getFrom().getStripped()), ["xmpp://"+str(mess.getFrom().getStripped())]))
                    ACLmsg.addReceiver(AID.aid(str(mess.getTo().getStripped()), ["xmpp://"+str(mess.getTo().getStripped())]))

                self._messages_mutex.acquire()
                timestamp = time.time()
                self._messages[timestamp]=ACLmsg
                self._messages_mutex.release()
                self.postMessage(ACLmsg)
                if raiseFlag: raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
                return True

        # Not a jabber-fipa message
        self._messages_mutex.acquire()
        timestamp = time.time()
        self._messages[timestamp]=mess
        self._messages_mutex.release()

        # Check wether is an offline action
        if not self._running:
            if mess.getName() == "iq":
                # Check if it's an offline disco info request
                if mess.getAttr("type") == "get":
                    q = mess.getTag("query")
                    if q and q.getNamespace() == NS_DISCO_INFO:
                        self.DEBUG("DISCO Behaviour called (offline)","info")
                        # Inform of services
                        reply = mess.buildReply("result")
                        if self.p2p_ready:
                            reply.getTag("query").addChild("feature", {"var":"http://jabber.org/protocol/si"})
                            reply.getTag("query").addChild("feature", {"var":"http://jabber.org/protocol/si/profile/spade-p2p-messaging"})
                        self.send(reply)
                        if raiseFlag: raise xmpp.NodeProcessed
                        return True
                # Check if it's an offline stream initiation request
                if mess.getAttr("type") == "set":
                    q = mess.getTag("si")
                    if q:
                        if mess.getType() == "set":
                            if mess.getTag("si").getAttr("profile") == "http://jabber.org/protocol/si/profile/spade-p2p-messaging":
                                # P2P Messaging Offer
                                if self.p2p_ready:
                                    # Take note of sender's p2p address if any
                                    if mess.getTag("si").getTag("p2p"):
                                        remote_address = str(mess.getTag("si").getTag("p2p").getData())
                                        d = {"url":remote_address, "p2p":True}
                                        self.p2p_lock.acquire()
                                        if self.p2p_routes.has_key(str(mess.getFrom().getStripped())):
                                            self.p2p_routes[str(mess.getFrom().getStripped())].update(d)
                                            if self.p2p_routes[str(mess.getFrom().getStripped())].has_key("socket"):
                                                self.p2p_routes[str(mess.getFrom().getStripped())]["socket"].close()
                                        else:
                                            self.p2p_routes[str(mess.getFrom().getStripped())] = d
                                        self.p2p_lock.release()

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
                                self.send(reply)
                                if raiseFlag: raise xmpp.NodeProcessed
                                return True

        self.DEBUG("Posting message " + str(mess), "info", "msg")
        self.postMessage(mess)
        if raiseFlag: raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
        return True


    def _other_messageCB(self, conn, mess):
        """
        non jabber:x:fipa chat messages callback
        """
        pass
        
    def _jabber_iqCB(self, conn, mess):
        """
        IQ callback
        manages jabber stanzas of the 'iq' protocol
        """
        # We post every jabber iq
        self.postMessage(mess)
        self.DEBUG("Jabber Iq posted to agent " + str(self.getAID().getName()),"info")


    def getAID(self):
        """
        returns AID
        """
        return self._aid

    def setAID(self, aid):
        """
        sets a new AID
        """
        self._aid = aid

    def addAddress(self, addr):
        self._aid.addAddress(addr)

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
        return str("spade://"+socket.gethostbyname(socket.gethostname())+":"+str(self.P2PPORT))


    def requestDiscoInfo(self, to):
        
        self.DEBUG("Request Disco Info called by " + str(self.getName()))
        rdif = P2P.RequestDiscoInfoBehav(to)
        t = Behaviour.MessageTemplate(rdif.temp_iq)
        if self._running:
            # Online way
            self.DEBUG("Request Disco Info ONLINE", "info")
            self.addBehaviour(rdif, t)
            rdif.join()
            return rdif.result
        else:
            # Offline way
            self.DEBUG("Request Disco Info OFFLINE", "info")
            self.runBehaviourOnce(rdif, t)
            return rdif.result


    def initiateStream(self, to):
        """
        Perform a Stream Initiation with another agent
        in order to stablish a P2P communication channel
        """


        self.DEBUG("Initiate Stream called by " + str(self.getName()))
        # First deal with Disco Info request
        services = self.requestDiscoInfo(to)
        if "http://jabber.org/protocol/si/profile/spade-p2p-messaging" in services:

            sib = P2P.SendStreamInitiationBehav(to)
            t = Behaviour.MessageTemplate(sib.temp_iq)

            if self._running:
                # Online way
                self.addBehaviour(sib, t)
                sib.join()
                return sib.result
            else:
                # Offline way
                self.DEBUG("Initiate Stream OFFLINE","warn")
                self.runBehaviourOnce(sib,t)
                return sib.result


    def send(self, ACLmsg, method="jabber"):
        """
        sends an ACLMessage
        """
        self._messages_mutex.acquire()
        timestamp = time.time()
        self._messages[timestamp]=ACLmsg
        self._messages_mutex.release()
        
        #if it is a jabber Iq or Presence message just send it
        if isinstance(ACLmsg,xmpp.Iq) or isinstance(ACLmsg,xmpp.Presence) or isinstance(ACLmsg,xmpp.Message):
            self.jabber.send(ACLmsg)
            return
        
        ACLmsg._attrs.update({"method":method})
        # Check for the sender field!!! (mistake #1)
        if not ACLmsg.getSender():
            ACLmsg.setSender(self.getAID())

        self._sendTo(ACLmsg, ACLmsg.getReceivers(), method=method.strip())

    def _sendTo(self, ACLmsg, tojid, method):
        """
        sends an ACLMessage to a specific JabberID
        """
        
        #First, try Ultra-Fast(tm) python cPickle way of things
        try:
            if method in ["auto", "p2ppy"]:
                remaining = copy.copy(tojid)
                for receiver in tojid:
                    to = None
                    for address in receiver.getAddresses():
                        #Get a jabber address
                        if "xmpp://" in address:
                            to = address.split("://")[1]
                            break
                    if to and self.send_p2p(None, to, method="p2ppy", ACLmsg=ACLmsg):
                        #The Ultra-Fast(tm) way worked. Remove this receiver from the remaining receivers
                        remaining.remove(receiver)

                tojid = remaining
                if not tojid:
                    #There is no one left to send the message to
                    return
        except Exception, e:
            self.DEBUG("Could not send through P2PPY: "+str(e), "warn")
            method = "jabber"

        # Second, try it the old way
        xenv = xmpp.protocol.Node('jabber:x:fipa x')
        envelope = Envelope.Envelope()
        generate_envelope = False
        #If there is more than one address in the sender or
        #the only address is not an xmpp address,
        #we need the full sender AID field
        try:
            if len(ACLmsg.getSender().getAddresses()) > 1 or \
                "xmpp" not in ACLmsg.getSender().getAddresses()[0]:
                envelope.setFrom(ACLmsg.getSender())
                generate_envelope = True
        except Exception, e:
            self.DEBUG("Error setting sender: "+ str(e), "err")

        try:
            for i in ACLmsg.getReceivers():
                #For every receiver,
                #if there is more than one address in the receiver or
                #the only address is not an xmpp address,
                #we need the full receiver AID field
                if len(i.getAddresses()) > 1 or \
                    "xmpp" not in i.getAddresses()[0]:
                    envelope.addTo(i)
                    generate_envelope = True
        except Exception, e:
            self.DEBUG("Error setting receivers: " + str(e),"err")


        try:
            #The same for 'reply_to'
            for i in ACLmsg.getReplyTo():
                #For every receiver,
                #if there is more than one address in the receiver or
                #the only address is not an xmpp address,
                #we need the full receiver AID field
                if len(i.getAddresses()) > 1 or \
                    "xmpp" not in i.getAddresses()[0]:
                    envelope.addIntendedReceiver(i)
                    generate_envelope = True
        except Exception, e:
            self.DEBUG("Error setting reply-to: " + str(e),"err")

        #Generate the envelope ONLY if it is needed
        if generate_envelope:
            xc = XMLCodec.XMLCodec()
            envxml = xc.encodeXML(envelope)
            xenv['content-type']='fipa.mts.env.rep.xml.std'
            xenv.addChild(node=simplexml.NodeBuilder(envxml).getDom())

        #For each of the receivers, try to send the message
        for to in tojid:
            isjabber = False
            for address in to.getAddresses():
                if "xmpp://" in address:
                    #If there is a jabber address for this receiver, send the message directly to it
                    jabber_id = address.split("://")[1]
                    isjabber = True
                    break
            if isjabber and str(self.getDomain()) in jabber_id:
                jabber_msg = xmpp.protocol.Message(jabber_id, xmlns="")
                jabber_msg.attrs.update(ACLmsg._attrs)
                jabber_msg.addChild(node=xenv)
                jabber_msg["from"]=self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())
            else:
                #I don't understand this address, relay the message to the platform
                jabber_msg = xmpp.protocol.Message(self.getSpadePlatformJID(), xmlns="")
                jabber_id = self.getSpadePlatformJID()
                jabber_msg.attrs.update(ACLmsg._attrs)
                jabber_msg.addChild(node=xenv)
                jabber_msg["from"]=self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())

            if (not self._running and method=="auto") or method=="jabber":
                self.jabber.send(jabber_msg)
                continue

            #If the receiver is one of our p2p contacts, send the message through p2p.
            #If it's not or it fails, send it through the jabber server
            #We suppose method in ['p2p']
            jabber_id = xmpp.JID(jabber_id).getStripped()

            if self.p2p_ready:
                sent = False
                self.p2p_send_lock.acquire()
                try:
                    sent = self.send_p2p(jabber_msg, jabber_id, method=method, ACLmsg=ACLmsg)
                except Exception, e:
                    self.DEBUG("P2P Connection to "+str(self.p2p_routes)+jabber_id+" prevented. Falling back. "+str(e), "warn")
                    sent = False
                self.p2p_send_lock.release()
                if not sent:
                    #P2P failed, try to send it through jabber
                    self.DEBUG("P2P failed, try to send it through jabber","warn")
                    jabber_msg.attrs.update({"method":"jabber"})
                    if method in ["auto","p2p","p2ppy"]: self.jabber.send(jabber_msg)

            else:
                #P2P is not available / not supported
                #Try to send it through jabber
                self.DEBUG("P2P is not available/supported, try to send it through jabber","warn")
                jabber_msg.attrs.update({"method":"jabber"})
                if method in ["auto","p2p","p2ppy"]: self.jabber.send(jabber_msg)


    def send_p2p(self, jabber_msg=None, to="", method="p2ppy", ACLmsg=None):

        #If this agent supports P2P, wait for P2PBEhaviour to properly start
        if self.p2p:
            while not self.p2p_ready:
                time.sleep(0.1)
        else:
            # send_p2p should not be called in a P2P-disabled agent !
            self.DEBUG("This agent does not support sending p2p messages", "warn")
            return False

        #Get the address
        if not to:
            if not jabber_msg:
                return False
            else:
                to = str(jabber_msg.getTo())
        if jabber_msg:
            self.DEBUG("Trying to send Jabber msg through P2P")
        elif ACLmsg:
            self.DEBUG("Trying to send ACL msg through P2P")
            
            
        try:
            #Try to get the contact's url
            url = self.p2p_routes[to]["url"]
        except:
            #The contact is not in our routes
            self.DEBUG("P2P: The contact " + str(to) + " is not in our routes. Starting negotiation","warn")
            self.initiateStream(to)
            if self.p2p_routes.has_key(to) and self.p2p_routes[to].has_key('p2p'):
                #If this p2p connection is marked as faulty,
                #check if enough time has passed to try again a possible p2p connection
                if self.p2p_routes[to]['p2p'] == False:
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
                        self.DEBUG("P2P: The p2p connection is really faulty","warn")
                        return False
                url = self.p2p_routes[to]["url"]
            else:
                #There is no p2p for this contact
                self.DEBUG("P2P: There is no p2p support for this contact","warn")
                return False


        #Check if there is already an open socket
        s = None
        if self.p2p_routes[to].has_key("socket"):
            s = self.p2p_routes[to]["socket"]
        if not s:
            #Parse url
            scheme, address = url.split("://",1)
            if scheme == "spade":
                #Check for address and port number
                l = address.split(":",1)
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
                        self.DEBUG("Error opening p2p socket " +'\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip(),"err")

            if not connected:
                self.DEBUG("Socket creation failed","warn")
                return False

        #Send length + message
        sent = False
        tries = 2
        while not sent and tries > 0:
            try:
                if method in ["p2p","auto"]:
                    jabber_msg.attrs.update({"method":"p2p"})
                    length = "%08d"%(len(str(jabber_msg)))
                    #Send message through socket
                    s.send(length+str(jabber_msg))
                    self.DEBUG("P2P message sent through p2p","ok")
                elif method in ["p2ppy"]:
                    ACLmsg._attrs.update({"method":"p2ppy"})
                    ser = pickle.dumps(ACLmsg)
                    length = "%08d"%(len(str(ser)))
                    s.send(length+ser)
                    self.DEBUG("P2P message sent through p2ppy","ok")
                sent = True

            except Exception, e:
                self.DEBUG("Socket: send failed, threw an exception: " +str(e), "err")
                self._p2p_failures += 1
                # Dispose of old socket
                self.p2p_lock.acquire()
                s.close()
                try:
                    del s
                    del self.p2p_routes[to]["socket"]
                except: pass
                self.p2p_lock.release()
                #Get address and port AGAIN
                scheme, address = url.split("://",1)
                if scheme == "spade":
                    #Check for address and port number
                    l = address.split(":",1)
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
            self.DEBUG("Socket send failed","warn")
            self.p2p_lock.acquire()
            self.p2p_routes[to]["p2p"] = False
            self.p2p_routes[to]["failed_time"] = time.time()
            self.p2p_lock.release()
            return False
        else:
            return True

    def _kill(self):
        """
        kills the agent
        """
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

	self.wui.stop()

        self._kill()
        if timeout > 0:
            to = time.now() + timeout
            while self._alive and time.now() < to:
                time.sleep(0.1)
        #No timeout (true blocking)
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
        self.behavioursGo.acquire()
        self._running = True
        self.behavioursGo.notifyAll()
        self.behavioursGo.release()

        #Start the Behaviours
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.start()

        #If this agent supports P2P, wait for P2PBEhaviour to properly start
        if self.p2p:
            while not self.p2p_ready:
                time.sleep(0.1)

        #############
        # Main Loop #
        #############
        while not self.forceKill():
            try:
                #Check for queued messages
                proc = False
                toRemove = []  # List of EventBehaviours to remove after this pass
                msg = self._receive(block=True, timeout=0.01)
                if msg != None:
                    bL = copy.copy(self._behaviourList)
                    for b in bL:
                        t = bL[b]
                        if (t != None):
			    if (t.match(msg) == True):
                                if ((b == types.ClassType or type(b) == types.TypeType) and issubclass(b, Behaviour.EventBehaviour)):
                                    ib = b()
                                    if ib.onetime:
                                        toRemove.append(b)
                                    ib.setAgent(self)
                                    ib.postMessage(msg)
                                    ib.start()
                                else:
                                    b.postMessage(msg)
                                proc = True

                    if (proc == False):
                        #If no template matches, post the message to the Default behaviour
                        self.DEBUG("Message was not reclaimed by any behaviour. Posting to default behaviour: " + str(msg) + str(bL), "warn", "msg")
                        if (self._defaultbehaviour != None):                            
                            self._defaultbehaviour.postMessage(msg)
                    for beh in toRemove:
                        self.removeBehaviour(beh)

            except Exception, e:
                self.DEBUG("Agent " + self.getName() + "Exception in run:" + str(e), "err")
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
            #Event behaviour do not start inmediately
            self._behaviourList[behaviour] = copy.copy(template)
            behaviour.setAgent(self)
            behaviour.start()
        else:
            self.DEBUG("Adding Event Behaviour "+str(behaviour.__class__))
            self._behaviourList[behaviour.__class__] = copy.copy(template)

    def runBehaviourOnce(self, behaviour,template=None):
        """
        Runs the behaviour offline
        Executes its process once
        @warning Only for OneShotBehaviour
        """
        if not issubclass(behaviour.__class__, Behaviour.OneShotBehaviour):
            self.DEBUG("Only OneShotBehaviour execution is allowed offline","err")
            return False
            
        if not self._running:
            try:
                behaviour._receive = self._receive
                behaviour.onStart()
                behaviour._process()
                behaviour.onEnd()
                del behaviour
                return True
            except:
                self.DEBUG("Failed the execution of the OFFLINE behaviour "+str(behaviour),"err")
                return False
        else:
            self.addBehaviour(behaviour,template)


    def removeBehaviour(self, behaviour):
        """
        removes a behavior from the agent
        """
        if (type(behaviour) not in [types.ClassType,types.TypeType]) and (not issubclass(behaviour.__class__, Behaviour.EventBehaviour)):
            behaviour.kill()
        try:
            self._behaviourList.pop(behaviour)
            self.DEBUG("Behaviour removed: " + str(behaviour), "info", "behaviour")
        except KeyError:
            self.DEBUG("removeBehaviour: Behaviour " + str(behaviour) +"with type " +str(type(behaviour))+ " is not registered in "+str(self._behaviourList),"warn")


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
        self.send(iq)
        if not nowait:
            while self._waitingForRoster:
                time.sleep(0.3)
            return self._roster


    ##################
    # FIPA procedures #
    ##################
    
    def searchAgent(self, AAD):
        """
        searches an agent in the AMS
        the search template is an AmsAgentDescription class
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.SearchAgentBehaviour(msg, AAD)

        self.addBehaviour(b,t)
        b.join()
        return b.result



    def modifyAgent(self, AAD):
        """
        modifies the AmsAgentDescription of an agent in the AMS
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.ModifyAgentBehaviour(msg, AAD)

        self.addBehaviour(b,t)
        b.join()
        return b.result



    def getPlatformInfo(self):
        """
        returns the Plarform Info
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.getPlatformInfoBehaviour(msg)

        self.addBehaviour(b,t)
        b.join()
        return b.result



    def registerService(self, service, methodCall=None, otherdf=None):
        """
        registers a service in the DF
        the service template is a DfAgentDescriptor
        """
        
        if isinstance(service,DF.Service): DAD=service.getDAD()
        else: DAD = service
        
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        if otherdf and isinstance(otherdf, AID.aid):
            template.setSender(otherdf)
        else:
            template.setSender(self.getDF())
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.registerServiceBehaviour(msg=msg, DAD=DAD, otherdf=otherdf)
        if self._running:
            # Online
            self.addBehaviour(b,t)
            b.join()
        else:
            self.runBehaviourOnce(b,t)

        if methodCall and b.result==True:
            if not isinstance(service,DF.Service):
                self.DEBUG("Could not register RPC Service. It's not a DF.Service class","error")
                return False

            name = service.getName()
            self.DEBUG("Registering RPC service "+ name)
            self.RPC[name.lower()] = (service, methodCall)
            
        return b.result


    def deregisterService(self, DAD, otherdf=None):
        """
        deregisters a service in the DF
        the service template is a DfAgentDescriptor
        """

        if self.RPC.has_key(DAD.getName()):
            del self.RPC[DAD.getName()]

        if isinstance(DAD,DF.Service):
            DAD=DAD.getDAD()
        
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        if otherdf and isinstance(otherdf, AID.aid):
            template.setSender(otherdf)
        else:
            template.setSender(self.getDF())

        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.deregisterServiceBehaviour(msg=msg, DAD=DAD, otherdf=otherdf)
        if self._running:
            # Online
            self.addBehaviour(b,t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b,t)
            return b.result


    def searchService(self, DAD):
    	"""
    	search a service in the DF
    	the service template is a DfAgentDescriptor

    	"""
    	if isinstance(DAD,DF.Service):
            DAD=DAD.getDAD()
            returnDAD=False
        else: returnDAD=True
    	
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.searchServiceBehaviour(msg, DAD)
        if self._running:
            self.addBehaviour(b,t)
            b.join()
        else:
            self.runBehaviourOnce(b,t)


        if b.result==None: return None
        if returnDAD: return b.result
        else:
            r = []
            for dad in b.result:
                for sd in  dad.getServices():
                    s=DF.Service()
                    if sd.getName(): s.setName(sd.getName())
                    if dad.getAID(): s.setOwner(dad.getAID())
                    for o in sd.getOntologies(): s.setOntology(o)
                    if sd.getProperty("description"): s.setDescription(sd.getProperty("description"))
                    if sd.getProperty("inputs"): s.setInputs(sd.getProperty("inputs"))
                    if sd.getProperty("outputs"): s.setOutputs(sd.getProperty("outputs"))
                    if sd.getProperty("P"):
                        for p in sd.getProperty("P"): s.addP(p)
                    if sd.getProperty("Q"): s.setQ(sd.getProperty("Q"))
                    r.append(s)
            return r


		
    def modifyService(self, DAD, methodCall=None):
        """
        modifies a service in the DF
        the service template is a DfAgentDescriptor
        """

        if methodCall:
            if not isinstance(DAD,DF.Service):
                self.DEBUG("Could not modify RPC Service. It's not a DF.Service class","error")
                return False

            self.RPC[DAD.getName()] = (DAD, methodCall)
        
        if isinstance(DAD,DF.Service):
            DAD=DAD.getDAD()
        
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = fipa.modifyServiceBehaviour(msg, DAD)

        if self._running:
            # Online
            self.addBehaviour(b,t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b,t)
            return b.result

    def invokeService(self, service):
        """
        invokes a service using jabber-rpc (XML-RPC)
        the service template is a DF.Service
        """

        if not isinstance(service,DF.Service):
            self.DEBUG("Service MUST be a DF.Service instance",'error')
            return False

        num = str(random.getrandbits(32))
        b = RPC.RPCClientBehaviour(service,num)
        t  = Behaviour.MessageTemplate(Iq(typ='result',queryNS="jabber:iq:rpc",attrs={'id':num}))
        t2 = Behaviour.MessageTemplate(Iq(typ='error',queryNS="jabber:iq:rpc",attrs={'id':num}))

        if self._running:
            # Online
            self.addBehaviour(b,t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b,t)
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
		    except Exception, e:
			_exception = sys.exc_info()
			if _exception[0]:
			    self._owner.DEBUG( '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip(),"err")
			    self._owner.DEBUG("Exception in jabber process: "+ str(e),"err")
			    self._owner.DEBUG("Jabber connection failed: "+self._owner.getAID().getName()+" (dying)","err")
			    self._kill()
			    self._owner.stop()
			    err = None

		    if err == None or err == 0:  # None or zero the integer, socket closed
			self._owner.DEBUG("Agent disconnected: "+self._owner.getAID().getName()+" (dying)","err")
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
        if not self._register(password):
            self._shutdown()

    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        tries = 5
        while not self.jabber.connect() and tries >0:
              time.sleep(0.005)
              tries -=1
        if tries <= 0:
            self.DEBUG("The agent could not connect to the platform "+ str(self.getDomain()),"err")
            return False


        if (self.jabber.auth(name=name,password=password) == None):
              raise NotImplementedError

        self.jabber.RegisterHandler('message',self._jabber_messageCB)
        self.jabber.RegisterHandler('presence',self._jabber_messageCB)
        self.jabber.RegisterHandler('iq',self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence',self._jabber_presenceCB)
        #self.jabber.RegisterHandler('iq',self._jabber_iqCB)

        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()
        return True

    def _shutdown(self):

        self._kill()  # Doublecheck death
        self.jabber_process._kill()

        #Stop the Behaviours
        for b in self._behaviourList:
            try:
                b.kill()
            except:
                pass
                
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.kill()
        #DeInit the Agent
        self.takeDown()

        self._alive = False

class Agent(AbstractAgent):
    """
    This is the main class which may be inherited to build a SPADE agent
    """


    def __init__(self, agentjid, password, port=5222, debug=[], p2p=False):
        jid = xmpp.protocol.JID(agentjid)
        self.server = jid.getDomain()
        self.port = port
        self.debug = debug
        AbstractAgent.__init__(self, agentjid, jid.getDomain(),p2p=p2p)
        
        self.jabber = xmpp.Client(jid.getDomain(), port, debug)

        # Try to register
        try:
            self.DEBUG("Trying to register agent " + agentjid)
            if not self._register(password):
                self.stop()
        except NotImplementedError:
            self.DEBUG("NotImplementedError: Could not register agent %s"%(agentjid),"err")
            self.stop()
            return
        except:
            self.DEBUG("Could not register agent %s"%(agentjid),"err")
            self.stop()
            return

        # Add Presence Control Behaviour
        self.addBehaviour(socialnetwork.PresenceBehaviour(), Behaviour.MessageTemplate(Presence()))

        # Add Roster Behaviour
        self.addBehaviour(socialnetwork.RosterBehaviour(), Behaviour.MessageTemplate(Iq(queryNS=NS_ROSTER)))

        self.DEBUG("Agent %s registered"%(agentjid),"ok")

        if not self.__register_in_AMS():
            self.DEBUG("Agent " + str(self.getAID().getName()) + " dying ...","err")
            self.stop()

        # Ask for roster
        ##self.getSocialNetwork(nowait=True)

    def setSocialItem(self, jid, presence=""):
        if self._socialnetwork.has_key(jid):
            if not self._socialnetwork[jid].getPresence():
                # If we have no previous presence information, update it
                self._socialnetwork[jid].setPresence(presence)
        else:
            self._socialnetwork[jid] = socialnetwork.SocialItem(self, jid, presence)


    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()


        tries = 5
        while not self.jabber.connect(use_srv=None) and tries >0:
            time.sleep(0.005)
            tries -=1
        if tries <=0 :
            self.setDebugToScreen()
            self.DEBUG("There is no SPADE platform at " + self.server + " . Agent dying...","err")
            return False


        if (self.jabber.auth(name,password,"spade") == None):

            self.DEBUG("First auth attempt failed. Trying to register","warn")

            if (autoregister == True):
                xmpp.features.getRegInfo(self.jabber,jid.getDomain())
                xmpp.features.register(self.jabber,jid.getDomain(),\
                {'username':name, 'password':str(password), 'name':name})


                if not self.jabber.reconnectAndReauth():
                    self.DEBUG("Second auth attempt failed (username="+str(name)+")", "err")
                    return False
            else:
                    return False

        self.DEBUG("Agent %s got authed"%(self._aid.getName()),"ok")

        self.jabber.RegisterHandler('message',self._jabber_messageCB)
        self.jabber.RegisterHandler('presence',self._jabber_messageCB)
        self.jabber.RegisterHandler('iq',self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence',self._jabber_presenceCB)

        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()

        # Request roster and send initial presence
        #self.getSocialNetwork()

        self.jabber.sendInitPresence()
        
        return True


    def _shutdown(self):
        #Stop the Behaviours
        for b in copy.copy(self._behaviourList):
            try:
                b.kill()
                if "P2PBehaviour" in str(b.__class__):
                    b.onEnd()
            except:
                pass

        if (self._defaultbehaviour != None):
            self._defaultbehaviour.kill()

        #DeInit the Agent
        self.takeDown()

        if self._alivemutex.testandset():
            if not self.jabber_process.forceKill():
                if not self.__deregister_from_AMS():
                    self.DEBUG("Agent " + str(self.getAID().getName()) + " dying without deregistering itself ...","err")
                self.jabber_process._kill()  # Kill jabber thread
            self._alive = False
        self._alivemutex.unlock()

        self._kill()  # Doublecheck death



    def __register_in_AMS(self, state='active', ownership=None, debug=False):
        # Let's change it to "subscribe"
        presence = xmpp.Presence(to=self.getAMS().getName(),frm=self.getName(),typ='subscribe')

        self.send(presence)

        self.DEBUG("Agent: " + str(self.getAID().getName()) + " registered correctly (inform)","ok")
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
            self.DEBUG("There was an error initiating the register of agent: " + str(self.getAID().getName()) + " (refuse)","err")
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " initiating registering process (agree)")
        else:
            # There was no answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error initiating the register of agent: " + str(self.getAID().getName()),"err")
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (msg.getPerformative() == 'failure'):
            self.DEBUG("There was an error with the register of agent: " + str(self.getAID().getName()) + " (failure)","err")
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " registered correctly (inform)","ok")
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error with the register of agent: " + str(self.getAID().getName()),"err")
            return False

        return True


    def __deregister_from_AMS(self, state=None, ownership=None, debug=False):

        presence = xmpp.Presence(to=self.getAMS().getName(),frm=self.getName(),typ='unsubscribe')

        self.send(presence)
        self.DEBUG("Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)","ok")

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
            self.DEBUG("There was an error initiating the deregister of agent: " + str(self.getAID().getName()) + " (refuse)","err")
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " initiating deregistering process (agree)")
        else:
            # There was no answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error deregistering of agent: " + str(self.getAID().getName()),"err")
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True,20)
        if (msg != None) and (msg.getPerformative() == 'failure'):
            self.DEBUG("There was an error with the deregister of agent: " + str(self.getAID().getName()) + " (failure)","err")
            return False
        elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)","ok")
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error with the deregister of agent: " + str(self.getAID().getName()),"err")
            return False

        return True
