# -*- coding: utf-8 -*-

from Agent import PlatformAgent
import AID
import Behaviour
import BasicFipaDateTime
from SL0Parser import *
from content import ContentObject
import xmpp
import copy
import thread


class DF(PlatformAgent):
    """
    Directory Facilitator Agent
    """

    class DefaultBehaviour(Behaviour.Behaviour):

        def __init__(self):
            Behaviour.Behaviour.__init__(self)
            self.sl0parser = SL0Parser()

        def _process(self):
            error = False
            msg = self._receive(True)
            if msg is not None:
                if msg.getPerformative().lower() == 'request':
                    if msg.getOntology().lower() == "fipa-agent-management":
                        if msg.getLanguage().lower() == "fipa-sl0":
                            content = self.sl0parser.parse(msg.getContent())
                            ACLtemplate = Behaviour.ACLTemplate()
                            ACLtemplate.setConversationId(msg.getConversationId())
                            #ACLtemplate.setSender(msg.getSender())
                            template = (Behaviour.MessageTemplate(ACLtemplate))

                            if "action" in content:
                                if "register" in content.action or "deregister" in content.action:
                                    self.myAgent.addBehaviour(DF.RegisterBehaviour(msg, content), template)
                                    self.myAgent.DEBUG("Received REGISTER action: " + str(content))
                                elif "search" in content.action:
                                    self.myAgent.addBehaviour(DF.SearchBehaviour(msg, content), template)
                                    self.myAgent.DEBUG("Received SEARCH action: " + str(content))
                                elif "modify" in content.action:
                                    self.myAgent.addBehaviour(DF.ModifyBehaviour(msg, content), template)
                                    self.myAgent.DEBUG("Received MODIFY action: " + str(content))
                            else:
                                reply = msg.createReply()
                                reply.setSender(self.myAgent.getAID())
                                reply.setPerformative("refuse")
                                reply.setContent("( " + msg.getContent() + "(unsuported-function " + content.keys()[0] + "))")
                                self.myAgent.send(reply)
                                self.myAgent.DEBUG("Received message with no action. Refusing: " + str(content), 'warn')

                                return -1

                        elif "rdf" in msg.getLanguage().lower():
                            co = msg.getContentObject()
                            ACLtemplate = Behaviour.ACLTemplate()
                            ACLtemplate.setConversationId(msg.getConversationId())
                            #ACLtemplate.setSender(msg.getSender())
                            template = (Behaviour.MessageTemplate(ACLtemplate))

                            if co and "fipa:action" in co.keys() and "fipa:act" in co["fipa:action"].keys():
                                if co["fipa:action"]["fipa:act"] in ["register", "deregister"]:
                                    self.myAgent.addBehaviour(DF.RegisterBehaviour(msg, co), template)
                                    self.myAgent.DEBUG("Received REGISTER action: " + str(co))
                                elif co["fipa:action"]["fipa:act"] == "search":
                                    self.myAgent.addBehaviour(DF.SearchBehaviour(msg, co), template)
                                    self.myAgent.DEBUG("Received SEARCH action: " + str(co))
                                elif co["fipa:action"]["fipa:act"] == "modify":
                                    self.myAgent.addBehaviour(DF.ModifyBehaviour(msg, co), template)
                                    self.myAgent.DEBUG("Received MODIFY action: " + str(co))
                            else:
                                    reply = msg.createReply()
                                    reply.setSender(self.myAgent.getAID())
                                    reply.setPerformative("refuse")
                                    co2 = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                                    co2["unsuported-function"] = co["fipa:action"]["fipa:act"]
                                    reply.setContentObject(co2)
                                    self.myAgent.send(reply)
                                    self.myAgent.DEBUG("Received message with no action. Refusing: " + str(co), 'warn')
                                    return -1

                        else:
                            error = "(unsupported-language " + msg.getLanguage() + ")"
                    else:
                        error = "(unsupported-ontology " + msg.getOntology() + ")"

                elif msg.getPerformative().lower() not in ['failure', 'refuse']:
                        error = "(unsupported-act " + msg.getPerformative() + ")"
                if error:
                    reply = msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("not-understood")
                    reply.setContent("( " + msg.getContent() + error + ")")
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("NOT-UNDERSTOOD: Could not process message. Error is:" + str(error), 'error')
                    return -1

                #TODO: delete old services

    class RegisterBehaviour(Behaviour.OneShotBehaviour):

        def __init__(self, msg, content):
            Behaviour.OneShotBehaviour.__init__(self)
            self.msg = msg
            self.content = content

        def _process(self):
            #The DF agrees and then informs dummy of the successful execution of the action
            error = False

            # Check if the content language is RDF/XML
            if "rdf" not in self.msg.getLanguage():
                rdf = False
                try:
                    if self.content.action == "register":
                        dad = DfAgentDescription(self.content.action.register['df-agent-description'])
                    else:
                        dad = DfAgentDescription(self.content.action.deregister['df-agent-description'])
                except KeyError:  # Exception,err:
                    error = "(missing-argument df-agent-description)"
                    self.myAgent.DEBUG("REFUSE: Register Behaviour could not extract DfAgentDescription " + error, 'error')

                if error:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("refuse")
                    reply.setContent("( " + self.msg.getContent() + error + ")")
                    self.myAgent.send(reply)

                    return -1

                else:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("agree")
                    reply.setContent("(" + str(self.msg.getContent()) + " true)")
                    self.myAgent.send(reply)

                if self.content.action == "register":

                    if dad.getAID().getName() not in self.myAgent.servicedb.keys():
                        self.myAgent.db_mutex.acquire()
                        self.myAgent.servicedb[dad.getAID().getName()] = dad
                        self.myAgent.db_mutex.release()
                    else:
                        #check if already-registered
                        for ss in dad.getServices():
                            found = False
                            for s in self.myAgent.servicedb[dad.getAID().getName()].getServices():
                                if s.match(ss):
                                    found = True
                            if found:
                                reply.setPerformative("failure")
                                reply.setContent("(" + self.msg.getContent() + "(already-registered))")
                                self.myAgent.send(reply)
                                self.myAgent.DEBUG("FAILURE: Service was already registered! Could not register " + str(dad), 'warn')
                                return -1

                        try:
                            for s in dad.getServices():
                                self.myAgent.db_mutex.acquire()
                                self.myAgent.servicedb[dad.getAID().getName()].addService(s)
                                self.myAgent.db_mutex.release()
                                self.myAgent.DEBUG("Service successfully registered: " + str(s), 'ok')
                        except Exception, err:
                            reply.setPerformative("failure")
                            reply.setContent("(" + self.msg.getContent() + "(internal-error))")
                            self.myAgent.send(reply)
                            self.myAgent.DEBUG("FAILURE: Service could not be registered: " + str(err), 'error')
                            return -1

                    self.DEBUG("Service succesfully deregistered: " + str(dad), 'ok')
                    reply.setPerformative("inform")
                    reply.setContent("(done " + self.msg.getContent() + ")")
                    self.myAgent.send(reply)

                    #publish event
                    s = Service(dad=dad).asContentObject()
                    node = xmpp.Node(node=str(s))
                    self.myAgent.publishEvent("DF:Service:Register", node)

                    return 1

                elif self.content.action == "deregister":

                    if dad.getAID().getName() not in self.myAgent.servicedb.keys():
                        reply.setPerformative("failure")
                        reply.setContent("(" + self.msg.getContent() + "(not-registered))")
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: Agent has no registered services! Could not deregister " + str(dad), 'warn')
                        return -1

                    #check if service is not registered
                    for ss in dad.getServices():
                        found = False
                        for s in self.myAgent.servicedb[dad.getAID().getName()].getServices():
                            if s.match(ss):
                                found = True
                        if not found:
                            reply.setPerformative("failure")
                            reply.setContent("(" + self.msg.getContent() + "(not-registered))")
                            self.myAgent.send(reply)
                            self.myAgent.DEBUG("FAILURE: Service is not registered! Could not deregister " + str(dad), 'warn')
                            return -1

                    try:
                        services = copy.copy(self.myAgent.servicedb[dad.getAID().getName()])
                        if dad.getServices() == []:
                            self.myAgent.db_mutex.acquire()
                            del self.myAgent.servicedb[dad.getAID().getName()]
                            self.myAgent.db_mutex.release()
                        else:
                            for ss in dad.getServices():
                                for s in services.getServices():
                                    if ss.match(s):
                                        self.myAgent.db_mutex.acquire()
                                        self.myAgent.servicedb[dad.getAID().getName()].delService(s)
                                        self.myAgent.db_mutex.release()
                    except Exception, err:
                        reply.setPerformative("failure")
                        reply.setContent("(" + self.msg.getContent() + '(internal-error "could not deregister service"))')
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: Service could not be deregistered: " + str(err), 'error')
                        return -1

                    self.DEBUG("Service succesfully deregistered: " + str(dad), 'ok')
                    reply.setPerformative("inform")
                    reply.setContent("(done " + self.msg.getContent() + ")")
                    self.myAgent.send(reply)

                    #publish event
                    s = Service(dad=dad).asContentObject()
                    node = xmpp.Node(node=str(s))
                    self.myAgent.publishEvent("DF:Service:UnRegister", node)

                    return 1

            elif "rdf" in self.msg.getLanguage():
                # Content in RDF/XML (ContentObject capable)
                rdf = True
                co_error = None
                try:
                    co = self.msg.getContentObject()
                    self.myAgent.DEBUG("Content processed " + str(co), 'info')
                    dad = DfAgentDescription(co=co.action.argument)
                    self.myAgent.DEBUG("DfAgentDescription extracted " + str(dad.asRDFXML()), 'info')
                except KeyboardInterrupt, err:
                    co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_error["fipa:error"] = "missing-argument df-agent-description"
                    self.myAgent.DEBUG("REFUSE: " + str(co_error) + ": " + str(err), 'error')

                if co_error:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("refuse")
                    reply.setContentObject(co_error)
                    self.myAgent.send(reply)
                    return -1

                else:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("agree")
                    co["fipa:done"] = "true"
                    reply.setContentObject(co)
                    self.myAgent.send(reply)

                if co["fipa:action"]["fipa:act"] == "register":
                    if dad.getAID().getName() not in self.myAgent.servicedb.keys():
                        self.myAgent.db_mutex.acquire()
                        self.myAgent.servicedb[dad.getAID().getName()] = dad
                        self.myAgent.db_mutex.release()
                    else:
                        #check if already-registered
                        for ss in dad.getServices():
                            found = False
                            for s in self.myAgent.servicedb[dad.getAID().getName()].getServices():
                                if s.match(ss):
                                    found = True
                                    break
                            if found:
                                reply.setPerformative("failure")
                                co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                                co_error["fipa:error"] = "already-registered"
                                reply.setContentObject(co_error)
                                self.myAgent.send(reply)
                                self.myAgent.DEBUG("FAILURE: Service already registered! ", 'warn')
                                return -1

                        try:
                            for s in dad.getServices():
                                self.myAgent.db_mutex.acquire()
                                self.myAgent.servicedb[dad.getAID().getName()].addService(s)
                                self.myAgent.db_mutex.release()
                                self.myAgent.DEBUG("Service successfully registered: " + str(s), 'ok')
                        except Exception, err:
                            reply.setPerformative("failure")
                            co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                            co_error["fipa:error"] = "internal-error"
                            reply.setContentObject(co_error)
                            self.myAgent.send(reply)
                            self.myAgent.DEBUG("FAILURE: Service could not be registered: " + str(err), 'error')
                            return -1

                    self.DEBUG("Service succesfully registered: " + str(dad), 'ok')
                    reply.setPerformative("inform")
                    co_rep = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_rep["fipa:done"] = "true"
                    reply.setContentObject(co_rep)
                    self.myAgent.send(reply)

                    #publish event
                    self.myAgent.DEBUG("Publishing Event: " + str(dad))
                    s = Service(dad=dad).asContentObject()
                    node = xmpp.Node(node=str(s))
                    self.myAgent.publishEvent("DF:Service:Register", node)

                    return 1

                elif co["fipa:action"]["fipa:act"] == "deregister":
                    if dad.getAID().getName() not in self.myAgent.servicedb.keys():
                        reply.setPerformative("failure")
                        co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                        co_error["fipa:error"] = 'not-registered'
                        reply.setContentObject(co_error)
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: Agent has no registered services", 'warn')
                        return -1

                    #check if service is not registered
                    for ss in dad.getServices():
                        found = False
                        for s in self.myAgent.servicedb[dad.getAID().getName()].getServices():
                            if s.match(ss):
                                found = True
                        if not found:
                            reply.setPerformative("failure")
                            co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                            co_error["fipa:error"] = 'not-registered'
                            reply.setContentObject(co_error)
                            self.myAgent.send(reply)
                            self.myAgent.DEBUG("FAILURE: Service is not registered! Could not deregister " + str(dad), 'warn')
                            return -1

                    try:
                        services = copy.copy(self.myAgent.servicedb[dad.getAID().getName()])
                        self.myAgent.DEBUG("Deregistering " + str(services) + " AND " + str(dad.getServices()))
                        if dad.getServices() == []:
                            self.myAgent.db_mutex.acquire()
                            del self.myAgent.servicedb[dad.getAID().getName()]
                            self.DEBUG("Deleting all agent entries: " + str(dad.getAID().getName() not in self.myAgent.servicedb.keys()))
                            self.myAgent.db_mutex.release()
                        else:
                            for ss in dad.getServices():
                                for s in services.getServices():
                                    if ss.match(s):
                                        self.myAgent.db_mutex.acquire()
                                        self.myAgent.servicedb[dad.getAID().getName()].delService(s)
                                        self.myAgent.db_mutex.release()
                    except Exception, err:
                        reply.setPerformative("failure")
                        co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                        co_error["fipa:error"] = 'internal-error "could not deregister service"'
                        reply.setContentObject(co_error)
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: internal-error 'could not deregister service': " + str(err), 'error')
                        return -1

                    self.DEBUG("Service succesfully deregistered: " + str(dad), 'ok')
                    reply.setPerformative("inform")
                    co_rep = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_rep["fipa:done"] = "true"
                    reply.setContentObject(co_rep)
                    self.myAgent.send(reply)

                    #publish event
                    s = Service(dad=dad).asContentObject()
                    node = xmpp.Node(node=str(s))
                    self.myAgent.publishEvent("DF:Service:UnRegister", node)

                    return 1

    class SearchBehaviour(Behaviour.OneShotBehaviour):

        def __init__(self, msg, content):
            Behaviour.OneShotBehaviour.__init__(self)
            self.msg = msg
            self.content = content

        def _process(self):

            error = False

            reply = self.msg.createReply()
            reply.setSender(self.myAgent.getAID())
            reply.setPerformative("agree")
            if "rdf" in self.msg.getLanguage():
                rdf = True
                reply.setContent("(" + str(self.msg.getContent()) + " true)")
            else:
                rdf = False
            self.myAgent.send(reply)

            if not rdf:
                max = 50
                if "search-constraints" in self.content.action.search:
                    if "max-results" in self.content.action.search["search-constraints"]:
                        try:
                            max_str = str(self.content.action.search["search-constraints"]["max-results"]).strip("[']")
                            max = int(max_str)
                        except Exception, err:
                            error = '(internal-error "max-results is not an integer")'
                            self.myAgent.DEBUG("FAILURE: internal-error 'max-results is not an integer' " + str(err), 'error')
                if error:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("failure")
                    reply.setContent("( " + self.msg.getContent() + error + ")")
                    self.myAgent.send(reply)
                    return -1

                result = []

                if "df-agent-description" in self.content.action.search:
                    try:
                        dad = DfAgentDescription(self.content.action.search["df-agent-description"])
                    except Exception, err:
                        self.myAgent.DEBUG("FAILURE: Could not extract DfAgentDescription from content: " + str(err), 'error')

                self.myAgent.db_mutex.acquire()
                if max in [-1, 0]:
                    # No limit
                    for agentid, dads in self.myAgent.servicedb.items():
                        if dads.match(dad):
                            d = copy.copy(dads)
                            if dad.services == []:
                                d.services = dads.getServices()
                            else:
                                d.services = []
                            for ss in dad.getServices():
                                for s in dads.getServices():
                                    if s.match(ss):
                                        d.addService(s)
                            result.append(d)
                else:
                    max = abs(max)
                    for agentid, dads in self.myAgent.servicedb.items():
                        if max >= 0:
                            if dads.match(dad):
                                d = copy.copy(dads)
                                if dad.services == []:
                                    d.services = dads.getServices()
                                else:
                                    d.services = []
                                for ss in dad.getServices():
                                    for s in dads.getServices():
                                        if s.match(ss):
                                            d.addService(s)
                                result.append(d)
                                max -= 1
                        else:
                            break

                self.myAgent.db_mutex.release()
                content = "((result " + self.msg.getContent().strip("\n")[1:-1]
                if len(result) > 0:
                    content += " (sequence "
                    for i in result:
                        content += str(i) + " "
                    content += ")"
                else:
                    pass
                content += "))"
                self.myAgent.DEBUG("Found " + str(len(result)) + " services", 'ok')
                for d in result:
                    self.myAgent.DEBUG(str(d), 'ok')

                reply.setPerformative("inform")
                reply.setContent(content)
                self.myAgent.send(reply)

                recvs = ""
                for r in reply.getReceivers():
                    recvs += str(r.getName())

                return 1

            else:
                # Content is in RDF/XML
                max = 50
                if self.content.action.argument.max_results:
                    try:
                        max_str = str(self.content.action.argument.max_results)
                        max = int(max_str)
                    except Exception, err:
                        # Ignoring the exception
                        self.myAgent.DEBUG("FAILURE: (internal-error) max-results is not an integer! ", 'error')
                        #co_error = ContentObject()
                        #co_error["error"] = '(internal-error "max-results is not an integer")'

                    result = []

                    if self.content.action.argument.df_agent_description:
                        try:
                            dad = DfAgentDescription(co=self.content.action.argument.df_agent_description)
                            self.myAgent.DEBUG("Searching for: " + str(dad) + " in ServiceDB: " + str(map(lambda s: str(s), self.myAgent.servicedb.values())))
                        except Exception, err:
                            self.myAgent.DEBUG("FAILURE: Could not extract DfAgentDescription from content: " + str(err), 'error')

                        self.myAgent.db_mutex.acquire()
                        if max in [-1, 0]:
                            # No limit
                            for agentid, dads in self.myAgent.servicedb.items():
                                self.myAgent.DEBUG("Comparing " + str(dad) + " WITH " + str(dads) + " ==> " + str(dads.match(dad)), 'ok')
                                if dads.match(dad):
                                    d = copy.copy(dads)
                                    if dad.services == []:
                                        d.services = dads.getServices()
                                    else:
                                        d.services = []
                                    for ss in dad.getServices():
                                        for s in dads.getServices():
                                            if s.match(ss):
                                                d.addService(s)
                                    result.append(d)
                        else:
                            max = abs(max)
                            for agentid, dads in self.myAgent.servicedb.items():
                                if max >= 0:
                                    if dads.match(dad):
                                        d = copy.copy(dads)
                                        if dad.services == []:
                                            d.services = dads.getServices()
                                        else:
                                            d.services = []
                                        for ss in dad.getServices():
                                            for s in dads.getServices():
                                                if s.match(ss):
                                                    d.addService(s)
                                        result.append(d)
                                        max -= 1
                                else:
                                    break
                        self.myAgent.db_mutex.release()

                    content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    content["fipa:result"] = []
                    for i in result:
                        content["fipa:result"].append(i.asContentObject())
                        self.myAgent.DEBUG(str(i), 'ok')
                    self.myAgent.DEBUG("Found " + str(len(result)) + " services.", 'ok')
                    reply.setPerformative("inform")
                    reply.setContentObject(content)
                    self.myAgent.send(reply)

                    #recvs = ""
                    #for r in reply.getReceivers():
                    #    recvs += str(r.getName())

                    return 1

    class ModifyBehaviour(Behaviour.OneShotBehaviour):

        def __init__(self, msg, content):
            Behaviour.OneShotBehaviour.__init__(self)
            self.msg = msg
            self.content = content

        def _process(self):

            #The DF agrees and then informs dummy of the successful execution of the action
            error = False
            co_error = False
            dad = None
            if "rdf" in self.msg.getLanguage():

                try:
                    co = self.msg.getContentObject()
                    dad = DfAgentDescription(co=co.action.argument)
                except KeyboardInterrupt, err:
                    co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_error["fipa:error"] = "missing-argument df-agent-description"

                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("refuse")
                    reply.setContentObject(co_error)
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("FAILURE: Could not extract DfAgentDescription from content: " + str(err), 'error')
                    return -1

                if dad and (dad.getAID().getName() != self.msg.getSender().getName()):
                    co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_error["fipa:error"] = "unauthorised"

                if co_error:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("refuse")
                    reply.setContentObject(co_error)
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("FAILURE: " + self.msg.getSender().getName() + " is UNAUTHORISED to modify service " + str(dad), 'warn')

                    return -1

                reply = self.msg.createReply()
                reply.setSender(self.myAgent.getAID())
                reply.setPerformative("agree")
                co = self.msg.getContentObject()
                co["fipa:done"] = "true"
                reply.setContentObject(co)
                self.myAgent.send(reply)

                if dad.getAID().getName() in self.myAgent.servicedb.keys():

                    try:
                        for ss in dad.getServices():
                            self.myAgent.db_mutex.acquire()
                            result = self.myAgent.servicedb[dad.getAID().getName()].updateService(ss)
                            self.myAgent.db_mutex.release()
                            if not result:
                                reply.setPerformative("failure")
                                co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                                co_error["fipa:error"] = "not-registered"
                                reply.setContentObject(co_error)
                                self.myAgent.send(reply)
                                self.myAgent.DEBUG("FAILURE: Could not modify service " + str(ss) + ". Service is NOT registered.", 'warn')
                    except Exception, err:
                        reply.setPerformative("failure")
                        co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                        co_error["fipa:error"] = "internal-error"
                        reply.setContentObject(co_error)
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: internal-error: " + str(err), 'error')
                        return -1

                    reply.setPerformative("inform")
                    co = self.msg.getContentObject()
                    co["fipa:done"] = "true"
                    reply.setContentObject(co)
                    self.myAgent.send(reply)

                    return 1

                else:
                    reply.setPerformative("failure")
                    co_error = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
                    co_error["fipa:error"] = "not-registered"
                    reply.setContentObject(co_error)
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("FAILURE: Could not modify service " + str(dad) + ". Agent has no registered services.", 'warn')
                    return -1

            else:
                #language is sl-0
                try:
                        dad = DF.DfAgentDescription(self.content.action.modify[0][1])
                except Exception, err:
                    error = "(missing-argument ams-agent-description)"
                    self.myAgent.DEBUG("FAILURE: Could not extract DfAgentDescription from content: " + str(err), 'error')

                if dad and (dad.getAID().getName() != self.msg.getSender().getName()):
                    error = "(unauthorised)"
                    self.myAgent.DEBUG("REFUSE: " + self.msg.getSender().getName() + " is not AUTHORISED to modify service " + str(dad), 'warn')

                if error:
                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("refuse")
                    reply.setContent("( " + self.msg.getContent() + error + ")")
                    self.myAgent.send(reply)

                    return -1

                else:

                    reply = self.msg.createReply()
                    reply.setSender(self.myAgent.getAID())
                    reply.setPerformative("agree")
                    reply.setContent("(" + str(self.msg.getContent()) + " true)")
                    self.myAgent.send(reply)

                if dad.getAID().getName() in self.myAgent.servicedb.keys():

                    try:
                        for ss in dad.getServices():
                            self.myAgent.db_mutex.acquire()
                            result = self.myAgent.servicedb[dad.getAID().getName()].updateService(ss)
                            self.myAgent.db_mutex.release()
                            if not result:
                                reply.setPerformative("failure")
                                reply.setContent("(" + self.msg.getContent() + "(not-registered))")
                                self.myAgent.send(reply)
                                self.myAgent.DEBUG("FAILURE: Could not modify service " + str(ss) + ". Service is NOT registered.", 'warn')
                    except Exception, err:
                        reply.setPerformative("failure")
                        reply.setContent("(" + self.msg.getContent() + "(internal-error))")
                        self.myAgent.send(reply)
                        self.myAgent.DEBUG("FAILURE: (internal-error) Modifying service: " + str(err), 'error')
                        return -1

                    reply.setPerformative("inform")
                    reply.setContent("(done " + self.msg.getContent() + ")")
                    self.myAgent.send(reply)

                    return 1

                else:
                    reply.setPerformative("failure")
                    reply.setContent("(" + self.msg.getContent() + "(not-registered))")
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("FAILURE: Could not modify service " + str(dad) + ". Agent has no registered services.", 'warn')
                    return -1

    def __init__(self, node, passw, server="localhost", port=5347, config={}):
        PlatformAgent.__init__(self, node, passw, server, port, config)
        #self.addAddress("http://"+self.getDomain()+":2099/acc")  # HACK

    def _setup(self):

        self.wui.start()
        self.servicedb = dict()
        self.db_mutex = thread.allocate_lock()

        #self.setDefaultBehaviour()
        db = self.DefaultBehaviour()
        mt = Behaviour.ACLTemplate()
        mt.setOntology("FIPA-Agent-Management")
        mt.setPerformative("request")
        mt.setProtocol('fipa-request')
        self.addBehaviour(db, Behaviour.MessageTemplate(mt))

        #create service events
        self.createEvent("DF:Service:Register")
        self.createEvent("DF:Service:UnRegister")


class DfAgentDescription:

    def __init__(self, content=None, co=None):
        #self.name = AID.aid()
        self.name = None
        self.services = []
        self.protocols = []
        self.ontologies = []
        self.languages = []
        self.lease_time = None
        self.scope = []

        if content:
            self.loadSL0(content)

        if co:
            if "df-agent-description" in co.keys():
                co = co["df-agent-description"]
            if co.name:
                self.name = AID.aid(co=co.name)
            if co.services:
                self.services = []
                if "ContentObject" in str(type(co.services)):
                    self.services.append(ServiceDescription(co=co.services))
                else:
                    # List
                    for s in co.services:
                        self.services.append(ServiceDescription(co=s))
            if co.lease_time:
                self.lease_time = co.lease_time
            if "lease-time" in co.keys():
                self.lease_time = co["lease-time"]
            if co.protocols:
                self.protocols = copy.copy(co.protocols)
            if co.ontologies:
                self.ontologies = copy.copy(co.ontologies)
            if co.languages:
                self.languages = copy.copy(co.languages)
            if co.scope:
                self.scope = copy.copy(co.scope)

    def asContentObject(self):
        """
        Returns a version of the DAD in ContentObject format
        """
        co = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
        if self.name:
            co["name"] = self.name.asContentObject()
        else:
            co["name"] = AID.aid().asContentObject()
        if self.lease_time:
            co["lease-time"] = str(self.lease_time)
        if self.protocols:
            co["protocols"] = copy.copy(self.protocols)
        if self.services:
            co["services"] = []
            for s in self.services:
                co["services"].append(s.asContentObject())
        if self.ontologies:
            co["ontologies"] = copy.copy(self.ontologies)
        if self.languages:
            co["languages"] = copy.copy(self.languages)
        if self.scope:
            co["scope"] = copy.copy(self.scope)

        return co

    def asRDFXML(self):
        """
        returns a printable version of the DAD in RDF/XML format
        """
        return str(self.asContentObject())

    def getAID(self):
        return self.name

    def getName(self):
        if self.name is not None:
            return self.name.getName()
        else:
            return AID.aid()

    def setAID(self, a):
        self.name = a

    def getServices(self):
        return self.services

    def addService(self, s):
        #FIX
        for ss in self.services:
            assert not ss.match(s)
        self.services.append(s)
        for p in s.getProtocols():
            if p not in self.protocols:
                self.addProtocol(p)
        for o in s.getOntologies():
            if o not in self.ontologies:
                self.addOntologies(o)
        for l in s.getLanguages():
            if l not in self.languages:
                self.addLanguage(l)

    def delService(self, s):
        index = None
        for i in range(len(self.services)):
            if self.services[i].match(s):
                index = i
                break
        if index is not None:
            self.services.pop(i)
        else:
            return False
        for p in s.getProtocols():
            if p in self.protocols:
                self.protocols.remove(p)
        for p in s.getOntologies():
            if p in self.ontologies:
                self.ontologies.remove(p)
        for p in s.getLanguages():
            if p in self.languages:
                self.languages.remove(p)
        return True

    def updateService(self, s):
        found = False
        for ss in self.services:
            if s.getName() == ss.getName():
                found = True
                if s.getType():
                    ss.setType(s.getType())
                if s.getProtocols():
                    ss.protocols = s.getProtocols()
                    for p in s.getProtocols():
                        if p not in self.protocols:
                            self.addProtocol(p)
                if s.getOntologies():
                    ss.ontologies = s.getOntologies()
                    for o in s.getOntologies():
                        if o not in self.ontologies:
                            self.addOntologies(o)
                if s.getLanguages():
                    ss.languages = s.getLanguages()
                    for l in s.getLanguages():
                        if l not in self.languages:
                            self.addLanguage(l)
                if s.getOwnership():
                    ss.setOwnership(s.getOwnership())
                for k, v in s.getProperties().items():
                    ss.addProperty(k, v)
        return found

    def getProtocols(self):
        return self.protocols

    def addProtocol(self, p):
        if p not in self.protocols:
            self.protocols.append(p)

    def getOntologies(self):
        return self.ontologies

    def addOntologies(self, o):
        if o not in self.ontologies:
            self.ontologies.append(o)

    def getLanguages(self):
        return self.languages

    def addLanguage(self, l):
        if l not in self.languages:
            self.languages.append(l)

    def getLeaseTime(self):
        return self.lease_time

    def setLeaseTime(self, lt):
        self.lease_time = lt

    def getScope(self):
        return self.scope

    def addScope(self, s):
        self.scope = s

    #def __eq__(self,y):
    def match(self, y):

        if y.name:
            if not self.getAID().match(y.name):
                return False
        if y.protocols:
            for p in y.protocols:
                if not (p in self.protocols):
                    return False
        if y.ontologies:
            for o in y.ontologies:
                if not (o in self.ontologies):
                    return False
        if y.languages:
            for l in y.languages:
                if not (l in self.languages):
                    return False
        if y.lease_time:
            if self.lease_time != y.getLeaseTime():
                return False
        if y.scope:
            if self.scope != y.getScope():
                return False

        if len(self.services) > 0 and len(y.getServices()) > 0:
            for i in y.services:
                matched = False
                for j in self.getServices():
                    #if i == j:
                    if j.match(i):
                        matched = True
                        break
                if not matched:
                    return False
            return True
        else:
            return True

    def __ne__(self, y):
        return not self == y

    def loadSL0(self, content):
        if content is not None:
            if "name" in content:
                self.name = AID.aid()
                self.name.loadSL0(content.name)

            if "services" in content:
                #TODO: the parser only detects 1 service-description!!!
                self.services = []  # ServiceDescription()
                #self.services.loadSL0(content.services.set['service-description'])
                for i in content.services.set:
                    sd = ServiceDescription(i[1])
                    self.services.append(sd)

            if "protocols" in content:
                self.protocols = content.protocols.set.asList()

            if "ontologies" in content:
                self.ontologies = content.ontologies.set.asList()

            if "languages" in content:
                self.languages = content.languages.set.asList()

            if "lease-time" in content:
                self.lease_time = BasicFipaDateTime.BasicFipaDateTime()
                #self.lease_time.fromString(content["lease-time"])
                self.lease_time = content["lease-time"][0]

            if "scope" in content:
                self.scope = content["scope"][0]

    def __str__(self):
        return self.asRDFXML()

    def asSL0(self):

        sb = ''
        if self.name is not None:
            sb = sb + ":name " + str(self.name) + "\n"

        if len(self.protocols) > 0:
            sb = sb + ":protocols \n(set\n"
            for i in self.protocols:
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"

        if len(self.ontologies) > 0:
            sb = sb + ":ontologies \n(set\n"
            for i in self.ontologies:
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"

        if len(self.languages) > 0:
            sb = sb + ":languages \n(set\n"
            for i in self.languages:
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"

        if self.lease_time is not None:
            sb = sb + ":lease-time " + str(self.lease_time) + '\n'

        if self.scope is not None:
            sb = sb + ":scope " + str(self.scope) + '\n'

        if len(self.services) > 0:
            sb = sb + ":services \n(set\n"
            for i in self.services:
                sb = sb + str(i.asSL0()) + '\n'
            sb = sb + ")\n"

        sb = "(df-agent-description \n" + sb + ")\n"
        return sb


class ServiceDescription:

    def __init__(self, content=None, co=None):

        self.name = None
        self.type = None
        self.protocols = []
        self.ontologies = []
        self.languages = []
        self.ownership = None
        self.properties = {}

        if content is not None:
            self.loadSL0(content)

        if co:
            #print "SD:",co.pprint()
            if co.name:
                self.name = co.name
            if co.type:
                self.type = co.type
            if co.protocols:
                self.protocols = copy.copy(co.protocols)
            if co.ontologies:
                self.ontologies = copy.copy(co.ontologies)
            if co.languages:
                self.languages = copy.copy(co.languages)
            if co.ownership:
                self.ownership = co.ownership
            if co.properties:
                #print co.properties
                for k, v in co.properties.items():
                    if ":" in k:
                        ns, key = k.split(":")
                    else:
                        key = k
                    self.properties[key] = v

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getType(self):
        return self.type

    def setType(self, t):
        self.type = t

    def getProtocols(self):
        return self.protocols

    def addProtocol(self, p):
        if p not in self.protocols:
            self.protocols.append(p)

    def getOntologies(self):
        return self.ontologies

    def addOntologies(self, o):
        if o not in self.ontologies:
            self.ontologies.append(o)

    def getLanguages(self):
        return self.languages

    def addLanguage(self, l):
        if l not in self.languages:
            self.languages.append(l)

    def getOwnership(self):
        return self.ownership

    def setOwnership(self, o):
        self.ownership = o  # .lower()

    def getProperties(self):
        return self.properties

    def getProperty(self, prop):
        if prop in self.properties.keys():
            return self.properties[prop]
        return None

    def addProperty(self, k, value):
        if ":" in k:
            ns, key = k.split(":")
        else:
            key = k
        self.properties[key] = value

    def __eq__(self, y):
        return self.match(y)

    def match(self, y):

        if y.name:
            if self.name != y.getName():
                return False
        if y.type:
            if self.type != y.getType():
                return False
        if y.protocols:
            for p in y.protocols:
                if not (p in self.protocols):
                    return False
        if y.ontologies:
            for o in y.ontologies:
                if not (o in self.ontologies):
                    return False
        if y.languages:
            for l in y.languages:
                if not (l in self.languages):
                    return False
        if y.ownership:
            if self.ownership != y.getOwnership():
                return False
        #properties
        for k, v in y.properties.items():
            if k in self.getProperties().keys():
                if y.getProperty(k) != v:
                    return False
            else:
                return False
        return True

    def __ne__(self, y):
        return not self == y

    def loadSL0(self, content):
        if content is not None:
            if "name" in content:
                self.name = str(content.name[0]).lower()

            if "type" in content:
                self.type = str(content.type[0]).lower()

            if "protocols" in content:
                self.protocols = content.protocols.set.asList()

            if "ontologies" in content:
                self.ontologies = content.ontologies.set.asList()

            if "languages" in content:
                self.languages = content.languages.set.asList()

            if "ownership" in content:
                self.ownership = content.ownership

            if "properties" in content:
                for p in content.properties.set.asDict().values():
                    self.properties[str(p['name']).lower().strip("[']")] = str(p['value']).lower().strip("[']")

    def __str__(self):
        return self.asRDFXML()

    def asSL0(self):

        sb = ""
        if self.name is not None:
            sb += ":name " + str(self.name) + "\n"
        if self.type:
            sb += ":type " + str(self.type) + "\n"

        if len(self.protocols) > 0:
            sb += ":protocols \n(set\n"
            for i in self.protocols:
                sb += str(i) + " "
            sb = sb + ")\n"

        if len(self.ontologies) > 0:
            sb = sb + ":ontologies \n(set\n"
            for i in self.ontologies:
                sb += str(i) + " "
            sb = sb + ")\n"

        if len(self.languages) > 0:
            sb = sb + ":languages \n(set\n"
            for i in self.languages:
                sb += str(i) + " "
            sb += ")\n"

        if self.ownership:
            sb += ":ownership " + str(self.ownership) + "\n"

        if len(self.properties) > 0:
            sb += ":properties \n (set\n"
            for k, v in self.properties.items():
                sb += " (property :name " + str(k) + " :value " + str(v) + ")\n"
            sb += ")\n"

        if sb != "":
            sb = "(service-description\n" + sb + ")\n"
        return sb

    def asContentObject(self):
        """
        Returns a version of the SD in ContentObject format
        """
        co = ContentObject()  # namespaces={"http://www.fipa.org/schemas/fipa-rdf0#":"fipa:"})
        if self.name:
            co["name"] = str(self.name)
        else:
            co["name"] = ""
        if self.type:
            co["type"] = str(self.type)
        else:
            co["type"] = ""
        if self.protocols:
            co["protocols"] = copy.copy(self.protocols)
        if self.ontologies:
            co["ontologies"] = copy.copy(self.ontologies)
        if self.languages:
            co["languages"] = copy.copy(self.languages)
        if self.ownership:
            co["ownership"] = self.ownership
        if self.properties != {}:
            co["properties"] = ContentObject()  # namespaces={"http://www.fipa.org/schemas/fipa-rdf0#":"fipa:"})
            for k, v in self.properties.items():
                if ":" in k:
                    ns, key = k.split(":")
                else:
                    key = k
                co["properties"][str(key)] = v
        return co

    def asRDFXML(self):
        """
        returns a printable version of the SD in RDF/XML format
        """
        return str(self.asContentObject())


class Service:

    def __init__(self, name=None, owner=None, P=[], Q=[], inputs=[], outputs=[], description=None, ontology=None, dad=None, co=None):

        self.name = name
        self.owner = owner
        self.dad = DfAgentDescription()
        sd = ServiceDescription()

        self.inputs = inputs
        self.outputs = outputs

        if co and "service" in co.keys():
            if co.service.name:
                name = co.service.name
            if co.service.owner:
                owner = AID.aid(co=co.service.owner)
            if co.service.ontology:
                ontology = co.service.ontology
            if co.service.P:
                P = co.service.P
            if co.service.Q:
                Q = co.service.Q
            if co.service.description:
                description = co.service.description

        #self.name  = name
        #self.owner = owner
        #self.dad = DfAgentDescription()
        if owner:
            self.dad.setAID(owner)
        if ontology:
            self.dad.addOntologies(ontology)

        if name is not None:
            sd.setName(name)
            if owner is not None:
                sd.setOwnership(owner.getName())
            if P != []:
                sd.addProperty("P", P)
            if Q != []:
                sd.addProperty("Q", Q)
            if inputs != []:
                sd.addProperty("inputs", inputs)
            if outputs != []:
                sd.addProperty("outputs", outputs)
            if ontology is not None:
                sd.addOntologies(str(ontology))
            if description is not None:
                sd.addProperty("description", str(description))

            self.dad.addService(sd)

        if dad:
            self.setDAD(dad)

    def setName(self, name):
        self.name = name
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            s.setName(name)
            services.append(s)
        self.dad.services = services

    def getName(self):
        return self.name

    def setOwner(self, owner):
        self.owner = owner
        self.dad.setAID(owner)
        if self.dad.getServices() != []:
            services = []
            for s in self.dad.getServices():
                s.setOwnership(owner.getName())
                services.append(s)
            self.dad.services = services

    def getOwner(self):
        return self.owner

    def setOntology(self, ontology):
        self.dad.addOntologies(ontology)
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            s.addOntologies(ontology)
            services.append(s)
        self.dad.services = services

    def getOntology(self):
        return self.dad.getOntologies()

    def addP(self, P):
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            p = s.getProperty("P")
            if not p:
                p = []
            p.append(P)
            s.addProperty('P', p)
            services.append(s)
        self.dad.services = services

    def getP(self):
        if self.dad.getServices() == []:
            return []
        p = self.dad.getServices()[0].getProperty("P")
        if p is None:
            return []
        else:
            return p

    def addQ(self, Q):
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            q = s.getProperty("Q")
            if not q:
                q = []
            q.append(Q)
            s.addProperty('Q', q)
            services.append(s)
            self.dad.services = services

    def getQ(self):
        if self.dad.getServices() == []:
            return []
        q = self.dad.getServices()[0].getProperty("Q")
        if q is None:
            return []
        else:
            return q

    def setInputs(self, inputs):
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            s.properties['inputs'] = inputs
            services.append(s)
        self.dad.services = services

    def getInputs(self):
        if self.dad.getServices() == []:
            return []
        return self.dad.getServices()[0].getProperty("inputs")

    def setOutputs(self, outputs):
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            s.properties['outputs'] = outputs
            services.append(s)
        self.dad.services = services

    def getOutputs(self):
        if self.dad.getServices() == []:
            return []
        return self.dad.getServices()[0].getProperty("outputs")

    def setDescription(self, description):
        if self.dad.getServices() == []:
            self.dad.addService(ServiceDescription())
        services = []
        for s in self.dad.getServices():
            s.properties['description'] = description
            services.append(s)
        self.dad.services = services

    def getDescription(self):
        if self.dad.getServices() == []:
            return []
        return self.dad.getServices()[0].getProperty("description")

    def getType(self):
        if self.dad.getServices() == []:
            return []
        return self.dad.getServices()[0].getType()

    def setType(self, typ):
        if self.dad.getServices() == []:
            return []
        self.dad.getServices()[0].setType(typ)

    def setDAD(self, dad):
        sd = dad.getServices()
        if len(sd) == 1:
            sd = sd[0]
        else:
            return None
        self.name = sd.getName()
        self.owner = dad.getAID()
        self.ontology = dad.getOntologies()

        self.dad = dad

    def getDAD(self):
        return self.dad

    def match(self, y):
        return y.dad.match(self.dad)

    def __eq__(self, y):
        if y is None:
            return False
        return y.match(self)

    def __ne__(self, y):
        return not self == y

    def __str__(self):
        return str(self.dad)

    def __repr__(self):
        return str(self.asContentObject())

    def asContentObject(self):

        co = ContentObject()
        co["service"] = ContentObject()
        if self.getName() is not None:
            co.service["name"] = self.getName()
        if self.getOwner() is not None:
            co.service["owner"] = self.getOwner().asContentObject()
        if self.getOntology() != []:
            co.service["ontology"] = self.getOntology()
        if self.getP() != []:
            co.service["P"] = self.getP()
        if self.getQ() != []:
            co.service["Q"] = self.getQ()
        if self.getDescription() is not None:
            co.service["description"] = self.getDescription()

        return co

    def asHTML(self):
        s = '<table class="servicesT" cellspacing="0">'
        s += '<tr><td class="servHd">Name</td><td class="servBodL">' + self.getName() + '</td></tr>'
        s += '<tr><td class="servHd">Owner</td><td class="servBodL">' + self.getOwner().getName() + '</td></tr>'
        if self.getType():
            s += '<tr><td class="servHd">Type</td><td class="servBodL">' + str(self.getType()) + '</td></tr>'
        if self.getDescription():
            s += '<tr><td class="servHd">Description</td><td class="servBodL">' + str(self.getDescription()) + '</td></tr>'
        if self.getOntology():
            s += '<tr><td class="servHd">Ontologies</td><td class="servBodL">' + str(self.getOntology()) + '</td></tr>'
        if self.getP():
            s += '<tr><td class="servHd">Preconditions</td><td class="servBodL">' + str(self.getP()) + '</td></tr>'
        if self.getQ():
            s += '<tr><td class="servHd">Postconditions</td><td class="servBodL">' + str(self.getQ()) + '</td></tr>'
        if self.getInputs():
            s += '<tr><td class="servHd">Inputs</td><td class="servBodL">' + str(self.getInputs()) + '</td></tr>'
        if self.getOutputs():
            s += '<tr><td class="servHd">Outputs</td><td class="servBodL">' + str(self.getOutputs()) + '</td></tr>'
        s += '</table>'

        return s
