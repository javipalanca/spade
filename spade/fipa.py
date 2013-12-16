# -*- coding: utf-8 -*-
import Behaviour
import SL0Parser
import DF
from content import *
import random


class SearchAgentBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg, AAD):
        Behaviour.OneShotBehaviour.__init__(self)
        self.AAD = AAD
        self.result = None
        self.finished = False
        self._msg = msg
        self.p = SL0Parser.SL0Parser()

    def _process(self):
        self._msg.addReceiver(self.myAgent.getAMS())
        self._msg.setPerformative('request')
        self._msg.setLanguage('rdf')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
        content["fipa:action"] = ContentObject()
        content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
        content["fipa:action"]["fipa:act"] = "search"
        content["fipa:action"]["fipa:argument"] = self.AAD.asContentObject()
        self._msg.setContentObject(content)

        self.myAgent.send(self._msg)
        msg = self._receive(True, 10)
        if msg is None or str(msg.getPerformative()) != 'agree':
            try:
                aadname = str(self.AAD.getAID().getName())
            except:
                aadname = "<unknown>"
            self.myAgent.DEBUG("There was an error searching the Agent " + aadname + "(not agree)", "warn")
            self.finished = True
            return None
        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'inform':
            try:
                aadname = str(self.AAD.getAID().getName())
            except:
                aadname = "<unknown>"
            self.myAgent.DEBUG("There was an error searching the Agent " + aadname + "(not inform)", "warn")
            self.finished = True
            return None
        else:
            try:
                co = msg.getContentObject()
                self.result = []
                from AMS import AmsAgentDescription
                for i in co["fipa:result"]:
                    self.result.append(AmsAgentDescription(co=i))

            except Exception, e:
                self.DEBUG("Parse Exception: " + str(e), "err")
                self.result = []
                return None

        self.finished = True


class ModifyAgentBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg, AAD):
        Behaviour.OneShotBehaviour.__init__(self)
        self.AAD = AAD
        self.result = None
        self.finished = False
        self._msg = msg

    def _process(self):
        p = SL0Parser.SL0Parser()
        self._msg.addReceiver(self.myAgent.getAMS())
        self._msg.setPerformative('request')
        self._msg.setLanguage('rdf')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
        content["fipa:action"] = ContentObject()
        content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
        content["fipa:action"]["fipa:act"] = "modify"
        content["fipa:action"]["fipa:argument"] = self.AAD.asContentObject()
        self._msg.setContentObject(content)

        self.myAgent.send(self._msg)

        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'agree':
            self.myAgent.DEBUG("There was an error modifying the requested Agent (not agree)", "warn")
            self.result = False
            return False
        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'inform':
            self.myAgent.DEBUG("There was an error modifying the requested Agent (not inform)", "warn")
            self.myAgent.DEBUG(str(msg.getContent()))
            self.result = False
            return False
        self.result = True
        return True


class getPlatformInfoBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg):
        Behaviour.OneShotBehaviour.__init__(self)
        self._msg = msg
        self.result = None
        self.finished = False

    def _process(self):
        msg = self._msg
        msg.addReceiver(self.myAgent.getAMS())
        msg.setPerformative('request')
        msg.setLanguage('rdf')
        msg.setProtocol('fipa-request')
        msg.setOntology('FIPA-Agent-Management')

        content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
        content["fipa:action"] = ContentObject()
        content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
        content["fipa:action"]["fipa:act"] = "get-description"
        msg.setContentObject(content)

        self.myAgent.send(msg)

        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'agree':
            self.myAgent.DEBUG("There was an error getting platform info (not-agree)", "warn")
            return False
        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'inform':
            self.myAgent.DEBUG("There was an error getting platform info (not-inform)", "warn")
            return False

        self.result = msg.getContentObject()


class registerServiceBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg, DAD, otherdf=None):
        Behaviour.OneShotBehaviour.__init__(self)
        self._msg = msg
        self.DAD = DAD
        self.result = None
        self.finished = False
        self.otherdf = otherdf

    def _process(self):
        force_sl0 = False
        if self.otherdf and isinstance(self.otherdf, AID.aid):
            self._msg.addReceiver(self.otherdf)
            force_sl0 = True
        else:
            self._msg.addReceiver(self.myAgent.getDF())
            self._msg.setPerformative('request')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

        if force_sl0:
            self._msg.setLanguage('fipa-sl0')
            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(register " + str(self.DAD) + ")"
            content += " ))"
            self._msg.setContent(content)

        else:
            self._msg.setLanguage('rdf')
            content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
            content["fipa:action"] = ContentObject()
            content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
            content["fipa:action"]["fipa:act"] = "register"
            content["fipa:action"]["fipa:argument"] = self.DAD.asContentObject()
            self._msg.setContentObject(content)

        self.myAgent.send(self._msg)

        self.result = True
        msg = self._receive(True, 30)
        print msg
        if msg is None or msg.getPerformative() not in ['agree', 'inform']:
            self.myAgent.DEBUG("There was an error registering the service " + str(self.DAD) + "(not agree)", "warn")
            self.result = False
            return False
        elif msg is None or msg.getPerformative() == 'agree':
            msg = self._receive(True, 20)
            if msg is None or msg.getPerformative() != 'inform':
                if not msg:
                    self.DEBUG("There was an error registering the Service " + str(self.DAD) + ". (timeout)", "warn")
                elif msg.getPerformative() == 'failure':
                    self.DEBUG("There was an error registering the Service " + str(self.DAD) + ". Failure: " + msg.getContentObject()['fipa:error'], "warn")
                else:
                    self.DEBUG("There was an error registering the Service " + str(self.DAD) + ". (not inform)", "warn")
                self.result = False
                return False

        self.result = True


class deregisterServiceBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg, DAD, otherdf=None):
        Behaviour.OneShotBehaviour.__init__(self)
        self._msg = msg
        self.DAD = DAD
        self.result = None
        self.finished = False
        self.otherdf = otherdf

    def _process(self):
        force_sl0 = False
        if self.otherdf and isinstance(self.otherdf, AID.aid):
            self._msg.addReceiver(self.otherdf)
            force_sl0 = True
        else:
            self._msg.addReceiver(self.myAgent.getDF())
        self._msg.setPerformative('request')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        if force_sl0:
            self._msg.setLanguage('fipa-sl0')
            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(deregister " + str(self.DAD) + ")"
            content += " ))"
            self._msg.setContent(content)

        else:
            self._msg.setLanguage('rdf')
            content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
            content["fipa:action"] = ContentObject()
            content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
            content["fipa:action"]["fipa:act"] = "deregister"
            content["fipa:action"]["fipa:argument"] = self.DAD.asContentObject()
            self._msg.setContentObject(content)

        self.myAgent.send(self._msg)

        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() not in ['agree', 'inform']:
            self.myAgent.DEBUG("There was an error deregistering the Service " + str(self.DAD) + ". (not-agree)", "warn")
            self.result = False
            return
        elif msg is None or msg.getPerformative() == 'agree':
            msg = self._receive(True, 20)
            if msg is None or msg.getPerformative() != 'inform':
                if not msg:
                    self.DEBUG("There was an error deregistering the Service " + str(self.DAD) + ". (timeout)", "warn")
                elif msg.getPerformative() == 'failure':
                    self.DEBUG("There was an error deregistering the Service " + str(self.DAD) + ". failure:" + msg.getContentObject()['fipa:error'], "warn")
                else:
                    self.DEBUG("There was an error deregistering the Service " + str(self.DAD) + ". (not inform)", "warn")
                self.result = False
                return

        self.result = True


class searchServiceBehaviour(Behaviour.OneShotBehaviour):

    def __init__(self, msg, DAD):
        Behaviour.OneShotBehaviour.__init__(self)
        self._msg = msg
        self.DAD = DAD
        self.result = None
        self.finished = False

    def _process(self):
        try:
            self._msg.addReceiver(self.myAgent.getDF())
            self._msg.setPerformative('request')
            self._msg.setLanguage('rdf')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')

            content = ContentObject()
            content["fipa:action"] = ContentObject()
            content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
            content["fipa:action"]["fipa:act"] = "search"
            content["fipa:action"]["fipa:argument"] = ContentObject()
            content["fipa:action"]["fipa:argument"]["fipa:max_results"] = "0"
            content["fipa:action"]["fipa:argument"]["fipa:df_agent_description"] = self.DAD.asContentObject()
            self._msg.setContentObject(content)

            self.myAgent.send(self._msg)

            msg = self._receive(True, 20)
            if msg is None:
                self.DEBUG("There was an error searching the Service (timeout on agree)", "warn")
                return
            elif msg.getPerformative() not in ['agree', 'inform']:
                self.DEBUG("There was an error searching the Service (not agree) Failure: " + str(msg.getContentObject()["fipa:error"]), "warn")
                return
            elif msg.getPerformative() == 'agree':
                msg = self._receive(True, 10)
                if msg is None:
                    self.DEBUG("There was an error searching the Service (timeout on inform)", "warn")
                    return
                elif msg.getPerformative() != 'inform':
                    self.DEBUG("There was an error searching the Service (not inform) " + str(msg.getContentObject()['fipa:error']), "warn")
                    return

            content = msg.getContentObject()
            self.result = []
            for dfd in content.result:
                d = DF.DfAgentDescription(co=dfd)
                self.result.append(d)

        except Exception, e:
            self.DEBUG("Exception searching service: " + str(e), "err")
            return

        return


class modifyServiceBehaviour(Behaviour.OneShotBehaviour):
    def __init__(self, msg, DAD):
        Behaviour.OneShotBehaviour.__init__(self)
        self._msg = msg
        self.DAD = DAD
        self.result = None

    def _process(self):
        self._msg.addReceiver(self.myAgent.getDF())
        self._msg.setPerformative('request')
        self._msg.setLanguage('rdf')
        self._msg.setProtocol('fipa-request')
        self._msg.setOntology('FIPA-Agent-Management')

        content = ContentObject(namespaces={"http://www.fipa.org/schemas/fipa-rdf0#": "fipa:"})
        content["fipa:action"] = ContentObject()
        content["fipa:action"]["fipa:actor"] = self.myAgent.getAID().asContentObject()
        content["fipa:action"]["fipa:act"] = "modify"
        content["fipa:action"]["fipa:argument"] = self.DAD.asContentObject()
        self._msg.setContentObject(content)

        self.myAgent.send(self._msg)

        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'agree':
            self.DEBUG("There was an error modifying the Service. (not agree) ", "warn")
            if msg:
                self.DEBUG(msg.getContentObject()['fipa:error'], "warn")
            self.result = False
            return
        msg = self._receive(True, 20)
        if msg is None or msg.getPerformative() != 'inform':
            self.DEBUG("There was an error modifying the Service. (not inform) " + str(msg.getContentObject()['fipa:error']), "warn")
            self.result = False
            return
        self.result = True
        return
