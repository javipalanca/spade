# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

sys.path.append('../..')

import spade

host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.msg = None


class SendMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@" + host, ["xmpp://b@" + host]))
        msg.setContent("testSendMsg")

        self.myAgent.send(msg)


class EventMsgBehav(spade.Behaviour.EventBehaviour):

    def _process(self):
        self.myAgent.msg = self._receive(block=True)


class BasicTestCase(unittest.TestCase):

    def setUp(self):

        self.Aaid = spade.AID.aid("a@" + host, ["xmpp://a@" + host])
        self.Baid = spade.AID.aid("b@" + host, ["xmpp://b@" + host])

        self.a = MyAgent("a@" + host, "secret")
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        self.b.start()

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testSendMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(EventMsgBehav(), t)
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


if __name__ == "__main__":
    unittest.main()
