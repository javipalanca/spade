# -*- coding: utf-8 -*-

try:
    import psyco
    psyco.full()
except ImportError:
    pass  # self.DEBUG("Psyco optimizing compiler not found","warn")

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
import pubsub
import bdi
from logic import *
from kb import *

import mutex
import types
import random
import string
import copy
import socket
import SocketServer
import colors
import cPickle as pickle
import uuid
try:
    import json
except ImportError:
    import simplejson as json 


import DF
from content import ContentObject
from wui import *

from xmpp import *

# Taken from xmpp debug
color_none = chr(27) + "[0m"
color_black = chr(27) + "[30m"
color_red = chr(27) + "[31m"
color_green = chr(27) + "[32m"
color_brown = chr(27) + "[33m"
color_blue = chr(27) + "[34m"
color_magenta = chr(27) + "[35m"
color_cyan = chr(27) + "[36m"
color_light_gray = chr(27) + "[37m"
color_dark_gray = chr(27) + "[30;1m"
color_bright_red = chr(27) + "[31;1m"
color_bright_green = chr(27) + "[32;1m"
color_yellow = chr(27) + "[33;1m"
color_bright_blue = chr(27) + "[34;1m"
color_purple = chr(27) + "[35;1m"
color_bright_cyan = chr(27) + "[36;1m"
color_white = chr(27) + "[37;1m"

try:
    threading.stack_size(64 * 1024)  # 64k compo
except:
    pass


def require_login(func):
    '''decorator for requiring login in wui controllers'''
    self = func.__class__

    def wrap(self, *args, **kwargs):
        if (not hasattr(self.session, "user_authenticated") or getattr(self.session, "user_authenticated") is False) and self.wui.passwd is not None:
            name = self.getName().split(".")[0].upper()
            if name == "ACC":
                name = "SPADE"
            return "login.pyra", {"name": name, 'message': "Authentication is required.", "forward_url": self.session.url}
        return func(self, *args, **kwargs)
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


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
        self._agent_log = []  # Log system
        self._aid = AID.aid(name=agentjid, addresses=["xmpp://" + agentjid])
        self._jabber = None
        self._serverplatform = serverplatform
        self.server = serverplatform
        self._defaultbehaviour = None
        self._behaviourList = dict()
        self._alive = True
        self._alivemutex = mutex.mutex()
        self._forceKill = threading.Event()
        self._forceKill.clear()
        self.JID = agentjid
        self.setName(str(agentjid))

        self._debug = False
        self._debug_filename = ""
        self._debug_file = None
        self._debug_mutex = thread.allocate_lock()

        self._messages = []
        self._messages_mutex = thread.allocate_lock()

        self.wui = WUI(self)
        self.wui.registerController("index", self.WUIController_admin)
        self.wui.registerController("login", self.WUIController_login)
        self.wui.registerController("logout", self.WUIController_logout)
        self.wui.registerController("admin", self.WUIController_admin)
        self.wui.registerController("log", self.WUIController_log)
        self.wui.registerController("messages", self.WUIController_messages)
        self.wui.registerController("search", self.WUIController_search)
        self.wui.registerController("send", self.WUIController_sendmsg)
        self.wui.registerController("sent", self.WUIController_sent)
        self.wui.registerController("roster", self.WUIController_roster)
        self.wui.passwd = None

        self._aclparser = ACLParser.ACLxmlParser()

        #self._socialnetwork = {}
        self._subscribeHandler = lambda frm, typ, stat, show: False
        self._unsubscribeHandler = lambda frm, typ, stat, show: False

        #PubSub
        self._pubsub = pubsub.PubSub(self)
        self._events = {}

        #Knowledge base
        self.kb = KB()  # knowledge base

        self._waitingForRoster = False  # Indicates that a request for the roster is in progress

        self.behavioursGo = threading.Condition()  # Condition to synchronise behaviours
        self._running = False

        # Peer2Peer messaging support
        self._P2P = P2P.P2P(self, p2p)

        # Remote Procedure Calls support
        self.RPC = {}
        self._RPC = RPC.RPC(self)

    def setAdminPasswd(self, passwd):
        self.wui.passwd = str(passwd)

    def WUIController_login(self, password=None, forward_url="index"):
        if hasattr(self.session, "user_authenticated") and getattr(self.session, "user_authenticated") is True:
            raise HTTP_REDIRECTION('index')

        name = self.getName().split(".")[0].upper()
        if name == "ACC":
            name = "SPADE"

        if password is None:
            return "login.pyra", {"name": name, "message": "Authentication is required.", "forward_url": forward_url}
        if password != self.wui.passwd:
            return "login.pyra", {"name": name, "message": "Password is incorrect. Try again.", "forward_url": forward_url}

        else:
            setattr(self.session, "user_authenticated", True)
            raise HTTP_REDIRECTION(forward_url)

    def WUIController_logout(self):
        if hasattr(self.session, "user_authenticated"):
            delattr(self.session, "user_authenticated")
        raise HTTP_REDIRECTION("index")

    @require_login
    def WUIController_admin(self):
        behavs = {}
        attrs = {}
        sorted_attrs = []
        for k in self._behaviourList.keys():
            behavs[id(k)] = k
        for attribute in self.__dict__:
            if eval("type(self." + attribute + ") not in [types.MethodType, types.BuiltinFunctionType, types.BuiltinMethodType, types.FunctionType]"):
                if attribute not in ["_agent_log", "_messages"]:
                    attrs[attribute] = eval("str(self." + attribute + ")")
        sorted_attrs = attrs.keys()
        sorted_attrs.sort()
        import pygooglechart
        chart = pygooglechart.QRChart(125, 125)
        chart.add_data(self.getAID().asXML())
        chart.set_ec('H', 0)
        return "admin.pyra", {"name": self.getName(), "aid": self.getAID(), "qrcode": chart.get_url(), "defbehav": (id(self._defaultbehaviour), self._defaultbehaviour), "behavs": behavs, "p2pready": self._P2P.isReady(), "p2proutes": self._P2P.getRoutes(), "attrs": attrs, "sorted_attrs": sorted_attrs}

    @require_login
    def WUIController_log(self):
        return "log.pyra", {"name": self.getName(), "log": self.getLog()}

    @require_login
    def WUIController_roster(self):
        roster = {}
        for friend in self.roster.getContacts():
            if friend == self.getName():
                continue
            roster[friend] = self.roster.getContact(friend)
        return "agent_roster.pyra", {"name": self.getName(), "roster": roster}

    @require_login
    def WUIController_messages(self, agents=None):
        index = 0
        mess = {}
        msc = ""
        agentslist = []
        for ts, m in self._messages:
            if isinstance(m, ACLMessage.ACLMessage):
                strm = self._aclparser.encodeXML(m)
                x = xml.dom.minidom.parseString(strm)
                #strm = x.toprettyxml()
                strm = m.asHTML()
                frm = m.getSender().getName()
                if frm is None or frm is "":
                    frm = "Unknown"
                else:
                    frm = str(frm).split("/")[0].split("@")[0].split(".")[0]
                r = m.getReceivers()
                if len(r) >= 1:
                    to = r[0].getName()
                    to = to.split("/")[0].split("@")[0].split(".")[0]
                else:
                    to = "Unknown"
                if to is "":
                    to = "Unknown"
                if agents:
                    if to in agents or frm in agents:
                        msc += frm + "->" + to + ':' + str(index) + " " + str(m.getPerformative()) + '\n'
                else:
                    msc += frm + "->" + to + ':' + str(index) + " " + str(m.getPerformative()) + '\n'
            else:
                strm = str(m)
                """strm = strm.replace("&gt;",">")
                strm = strm.replace("&lt;","<")
                strm = strm.replace("&quot;",'"')"""
                x = xml.dom.minidom.parseString(strm)
                strm = x.toprettyxml()
                # Quick'n dirty hack to display jabber messages on the WUI
                # Will fix with a proper display
                strm = strm.replace(">", "&gt;")
                strm = strm.replace("<", "&lt;")
                strm = strm.replace('"', "&quot;")
                frm = m.getFrom().getNode()
                if frm is None or frm is "":
                    frm = "Unknown"
                else:
                    frm = str(frm).split("/")[0].split("@")[0].split(".")[0]
                to = m.getTo().getNode()
                if to is None or to is "":
                    to = "Unknown"
                else:
                    to = str(to).split("/")[0].split("@")[0].split(".")[0]
                if agents:
                    if to in agents or frm in agents:
                        msc += frm + "-->" + to + ':' + str(index) + ' ' + str(m.getName())
                        if m.getType():
                            msc += " " + str(m.getType()) + '\n'
                        elif m.getName() == "message":
                            if m.getAttr("performative"):
                                msc += " " + str(m.getAttr("performative")) + '\n'
                            else:
                                msc += '\n'
                        else:
                            msc += '\n'
                else:
                    msc += frm + "-->" + to + ':' + str(index) + ' ' + str(m.getName())
                    if m.getType():
                        msc += " " + str(m.getType()) + '\n'
                    elif m.getName() == "message":
                        if m.getAttr("performative"):
                            msc += " " + str(m.getAttr("performative")) + '\n'
                        else:
                            msc += '\n'
                    else:
                        msc += '\n'

            if frm not in agentslist:
                agentslist.append(frm)
            if to not in agentslist:
                agentslist.append(to)

            mess[index] = (ts, strm)
            index += 1

        return "messages.pyra", {"name": self.getName(), "messages": mess, "diagram": msc, "agentslist": agentslist}

    @require_login
    def WUIController_search(self, query):

        #FIRST SEARCH AGENTS
        from AMS import AmsAgentDescription
        agentslist = []

        #search by name
        aad = AmsAgentDescription()
        aad.setAID(AID.aid(name=query))
        res = self.searchAgent(aad)
        if res:
            agentslist += res

        #search by address
        aad = AmsAgentDescription()
        aad.setAID(AID.aid(addresses=[query]))
        res = self.searchAgent(aad)
        if res:
            for a in res:
                if not a in agentslist:
                    agentslist.append(a)

        #search by ownership
        aad = AmsAgentDescription()
        aad.setOwnership(query)
        res = self.searchAgent(aad)
        if res:
            for a in res:
                if not a in agentslist:
                    agentslist.append(a)

        #search by state
        aad = AmsAgentDescription()
        aad.setState(query)
        res = self.searchAgent(aad)
        if res:
            for a in res:
                if not a in agentslist:
                    agentslist.append(a)

        # Build AWUIs dict
        awuis = {}
        if agentslist:
            aw = ""
            for agent in agentslist:
                if agent.getAID():
                    aw = "#"
                    for addr in agent.getAID().getAddresses():
                        if "awui://" in addr:
                            aw = addr.replace("awui://", "http://")
                            break
                    awuis[agent.getAID().getName()] = aw
            self.DEBUG("AWUIs: " + str(awuis))

        #NOW SEARCH SERVICES
        from DF import Service, DfAgentDescription, ServiceDescription
        servs = {}

        #search by name
        s = Service(name=query)
        search = self.searchService(s)

        for service in search:
            if service.getDAD().getServices()[0].getType() not in servs.keys():
                servs[service.getDAD().getServices()[0].getType()] = []
            if service not in servs[service.getDAD().getServices()[0].getType()]:
                servs[service.getDAD().getServices()[0].getType()].append(service)

        #search by type
        s = Service()
        sd = ServiceDescription()
        sd.setType(query)
        dad = DfAgentDescription()
        dad.addService(sd)
        s.setDAD(dad)
        search = self.searchService(s)

        for service in search:
            if service.getDAD().getServices()[0].getType() not in servs.keys():
                servs[service.getDAD().getServices()[0].getType()] = []
            if service not in servs[service.getDAD().getServices()[0].getType()]:
                servs[service.getDAD().getServices()[0].getType()].append(service)

        #search by owner
        s = Service(owner=AID.aid(name=query))
        search = self.searchService(s)

        for service in search:
            if service.getDAD().getServices()[0].getType() not in servs.keys():
                servs[service.getDAD().getServices()[0].getType()] = []
            if service not in servs[service.getDAD().getServices()[0].getType()]:
                servs[service.getDAD().getServices()[0].getType()].append(service)

        #search by ontology
        s = Service()
        dad = DfAgentDescription()
        dad.addOntologies(query)
        dad.addService(sd)
        s.setDAD(dad)
        search = self.searchService(s)

        for service in search:
            if service.getDAD().getServices()[0].getType() not in servs.keys():
                servs[service.getDAD().getServices()[0].getType()] = []
            if service not in servs[service.getDAD().getServices()[0].getType()]:
                servs[service.getDAD().getServices()[0].getType()].append(service)

        #search by description
        '''s = Service()
        s.setDescription(query)
        search = self.searchService(s)

        for service in search:
                if service.getDAD().getServices()[0].getType() not in servs.keys():
                    servs[service.getDAD().getServices()[0].getType()] = []
                if service not in servs[service.getDAD().getServices()[0].getType()]:
                    print "found by description:" +str(service)
                    servs[service.getDAD().getServices()[0].getType()].append(service)'''

        return "search.pyra", {"name": self.getName(), "agentslist": agentslist, "awuis": awuis, "services": servs}

    @require_login
    def WUIController_sendmsg(self, to=None):
        from AMS import AmsAgentDescription
        agentslist = []
        aad = AmsAgentDescription()
        res = self.searchAgent(aad)
        if res is None:
            res = [self]
        for a in res:
            agentslist.append(a.getAID().getName())
        return "message.pyra", {"name": self.getName(), "keys": agentslist, "to": to}

    @require_login
    def WUIController_sent(self, receivers=[], performative=None, sender=None, reply_with=None, reply_by=None, reply_to=None, in_reply_to=None, encoding=None, language=None, ontology=None, protocol=None, conversation_id=None, content=""):
        msg = ACLMessage.ACLMessage()
        if isinstance(receivers, types.StringType):
            a = AID.aid(name=receivers, addresses=["xmpp://" + receivers])
            msg.addReceiver(a)
        elif isinstance(receivers, types.ListType):
            for r in receivers:
                a = AID.aid(name=r, addresses=["xmpp://" + r])
                msg.addReceiver(a)
        if performative:
            msg.setPerformative(performative)
        if sender:
            a = AID.aid(name=sender, addresses=["xmpp://" + sender])
            msg.setSender(a)
        if reply_to:
            msg.setReplyTo(reply_to)
        if reply_with:
            msg.setReplyWith(reply_with)
        if reply_by:
            msg.setReplyBy(reply_by)
        if in_reply_to:
            msg.setInReplyTo(in_reply_to)
        if encoding:
            msg.setEncoding(encoding)
        if language:
            msg.setLanguage(language)
        if ontology:
            msg.setOntology(ontology)
        if conversation_id:
            msg.setConversationId(conversation_id)
        if content:
            msg.setContent(content)

        self.send(msg)

        return "sentmsg.pyra", {"name": self.getName(), "msg": msg}

    def registerLogComponent(self, component):
        #self._agent_log[component] = {}
        pass

    def DEBUG(self, dmsg, typ="info", component="spade"):
        # Record at log
        t = time.ctime()
        dmsg = dmsg.replace("&gt;", ">")
        dmsg = dmsg.replace("&lt;", "<")
        dmsg = dmsg.replace("&quot;", '"')

        self._debug_mutex.acquire()
        self._agent_log.append((typ, dmsg, component, t))
        self._debug_mutex.release()

        if self._debug:
            # Print on screen
            if typ == "info":
                print colors.color_none + self.getName() +":[" + component + "] " + dmsg + " , info" + colors.color_none
            elif typ == "err":
                print colors.color_none + self.getName() + ":[" + component + "] " + color_red + dmsg + " , error" + colors.color_none
            elif typ == "ok":
                print colors.color_none + self.getName() + ":[" + component + "] " + colors.color_green + dmsg + " , ok" + colors.color_none
            elif typ == "warn":
                print colors.color_none + self.getName() + ":[" + component + "] " + colors.color_yellow + dmsg + " , warn" + colors.color_none

        # Log to file
        if self._debug_file:
            if typ == "info":
                self._debug_file.write(t + ": [" + component + "] " + dmsg + " , info\n")
            elif typ == "err":
                self._debug_file.write(t + ": [" + component + "] " + dmsg + " , error\n")
            elif typ == "ok":
                self._debug_file.write(t + ": [" + component + "] " + dmsg + " , ok\n")
            elif typ == "warn":
                self._debug_file.write(t + ": [" + component + "] " + dmsg + " , warn\n")
            self._debug_file.flush()

    def setDebug(self, activate=True):
        self.setDebugToScreen(activate)
        self.setDebugToFile(activate)

    def setDebugToScreen(self, activate=True):
        self._debug = activate
        if activate:
            self.jabber._DEBUG.active_set(['always'])
        else:
            self.jabber._DEBUG.active_set()

    def setDebugToFile(self, activate=True, fname=""):
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
        l = copy.copy(self._agent_log)
        l.reverse()
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

        children = mess.getTags(name='x', namespace='http://jabber.org/protocol/muc#user')
        for x in children:
            for item in x.getTags(name='item'):
                role = item.getAttr('role')
                affiliation = item.getAttr('affiliation')

        try:
            # Pass the FIPA-message to all the behaviours
            for b in self._behaviourList.keys():
                b.managePresence(frm, typ, status, show, role, affiliation)

            self._defaultbehaviour.managePresence(frm, typ, status, show, role, affiliation)
        except Exception, e:
            # There is not a default behaviour yet
            self.DEBUG(str(e), "err")

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
                # Clean
                    del ACLmsg._attrs["from"]
                except:
                    pass
                try:
                    # Clean
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
                        ACLmsg.setSender(AID.aid(str(mess.getFrom().getStripped()), ["xmpp://" + str(mess.getFrom().getStripped())]))
                    if envelope.getIntendedReceiver():
                        for ir in envelope.getIntendedReceiver():
                            ACLmsg.addReceiver(ir)
                    else:
                        ACLmsg.addReceiver(AID.aid(str(mess.getTo().getStripped()), ["xmpp://" + str(mess.getTo())]))
                else:
                    ACLmsg.setSender(AID.aid(str(mess.getFrom().getStripped()), ["xmpp://" + str(mess.getFrom().getStripped())]))
                    ACLmsg.addReceiver(AID.aid(str(mess.getTo().getStripped()), ["xmpp://" + str(mess.getTo().getStripped())]))

                self._messages_mutex.acquire()
                timestamp = time.time()
                self._messages.append((timestamp, ACLmsg))
                self._messages_mutex.release()
                self.postMessage(ACLmsg)
                if raiseFlag:
                    raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
                return True

        # Not a jabber-fipa message
        self._messages_mutex.acquire()
        timestamp = time.time()
        self._messages.append((timestamp, mess))
        self._messages_mutex.release()

        # Check wether is an offline action
        #if not self._running:
        #    if mess.getName() == "iq":
        #        print "IQ ARRIVED " + str(mess)

        self.DEBUG("Posting message " + str(mess), "info", "msg")
        self.postMessage(mess)
        if raiseFlag:
            raise xmpp.NodeProcessed  # Forced by xmpp.py for not returning an error stanza
        return True

    def _other_messageCB(self, conn, mess):
        """
        non jabber:x:fipa chat messages callback
        """
        self.DEBUG("Arrived an unknown message " + str(mess), "warn")
        self.postMessage(mess)

    def _jabber_iqCB(self, conn, mess):
        """
        IQ callback
        manages jabber stanzas of the 'iq' protocol
        """
        # We post every jabber iq
        ##self.postMessage(mess)
        ##self.DEBUG("Jabber Iq posted to agent " + str(self.getAID().getName()), "info")

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
        return AID.aid(name="ams." + self._serverplatform, addresses=["xmpp://ams." + self._serverplatform])

    def getDF(self):
        """
        returns the DF aid
        """
        return AID.aid(name="df." + self._serverplatform, addresses=["xmpp://df." + self._serverplatform])

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
        try:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        except:
            ip = "127.0.0.1"
        return str("spade://" + ip + ":" + str(self._P2P.getPort()))

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
                self.DEBUG("Initiate Stream OFFLINE", "warn")
                self.runBehaviourOnce(sib, t)
                return sib.result

    def send(self, ACLmsg, method="jabber"):
        """
        sends an ACLMessage
        """
        self._messages_mutex.acquire()
        timestamp = time.time()
        self._messages.append((timestamp, ACLmsg))
        self._messages_mutex.release()

        #if it is a jabber Iq or Presence message just send it
        if isinstance(ACLmsg, xmpp.Iq) or isinstance(ACLmsg, xmpp.Presence) or isinstance(ACLmsg, xmpp.Message):
            self.jabber.send(ACLmsg)
            return

        ACLmsg._attrs.update({"method": method})
        if ACLmsg.getAclRepresentation() is None:
            ACLmsg.setAclRepresentation(ACLMessage.FIPA_ACL_REP_XML)
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
                    if to and self._P2P.send(None, to, method="p2ppy", ACLmsg=ACLmsg):
                        #The Ultra-Fast(tm) way worked. Remove this receiver from the remaining receivers
                        remaining.remove(receiver)

                tojid = remaining
                if not tojid:
                    #There is no one left to send the message to
                    return
        except Exception, e:
            self.DEBUG("Could not send through P2PPY: " + str(e), "warn")
            method = "jabber"

        # Second, try it the old way
        xenv = xmpp.protocol.Node('jabber:x:fipa x')
        envelope = Envelope.Envelope()
        generate_envelope = False
        #If there is more than one address in the sender or
        #the only address is not an xmpp address,
        #we need the full sender AID field
        try:
            if method == "xmppfipa" or len(ACLmsg.getSender().getAddresses()) > 1 or \
                    "xmpp" not in ACLmsg.getSender().getAddresses()[0]:
                envelope.setFrom(ACLmsg.getSender())
                generate_envelope = True
        except Exception, e:
            self.DEBUG("Error setting sender: " + str(e), "err")

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
            self.DEBUG("Error setting receivers: " + str(e), "err")

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
            self.DEBUG("Error setting reply-to: " + str(e), "err")

        #Generate the envelope ONLY if it is needed
        if generate_envelope:
            envelope.setAclRepresentation(ACLmsg.getAclRepresentation())
            xc = XMLCodec.XMLCodec()
            envxml = xc.encodeXML(envelope)
            xenv['content-type'] = 'fipa.mts.env.rep.xml.std'
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
                jabber_msg["from"] = self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())
            else:
                #I don't understand this address, relay the message to the platform
                jabber_msg = xmpp.protocol.Message(self.getSpadePlatformJID(), xmlns="")
                jabber_id = self.getSpadePlatformJID()
                jabber_msg.attrs.update(ACLmsg._attrs)
                jabber_msg.addChild(node=xenv)
                jabber_msg["from"] = self.getAID().getName()
                jabber_msg.setBody(ACLmsg.getContent())

            if (not self._running and method == "auto") or method == "jabber" or method == "xmppfipa":
                self.jabber.send(jabber_msg)
                continue

            #If the receiver is one of our p2p contacts, send the message through p2p.
            #If it's not or it fails, send it through the jabber server
            #We suppose method in ['p2p']
            jabber_id = xmpp.JID(jabber_id).getStripped()

            if self._P2P.isReady():
                sent = False
                self._P2P.acquire()
                try:
                    sent = self._P2P.send(jabber_msg, jabber_id, method=method, ACLmsg=ACLmsg)
                except Exception, e:
                    self.DEBUG("P2P Connection to " + str(self._P2P.getRoutes()) + jabber_id + " prevented. Falling back. " + str(e), "warn")
                    sent = False
                self._P2P.release()
                if not sent:
                    #P2P failed, try to send it through jabber
                    self.DEBUG("P2P failed, try to send it through jabber", "warn")
                    jabber_msg.attrs.update({"method": "jabber"})
                    if method in ["auto", "p2p", "p2ppy"]:
                        self.jabber.send(jabber_msg)

            else:
                #P2P is not available / not supported
                #Try to send it through jabber
                self.DEBUG("P2P is not available/supported, try to send it through jabber", "warn")
                jabber_msg.attrs.update({"method": "jabber"})
                if method in ["auto", "p2p", "p2ppy"]:
                    self.jabber.send(jabber_msg)

    def _kill(self):
        """
        kills the agent
        """
        if self.wui.isRunning():
            self.wui.stop()
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
        try:
            self.roster.sendPresence("unavailable")
        except Exception, e:
            self.DEBUG("Did not send 'unavailable' presence: " + str(e), 'warn')

        self.wui.stop()
        if not self.forceKill():
            self._shutdown()
        else:
            self._kill()

        if timeout > 0:
            to = time.now() + timeout
            while self.isRunning() and time.now() < to:
                time.sleep(0.1)
        #No timeout (true blocking)
        else:
            while self.isRunning():
                time.sleep(0.1)
        self.DEBUG("Stopping agent " + self.getName(), 'ok')
        return True

    def forceKill(self):
        return self._forceKill.isSet()

    def _setup(self):
        """
        setup agent method. configures the agent
        must be overridden
        """
        pass

    def _initBdiBehav(self):
        """
        starts the BDI behaviour ONLY
        if self is a subclass of bdi.BDIAgent
        """
        if issubclass(self.__class__, BDIAgent):
            self._startBdiBehav()

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
        if (self._defaultbehaviour is not None):
            self._defaultbehaviour.start()

        #If this agent supports P2P, wait for P2PBEhaviour to properly start
        if self._P2P.p2p:
            counter = 10
            while not self._P2P.isReady() and counter > 0:
                time.sleep(0.2)
                counter -= 1
            if not self._P2P.isReady():
                self.DEBUG("This agent could not activate p2p messages behaviour", "err")

        #############
        # Main Loop #
        #############
        self.DEBUG("Agent " + self.getName() + " starts main loop", "info")
        while not self.forceKill():
            try:
                #Check for queued messages
                proc = False
                toRemove = []  # List of EventBehaviours to remove after this pass
                msg = self._receive(block=True, timeout=0.01)
                if msg is not None:
                    bL = copy.copy(self._behaviourList)
                    for b in bL:
                        t = bL[b]
                        if t is not None:
                            if t.match(msg) is True:
                                if not (isinstance(b, types.TypeType) or isinstance(b, types.ClassType)) and not issubclass(b.__class__, Behaviour.EventBehaviour):
                                    b.postMessage(msg)
                                else:
                                    ib = b()
                                    if ib.onetime:
                                        toRemove.append(b)
                                    ib.setAgent(self)
                                    ib.postMessage(msg)
                                    ib.start()
                                proc = True

                    if proc is False:
                        #If no template matches, post the message to the Default behaviour
                        self.DEBUG("Message was not reclaimed by any behaviour. Posting to default behaviour: " + str(msg) + str(bL.keys()), "info", "msg")
                        if (self._defaultbehaviour is not None):
                            self._defaultbehaviour.postMessage(msg)
                    for beh in toRemove:
                        self.removeBehaviour(beh)
            except Exception, e:
                self.DEBUG("Agent " + self.getName() + " Exception in run: " + str(e), "err")
                self._kill()

        self.DEBUG("Agent starts shutdown", 'info')
        self._shutdown()

    def setDefaultBehaviour(self, behaviour):
        """
        sets a Behavior as Default
        """
        class NotAllowed(Exception):
            """
            Not Allowed Exception: an EventBehaviour cannot be a default behaviour
            """
            def __init__(self):
                pass

            def __str__(self):
                return "an EventBehaviour cannot be a default behaviour"

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
        if not issubclass(behaviour.__class__, Behaviour.EventBehaviour):  # and type(behaviour) != types.TypeType:
            #Event behaviour do not start inmediately
            self._behaviourList[behaviour] = copy.copy(template)
            behaviour.setAgent(self)
            behaviour.start()
        else:
            self.DEBUG("Adding Event Behaviour " + str(behaviour.__class__))
            self._behaviourList[behaviour.__class__] = copy.copy(template)

    def runBehaviourOnce(self, behaviour, template=None):
        """
        Runs the behaviour offline
        Executes its process once
        @warning Only for OneShotBehaviour
        """
        if not issubclass(behaviour.__class__, Behaviour.OneShotBehaviour):
            self.DEBUG("Only OneShotBehaviour execution is allowed offline", "err")
            return False

        if not self._running:
            try:
                behaviour._receive = self._receive
                behaviour.myAgent = self
                behaviour.onStart()
                behaviour._process()
                behaviour.onEnd()
                del behaviour
                return True
            except Exception, e:
                self.DEBUG("Failed the execution of the OFFLINE behaviour " + str(behaviour) + ": " + str(e), "err")
                return False
        else:
            self.addBehaviour(behaviour, template)

    def removeBehaviour(self, behaviour):
        """
        removes a behavior from the agent
        """
        if (type(behaviour) not in [types.ClassType, types.TypeType]) and (not issubclass(behaviour.__class__, Behaviour.EventBehaviour)):
            behaviour.kill()
        try:
            self._behaviourList.pop(behaviour)
            self.DEBUG("Behaviour removed: " + str(behaviour.getName()), "info", "behaviour")
        except KeyError:
            self.DEBUG("removeBehaviour: Behaviour " + str(behaviour) + "with type " + str(type(behaviour)) + " is not registered in " + str(self._behaviourList.keys()), "warn")

    def hasBehaviour(self, behaviour):
        """
        returns True if the behaviour is active in the agent
        otherwise returns False
        """
        if behaviour in self._behaviourList.keys():
            return True
        return False

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
        #iq = Iq("get", NS_ROSTER)
        #self.send(iq)
        #if not nowait:
        #    while self._waitingForRoster:
        #        time.sleep(0.3)
        #    return self._roster

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
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.SearchAgentBehaviour(msg, AAD)

        self.addBehaviour(b, t)
        b.join()
        return b.result

    def modifyAgent(self, AAD):
        """
        modifies the AmsAgentDescription of an agent in the AMS
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.ModifyAgentBehaviour(msg, AAD)

        self.addBehaviour(b, t)
        b.join()
        return b.result

    def getPlatformInfo(self):
        """
        returns the Plarform Info
        """
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.getPlatformInfoBehaviour(msg)

        self.addBehaviour(b, t)
        b.join()
        return b.result

    def registerService(self, service, methodCall=None, otherdf=None):
        """
        registers a service in the DF
        the service template is a DfAgentDescriptor
        """

        if isinstance(service, DF.Service):
            DAD = service.getDAD()
        else:
            DAD = service

        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        if otherdf and isinstance(otherdf, AID.aid):
            template.setSender(otherdf)
        else:
            template.setSender(self.getDF())
        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.registerServiceBehaviour(msg=msg, DAD=DAD, otherdf=otherdf)
        if self._running:
            # Online
            self.addBehaviour(b, t)
            b.join()
        else:
            self.runBehaviourOnce(b, t)

        if methodCall and b.result is True:
            if not isinstance(service, DF.Service):
                self.DEBUG("Could not register RPC Service. It's not a DF.Service class", "error")
                return False

            name = service.getName()
            self.DEBUG("Registering RPC service " + name)
            self.RPC[name.lower()] = (service, methodCall)
        return b.result

    def deregisterService(self, DAD, otherdf=None):
        """
        deregisters a service in the DF
        the service template is a DfAgentDescriptor
        """

        if DAD.getName() in self.RPC.keys():
            del self.RPC[DAD.getName()]

        if isinstance(DAD, DF.Service):
            DAD = DAD.getDAD()

        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        if otherdf and isinstance(otherdf, AID.aid):
            template.setSender(otherdf)
        else:
            template.setSender(self.getDF())

        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.deregisterServiceBehaviour(msg=msg, DAD=DAD, otherdf=otherdf)
        if self._running:
            # Online
            self.addBehaviour(b, t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b, t)
            return b.result

    def searchService(self, DAD):
        """
        search a service in the DF
        the service template is a DfAgentDescriptor

        """
        if isinstance(DAD, DF.Service):
            DAD = DAD.getDAD()
            returnDAD = False
        else:
            returnDAD = True

        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.searchServiceBehaviour(msg, DAD)
        if self._running:
            self.addBehaviour(b, t)
            b.join()
        else:
            self.runBehaviourOnce(b, t)

        if b.result is None:
            return None
        if returnDAD:
            return b.result
        else:
            r = []
            for dad in b.result:
                for sd in dad.getServices():
                    s = DF.Service()
                    if sd.getName():
                        s.setName(sd.getName())
                    if dad.getAID():
                        s.setOwner(dad.getAID())
                    for o in sd.getOntologies():
                        s.setOntology(o)
                    if sd.getProperty("description"):
                        s.setDescription(sd.getProperty("description"))
                    if sd.getProperty("inputs"):
                        s.setInputs(sd.getProperty("inputs"))
                    if sd.getProperty("outputs"):
                        s.setOutputs(sd.getProperty("outputs"))
                    if sd.getProperty("P"):
                        for p in sd.getProperty("P"):
                            s.addP(p)
                    if sd.getProperty("Q"):
                        for q in sd.getProperty("Q"):
                            s.addQ(q)
                    s.getDAD().getServices()[0].setType(sd.getType())
                    for o in sd.getOntologies():
                        s.setOntology(o)
                    r.append(s)
            return r

    def modifyService(self, DAD, methodCall=None):
        """
        modifies a service in the DF
        the service template is a DfAgentDescriptor
        """

        if methodCall:
            if not isinstance(DAD, DF.Service):
                self.DEBUG("Could not modify RPC Service. It's not a DF.Service class", "error")
                return False

            self.RPC[DAD.getName()] = (DAD, methodCall)

        if isinstance(DAD, DF.Service):
            DAD = DAD.getDAD()

        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        r = str(uuid.uuid4()).replace("-", "")
        msg.setReplyWith(r)
        template.setInReplyTo(r)
        t = Behaviour.MessageTemplate(template)
        b = fipa.modifyServiceBehaviour(msg, DAD)

        if self._running:
            # Online
            self.addBehaviour(b, t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b, t)
            return b.result

    ####################
    #RPC invokation
    ####################
    def invokeService(self, service, inputs=None):
        """
        invokes a service using jabber-rpc (XML-RPC)
        the service template must be a DF.Service
        if inputs is None, they are extracted from the agent's KB
        """

        if not isinstance(service, DF.Service):
            self.DEBUG("Service MUST be a DF.Service instance", 'error')
            return False

        num = str(uuid.uuid4()).replace("-", "")

        if inputs is None:  # inputs = self.KB
            inputs = {}
            for i in service.getInputs():
                r = self.kb.get(str(i))
                if r is None:
                    self.DEBUG("Can not invoke Service, input not found: " + str(i), 'error')
                    return False
                self.DEBUG("Adding input: " + str(i) + " = " + str(r))
                inputs[i] = r

        self.DEBUG("Invoking service " + str(service.getName()) + " with inputs = " + str(inputs))
        b = RPC.RPCClientBehaviour(service, inputs, num)
        t = Behaviour.MessageTemplate(Iq(typ="result", attrs={'id': num}))

        if self._running:
            # Online
            self.addBehaviour(b, t)
            b.join()
            return b.result
        else:
            self.runBehaviourOnce(b, t)
            return b.result

    ####################
    #PubSub services
    ####################
    def publishEvent(self, name, event):
        return self._pubsub.publish(name, event)

    def subscribeToEvent(self, name, behaviour=None, server=None, jid=None):
        r = self._pubsub.subscribe(name, server, jid)
        if r[0] == 'ok' and behaviour is not None:
            if not issubclass(behaviour.__class__, Behaviour.EventBehaviour):
                self.DEBUG("Behaviour MUST be an EventBehaviour to subscribe to events.", "error", "pubsub")
                return ("error", ["not-event-behaviour"])
            self._events[name] = behaviour
            n = xmpp.Node(node='<message xmlns="jabber:client"><event xmlns="http://jabber.org/protocol/pubsub#events"><items node="' + name + '" /></event></message>')
            template = xmpp.Message(node=n)
            mt = Behaviour.MessageTemplate(template)
            self.addBehaviour(behaviour, mt)
        return r

    def unsubscribeFromEvent(self, name, server=None, jid=None):
        r = self._pubsub.unsubscribe(name, server, jid)
        if name in self._events.keys():
            self.removeBehaviour(self._events[name])
            del self._events[name]
        return r

    def createEvent(self, name, server=None, type='leaf', parent=None, access=None):
        return self._pubsub.createNode(name, server=None, type='leaf', parent=None, access=None)

    def deleteEvent(self, name, server=None):
        return self._pubsub.deleteNode(name, server=None)

    ########################
    #Knowledge Base services
    ########################
    def addBelieve(self, sentence, type="insert"):
        if isinstance(sentence, types.StringType):
            try:
                if issubclass(Flora2KB.Flora2KB, self.kb.__class__):
                    self.kb.tell(sentence, type)
            except:
                self.kb.tell(sentence)
        else:
            self.kb.tell(sentence)
        self._needDeliberate = True
        ###self.newBelieveCB(sentence) #TODO

    def removeBelieve(self, sentence, type="delete"):
        if isinstance(sentence, types.StringType):
            try:
                if issubclass(Flora2KB.Flora2KB, self.kb.__class__):
                    self.kb.retract(sentence, type)
            except:
                self.kb.retract(sentence)
        else:
            self.kb.retract(sentence)
        self._needDeliberate = True

    def askBelieve(self, sentence):
        return self.kb.ask(sentence)

    def configureKB(self, typ, sentence=None, path=None):
        self.kb.configure(typ, sentence, path)

    def saveFact(self, name, sentence):
        self.kb.set(name, sentence)

    def getFact(self, name):
        return self.kb.get(name)

    def loadKB(self, module, into=None):
        return self.kb.loadModule(module, into)

##################################


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
            self._owner.DEBUG("Jabber thread dying.", 'info')
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
                    self._owner.DEBUG('\n' + ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip(), "err")
                    self._owner.DEBUG("Exception in jabber process: " + str(e), "err")
                    self._owner.DEBUG("Jabber connection failed: " + self._owner.getAID().getName() + " (dying)", "err")
                    self._kill()
                    self._owner.stop()
                    err = None

            if err is None or err == 0:  # None or zero the integer, socket closed
                self._owner.DEBUG("Agent disconnected: " + self._owner.getAID().getName() + " (dying)", "err")
                self._kill()
                self._owner.stop()


class PlatformAgent(AbstractAgent):
    """
    A PlatformAgent is a SPADE component.
    Examples: AMS, DF, ACC, ...
    """
    def __init__(self, node, password, server="localhost", port=5347, config=None, debug=[], p2p=False):

        self.jabber = xmpp.Component(server=server, port=port, debug=debug)
        AbstractAgent.__init__(self, node, server, p2p=p2p)

        self.config = config
        if 'adminpasswd' in config.keys():
            self.wui.passwd = config['adminpasswd']

        self.debug = debug
        if not self._register(password):
            self._shutdown()

        # Register PubSub handlers
        self._pubsub.register()

        # Register RPC handlers
        self._RPC.register()

        # Register P2P handlers
        self._P2P.register()

    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        tries = 5
        while not self.jabber.connect() and tries > 0:
            time.sleep(0.005)
            tries -= 1
        if tries <= 0:
            self.DEBUG("The agent could not connect to the platform " + str(self.getDomain()), "err")
            return False

        if (self.jabber.auth(name=name, password=password) is None):
            raise NotImplementedError

        self.jabber.RegisterHandler('message', self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence', self._jabber_messageCB)
        self.jabber.RegisterDefaultHandler(self._other_messageCB)
        #self.jabber.RegisterHandler('iq', self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence',self._jabber_presenceCB)
        #self.jabber.RegisterHandler('iq',self._jabber_iqCB)

        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()
        return True

    def _shutdown(self):

        self._kill()  # Doublecheck death
        if hasattr(self, "jabber_process"):
            self.jabber_process._kill()

        #Stop the Behaviours
        for b in self._behaviourList.keys():  # copy.copy(self._behaviourList.keys()):
            try:
                if not (isinstance(b, types.TypeType) or isinstance(b, types.ClassType)):
                    if not issubclass(b.__class__, Behaviour.EventBehaviour):
                        b.kill()
            except Exception, e:
                self.DEBUG("Could not kill behavior " + str(b) + ": " + str(e), "warn")

        if issubclass(self.__class__, BDIAgent):
            self.bdiBehav.kill()

        if (self._defaultbehaviour is not None):
            self._defaultbehaviour.kill()

        #DeInit the Agent
        self.takeDown()

        self._alive = False


class AgentNotRegisteredError(Exception):
    pass


class Agent(AbstractAgent):
    """
    This is the main class which may be inherited to build a SPADE agent
    """

    def __init__(self, agentjid, password, resource="spade", port=5222, debug=[], p2p=False):
        jid = xmpp.protocol.JID(agentjid)
        self.server = jid.getDomain()
        self.resource = resource
        self.port = port
        self.debug = debug
        self.jabber = xmpp.Client(jid.getDomain(), port, debug)
        AbstractAgent.__init__(self, agentjid, jid.getDomain(), p2p=p2p)

        # Try to register
        self.DEBUG("Trying to register agent " + agentjid)
        if not self._register(password):
            self.setDebugToScreen()
            self.DEBUG("Could not register agent %s" % (agentjid), "err")
            self.stop()
            raise AgentNotRegisteredError

        # Add Presence Control Behaviour
        self.addBehaviour(socialnetwork.PresenceBehaviour(), Behaviour.MessageTemplate(Presence()))

        # Register PubSub handlers
        self._pubsub.register()

        # Register RPC handlers
        self._RPC.register()

        # Register P2P handlers
        self._P2P.register()

        # Add Roster Behaviour
        ##self.addBehaviour(socialnetwork.RosterBehaviour(), Behaviour.MessageTemplate(Iq(queryNS=NS_ROSTER)))

        # Add BDI Behaviour #only for BDI agents
        self._initBdiBehav()

        self.DEBUG("Agent %s registered" % (agentjid), "ok")

        if not self.__register_in_AMS():
            self.DEBUG("Agent " + str(self.getAID().getName()) + " dying ...", "err")
            self.stop()

        # Ask for roster
        ##self.getSocialNetwork(nowait=True)


    def _register(self, password, autoregister=True):
        """
        registers the agent in the Jabber server
        """

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        tries = 5
        while not self.jabber.connect(use_srv=None) and tries > 0:
            time.sleep(0.005)
            tries -= 1
        if tries <= 0:
            self.setDebugToScreen()
            self.DEBUG("There is no SPADE platform at " + self.server + " . Agent dying...", "err")
            return False

        if (self.jabber.auth(name, password, self.resource) is None):

            self.DEBUG("First auth attempt failed. Trying to register", "warn")

            if autoregister is True:
                xmpp.features.getRegInfo(self.jabber, jid.getDomain())
                xmpp.features.register(self.jabber, jid.getDomain(),
                                       {'username': name, 'password': str(password), 'name': name})

                if not self.jabber.reconnectAndReauth():
                    self.DEBUG("Second auth attempt failed (username=" + str(name) + ")", "err")
                    return False
            else:
                return False

        self.DEBUG("Agent %s got authed" % (self._aid.getName()), "ok")

        self.roster = socialnetwork.Roster(self)

        self.jabber.RegisterHandler('message', self._jabber_messageCB)
        #self.jabber.RegisterHandler('presence', self._jabber_messageCB)
        #self.jabber.RegisterHandler('iq', self._jabber_messageCB)
        self.jabber.RegisterDefaultHandler(self._other_messageCB)

        self.jabber_process = jabberProcess(self.jabber, owner=self)
        self.jabber_process.start()

        # Request roster and send initial presence
        #self.getSocialNetwork()

        self.jabber.sendInitPresence()

        return True

    def _shutdown(self):
        #Stop the Behaviours
        for b in self._behaviourList.keys():  # copy.copy(self._behaviourList.keys()):
            try:
                if not (isinstance(b, types.TypeType) or isinstance(b, types.ClassType)):
                    if not issubclass(b.__class__, Behaviour.EventBehaviour):
                        b.kill()
            except Exception, e:
                self.DEBUG("Could not kill behavior " + str(b) + ": " + str(e), "warn")

        if issubclass(self.__class__, BDIAgent):
            self.bdiBehav.kill()

        if (self._defaultbehaviour is not None):
            self._defaultbehaviour.kill()

        #DeInit the Agent
        self.takeDown()

        if self._alivemutex.testandset():
            if hasattr(self, "jabber_process") and not self.jabber_process.forceKill():
                if not self.__deregister_from_AMS():
                    self.DEBUG("Agent " + str(self.getAID().getName()) + " dying without deregistering itself ...", "err")
                self.jabber_process._kill()  # Kill jabber thread
            self._alive = False
        self._alivemutex.unlock()
        self._kill()  # Doublecheck death
        self._alive = False

    def __register_in_AMS(self, state='active', ownership=None, debug=False):
        # Let's change it to "subscribe"
        presence = xmpp.Presence(to=self.getAMS().getName(), frm=self.getName(), typ='subscribe')

        self.send(presence)

        self.DEBUG("Agent: " + str(self.getAID().getName()) + " registered correctly (inform)", "ok")
        return True

    def __register_in_AMS_with_ACL(self, state='active', ownership=None, debug=False):

        self._msg = ACLMessage.ACLMessage()
        self._msg.addReceiver(self.getAMS())
        self._msg.setPerformative('request')
        self._msg.setLanguage('fipa-sl0')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        content = "((action "
        content += str(self.getAID())
        content += "(register (ams-agent-description "
        content += ":name " + str(self.getAID())
        content += ":state " + state
        if ownership:
            content += ":ownership " + ownership
        content += " ) ) ))"

        self._msg.setContent(content)

        self.send(self._msg)

        # We expect the initial answer from the AMS
        msg = self._receive(True, 20)
        if (msg is not None) and (str(msg.getPerformative()) == 'refuse'):
            self.DEBUG("There was an error initiating the register of agent: " + str(self.getAID().getName()) + " (refuse)", "err")
            return False
        elif (msg is not None) and (str(msg.getPerformative()) == 'agree'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " initiating registering process (agree)")
        else:
            # There was no answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error initiating the register of agent: " + str(self.getAID().getName()), "err")
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True, 20)
        if (msg is not None) and (msg.getPerformative() == 'failure'):
            self.DEBUG("There was an error with the register of agent: " + str(self.getAID().getName()) + " (failure)", "err")
            return False
        elif (msg is not None) and (str(msg.getPerformative()) == 'inform'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " registered correctly (inform)", "ok")
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error with the register of agent: " + str(self.getAID().getName()), "err")
            return False

        return True

    def __deregister_from_AMS(self, state=None, ownership=None, debug=False):

        presence = xmpp.Presence(to=self.getAMS().getName(), frm=self.getName(), typ='unsubscribe')

        self.send(presence)
        self.DEBUG("Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)", "ok")

        return True

    def __deregister_from_AMS_with_ACL(self, state=None, ownership=None, debug=False):

        _msg = ACLMessage.ACLMessage()
        _msg.addReceiver(self.getAMS())
        _msg.setPerformative('request')
        _msg.setLanguage('fipa-sl0')
        _msg.setProtocol('fipa-request')
        _msg.setOntology('FIPA-Agent-Management')

        content = "((action "
        content += str(self.getAID())
        content += "(deregister (ams-agent-description "
        content += " :name " + str(self.getAID())
        if state:
            content += " :state " + state
        if ownership:
            content += " :ownership " + ownership
        content += " ) ) ))"

        _msg.setContent(content)

        self.send(_msg)

        # We expect the initial answer from the AMS
        msg = self._receive(True, 20)
        if (msg is not None) and (str(msg.getPerformative()) == 'refuse'):
            self.DEBUG("There was an error initiating the deregister of agent: " + str(self.getAID().getName()) + " (refuse)", "err")
            return False
        elif (msg is not None) and (str(msg.getPerformative()) == 'agree'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " initiating deregistering process (agree)")
        else:
            # There was no answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error deregistering of agent: " + str(self.getAID().getName()), "err")
            return False

        # Now we expect the real informative answer from the AMS
        msg = self._receive(True, 20)
        if (msg is not None) and (msg.getPerformative() == 'failure'):
            self.DEBUG("There was an error with the deregister of agent: " + str(self.getAID().getName()) + " (failure)", "err")
            return False
        elif (msg is not None) and (str(msg.getPerformative()) == 'inform'):
            self.DEBUG("Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)", "ok")
        else:
            # There was no real answer from the AMS or it answered something weird, so error
            self.DEBUG("There was an error with the deregister of agent: " + str(self.getAID().getName()), "err")
            return False

        return True


class BDIAgent(Agent):
    def _startBdiBehav(self):
        self.bdiBehav = bdi.BDIBehaviour(period=1)
        self.addBehaviour(self.bdiBehav, None)
        self.DEBUG("BDI behaviour added.", 'info')

    def setPeriod(self, period):
        self.bdiBehav.setPeriod(period)

    def getPeriod(self):
        return self.bdiBehav.getPeriod()

    def addPlan(self, inputs=[], outputs=[], P=[], Q=[], services=[]):
        return self.bdiBehav.addPlan(inputs, outputs, P, Q, services)

    def addGoal(self, goal):
        self.bdiBehav.addGoal(goal)

    def setPlanSelectedCB(self, func):
        '''func MUST have as input parameter a plan'''
        self.bdiBehav.planSelectedCB = func

    def setGoalCompletedCB(self, func):
        '''func MUST have as input parameter a goal'''
        self.bdiBehav.goalCompletedCB = func

    def setServiceCompletedCB(self, func):
        '''func MUST have as input parameter a DF.Service'''
        self.bdiBehav.serviceCompletedCB = func
