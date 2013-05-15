# -*- coding: utf-8 -*-
from spade.AMS import AmsAgentDescription
from spade.DF import DfAgentDescription, Service
from spade.Agent import PlatformAgent, require_login
import spade.Envelope
import spade.AID
import spade.Behaviour
import spade.ACLMessage
import spade.BasicFipaDateTime

#from spade.wui import require_login
from os.path import abspath


class PlatformRestart(Exception):
    def __str__(self):
        return


class SpadePlatform(PlatformAgent):

    class RouteBehaviour(spade.Behaviour.Behaviour):
        #This behavior routes messages between agents.
        #Also uses MTPs when different protocols are required (HTTP, ...)
        def __init__(self):
            spade.Behaviour.Behaviour.__init__(self)

        def _process(self):
            msg = self._receive(True)
            if (msg is not None):
                self.myAgent.DEBUG("SPADE Platform Received a message: " + str(msg), 'info')
                if msg.getSender() == self.myAgent.getAID():
                    # Prevent self-loopholes
                    self.myAgent.DEBUG("ACC LOOP HOLE", "warn")
                    return

                #prepare to send the message to each one of the receivers separately
                to_list = msg.getReceivers()
                d = {}
                for to in to_list:
                    if (self.myAgent.getAID().getName() != to.getName()):
                        if not to.getAddresses()[0] in d:
                            d[to.getAddresses()[0]] = list()
                        d[to.getAddresses()[0]].append(to)
                for k, v in d.items():
                    newmsg = msg
                    newmsg.to = v
                    try:
                        protocol, receiver_URI = k.split("://")
                    except:
                        self.myAgent.DEBUG("Malformed Agent Address URI: " + str(k), "error")
                        break

                    # Check if one of our MTPs handles this protocol
                    #switch(protocol)
                    if protocol in self.myAgent.mtps.keys():
                        self.myAgent.DEBUG("Message through protocol " + str(protocol))
                        payload = newmsg

                        envelope = spade.Envelope.Envelope()
                        envelope.setFrom(newmsg.getSender())
                        for i in newmsg.getReceivers():
                            envelope.addTo(i)
                        envelope.setAclRepresentation(newmsg.getAclRepresentation())
                        envelope.setPayloadLength(len(str(payload)))
                        envelope.setPayloadEncoding("US-ASCII")
                        envelope.setDate(spade.BasicFipaDateTime.BasicFipaDateTime())
                        self.myAgent.mtps[protocol].send(envelope, payload)
                    else:
                        # Default case: it's an XMPP message
                        self.myAgent.DEBUG("Message through protocol XMPP", 'info')
                        platform = self.myAgent.getSpadePlatformJID().split(".", 1)[1]
                        if not platform in receiver_URI:
                            # Outside platform
                            self.myAgent.DEBUG("Message for another platform", 'info')
                            self.myAgent.send(newmsg, "jabber")
                        else:
                            # THIS platform
                            self.myAgent.DEBUG("Message for current platform", 'info')
                            for recv in v:
                                #self.myAgent._sendTo(newmsg, recv.getName(), "jabber")
                                self.myAgent.send(newmsg, "jabber")

                    """
                    if k[7:] != self.myAgent.getSpadePlatformJID():
                        self.myAgent._sendTo(newmsg, k[7:])
                    else:
                        for recv in v:
                            self.myAgent._sendTo(newmsg, recv.getName())
                    # Reenviamos el msg a todos los destinatarios
                    # Tambien deberiamos comprobar el protocolo y usar una pasarela en el caso de que sea necesario.
                    #print "Message to", to.getName(), "... Posting!"
                    """
            else:
                pass
                ##self.myAgent.DEBUG("ACC::dying... this shouldn't happen", 'err')

    def __init__(self, node, password, server, port, config=None):
        PlatformAgent.__init__(self, node, password, server, port, config=config, debug=[])
        self.mtps = {}

    def _setup(self):
        self.setDefaultBehaviour(self.RouteBehaviour())

        self.wui.registerController("index", self.index)
        self.wui.registerController("agents", self.agents)
        self.wui.registerController("services", self.services)
        self.wui.registerController("roster", self.get_roster)
        self.wui.setPort(8008)
        self.wui.start()

        import mtps
        # Load MTPs
        for name, _mtp in self.config.acc.mtp.items():
            try:
                mod = "mtps."+name
                mod = __import__(mod, globals(), locals(),[name])
                self.mtps[_mtp['protocol']] = mod.INSTANCE(name, self.config, self)
            except Exception, e:
                self.DEBUG("EXCEPTION IMPORTING MTPS: " + str(e), 'err', 'acc')

    def takeDown(self):
        for k, _mtp in self.mtps.items():
            try:
                _mtp.stop()
                del self.mtps[k]
            except:
                pass

    def setXMPPServer(self, server):
        self.server = server

    #Controllers
    def index(self):
        import sys
        import time
        servername = self.getDomain()
        platform = self.getName()
        version = str(sys.version)
        the_time = str(time.ctime())
        doc_path = abspath('.')
        return "webadmin_indigo.pyra", dict(name=platform, servername=servername, platform=platform, version=version, time=the_time, doc_path=doc_path)

    @require_login
    def agents(self):
        import sys
        import time
        #so = self.session
        servername = self.getDomain()
        platform = self.getName()
        version = str(sys.version)
        the_time = str(time.ctime())
        search = self.searchAgent(AmsAgentDescription())
        """for agent in search:
            if not agent.has_key("fipa:state"):
                agent["fipa:state"] = ""
        """
        # Build AWUIs dict
        awuis = {}
        if search:
            aw = ""
            for agent in search:
                if agent.getAID():
                    aw = "#"
                    for addr in agent.getAID().getAddresses():
                        if "awui://" in addr:
                            aw = addr.replace("awui://", "http://")
                            break
                    awuis[agent.getAID().getName()] = aw
        self.DEBUG("AWUIs: " + str(awuis))
        return "agents.pyra", dict(name=platform, servername=servername, platform=platform, version=version, time=the_time, agents=search, awuis=awuis)

    @require_login
    def services(self):
        import sys
        import time
        servername = self.getDomain()
        platform = self.getName()
        version = str(sys.version)
        the_time = str(time.ctime())
        try:
            search = self.searchService(DfAgentDescription())
        except Exception, e:
            print "Exception: " + str(e)
        servs = {}
        for dad in search:
            for service in dad.getServices():
                if service.getType() not in servs.keys():
                    servs[service.getType()] = []
                new_dad = dad
                new_dad.services = [service]
                s = Service(dad=new_dad)
                servs[service.getType()].append(s)
        self.DEBUG("Services: " + str(servs))
        return "services.pyra", dict(name=platform, servername=servername, platform=platform, version=version, time=the_time, services=servs)

    @require_login
    def get_roster(self):
        import sys
        import time
        import copy
        servername = self.getDomain()
        platform = self.getName()
        version = str(sys.version)
        the_time = str(time.ctime())
        roster = copy.copy(self.server.DB.db)
        for server, v in roster.items():
            try:
                del v["__ir__"]
            except: pass
            for r in v.values():
                try:
                    del r["roster"]["__ir__"]
                except: pass
        return "rosterdb.pyra", dict(name=platform, servername=servername, platform=platform, version=version, time=the_time, roster=roster)

    def getMembers(self, aname):
        msg = spade.ACLMessage.ACLMessage()
        msg.setOntology("spade:x:organization")
        template = spade.Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = spade.Behaviour.MessageTemplate(template)
        b = self.GetMembersBehav()
        b.msg = msg
        b.aname = aname
        self.addBehaviour(b, t)
        b.join()
        return b.result

    class GetMembersBehav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            self.result = []
            self.msg.addReceiver(spade.AID.aid(self.aname, addresses=["xmpp://" + self.aname]))
            self.msg.setContent("MEMBERS")
            self.myAgent.send(self.msg)
            rep = None
            rep = self._receive(True, 20)
            if rep:
                print "The members list arrived"
                self.result = rep.getContent().split(",")
