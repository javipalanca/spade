# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.pi = None
        self.msg = None


class GetPIBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        self.myAgent.pi = self.myAgent.getPlatformInfo()


class SendMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["xmpp://b@" + host]))
        msg.setContent("testSendMsg")

        self.myAgent.send(msg)


class RecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        self.myAgent.msg = self._receive(block=True, timeout=10)


class SendAndRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["xmpp://b@" + host]))
        msg.setContent("testSendAndRecvMsg")

        self.myAgent.send(msg)
        self.myAgent.msg = None
        self.myAgent.msg = self._receive(block=True, timeout=10)


class AnswerMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = None
        msg = self._receive(block=True, timeout=10)
        if msg is not None:
            content = msg.getContent()
            msg = msg.createReply()
            msg.setContent(content)
            self.myAgent.send(msg)


class BasicTestCase(unittest.TestCase):

    def setUp(self):

        self.Aaid = spade.AID.aid("a@" + host, ["xmpp://a@" + host])
        self.Baid = spade.AID.aid("b@" + host, ["xmpp://b@" + host])

        self.a = MyAgent("a@" + host, "secret")
        #self.a.setDebug()
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        self.b.start()

        #self.rdf = """<rdf:ap-description><rdf:ap-services><rdf:ap-service><rdf:type>fipa.agent-management.ams</rdf:type><rdf:addresses>acc.127.0.0.1</rdf:addresses><rdf:name>xmpp://ams.127.0.0.1</rdf:name></rdf:ap-service></rdf:ap-services><rdf:name>xmpp://acc.127.0.0.1</rdf:name></rdf:ap-description>"""
        self.rdf = """<rdf:RDF xmlns:fipa="http://www.fipa.org/schemas/fipa-rdf0#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:ap-description><rdf:ap-services list="true"><rdf:ap-services><rdf:ap-service><rdf:type>fipa.agent-management.ams</rdf:type><rdf:addresses list="true"><rdf:addresses>acc.127.0.0.1</rdf:addresses></rdf:addresses><rdf:name>xmpp://ams.127.0.0.1</rdf:name></rdf:ap-service></rdf:ap-services></rdf:ap-services><rdf:name>xmpp://acc.127.0.0.1</rdf:name></rdf:ap-description></rdf:RDF>"""
        #self.pi = spade.content.RDFXML2CO(self.rdf)

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testGetPlatformInfo(self):
        self.a.addBehaviour(GetPIBehav(), None)
        counter = 0
        while self.a.pi is None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.pi, None)
        from coTestCase import isEqualXML
        #self.assertEqual( str(self.a.pi),  self.rdf) # 'Incorrect Platform Info'
        assert isEqualXML(str(self.a.pi.asRDFXML()), self.rdf)

    def testSendMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(RecvMsgBehav(), t)
        self.a.addBehaviour(SendMsgBehav(), None)
        counter = 0
        while self.b.msg is None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg, None)
        self.assertEqual(self.b.msg.getContent(), "testSendMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()), 1)
        self.assertEqual(self.b.msg.getReceivers()[0], self.Baid)

    def testSendAndRecvMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(AnswerMsgBehav(), t)
        template.setSender(self.Baid)
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(SendAndRecvMsgBehav(), t)
        counter = 0
        while self.a.msg is None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.msg, None)
        self.assertEqual(self.a.msg.getContent(), "testSendAndRecvMsg")


if __name__ == "__main__":
    unittest.main()
