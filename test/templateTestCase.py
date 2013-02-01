# -*- coding: utf-8 -*-
import unittest

import spade
from spade.AID import aid
import xmpp

host = "127.0.0.1"


class TemplateTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testACLTemplateMatchTrue(self):
        acltemplate = spade.Behaviour.ACLTemplate()
        acltemplate.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        acltemplate.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        acltemplate.setPerformative("query")

        message = spade.ACLMessage.ACLMessage()
        message.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        message.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        message.setPerformative("query")

        mt = spade.Behaviour.MessageTemplate(acltemplate)

        self.assertTrue(mt.match(message))

    def testACLTemplateMatchFalse(self):
        acltemplate = spade.Behaviour.ACLTemplate()
        acltemplate.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        acltemplate.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        acltemplate.setPerformative("query")

        message = spade.ACLMessage.ACLMessage()
        message.setSender(aid(name="sender2@host", addresses=["sender2@host"]))
        message.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        message.setPerformative("query")

        mt = spade.Behaviour.MessageTemplate(acltemplate)

        self.assertFalse(mt.match(message))

    def testACLMessageMatchTrue(self):
        aclmsg = spade.ACLMessage.ACLMessage()
        aclmsg.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        aclmsg.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        aclmsg.setPerformative("query")

        message = spade.ACLMessage.ACLMessage()
        message.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        message.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        message.setPerformative("query")
        message.setConversationId(aclmsg.getConversationId())

        mt = spade.Behaviour.MessageTemplate(aclmsg)

        self.assertTrue(mt.match(message))

    def testACLMessageMatchFalse(self):
        aclmsg = spade.ACLMessage.ACLMessage()
        aclmsg.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        aclmsg.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        aclmsg.setPerformative("query")

        message = spade.ACLMessage.ACLMessage()
        message.setSender(aid(name="sender2@host", addresses=["sender2@host"]))
        message.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        message.setPerformative("query")
        message.setConversationId(aclmsg.getConversationId())

        mt = spade.Behaviour.MessageTemplate(aclmsg)

        self.assertFalse(mt.match(message))

    def testXMPPMessageMatchTrue(self):
        xmpptemplate = xmpp.Message()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))

        message = xmpp.Message()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertTrue(mt.match(message))

    def testXMPPMessageMatchFalse(self):
        xmpptemplate = xmpp.Message()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))

        message = xmpp.Message()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv2@host"))

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertFalse(mt.match(message))


    def testXMPPPresenceMatchTrue(self):
        xmpptemplate = xmpp.Presence()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))
        xmpptemplate.setType("unavailable")
        xmpptemplate.setShow("myShow msg")
        xmpptemplate.setStatus("I am sleeping")

        message = xmpp.Presence()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))
        message.setType("unavailable")
        message.setShow("myShow msg")
        message.setStatus("I am sleeping")

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertTrue(mt.match(message))

    def testXMPPPresenceMatchFalse(self):
        xmpptemplate = xmpp.Presence()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))
        xmpptemplate.setType("unavailable")
        xmpptemplate.setShow("myShow msg")
        xmpptemplate.setStatus("I am sleeping")

        message = xmpp.Presence()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))
        message.setType("unavailable")
        message.setShow("myShow msg")
        message.setStatus("Back to work!")

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertFalse(mt.match(message))


    def testXMPPPresenceMatchFalseByNS(self):
        xmpptemplate = xmpp.Presence()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))
        xmpptemplate.setType("unavailable")
        xmpptemplate.setShow("myShow msg")
        xmpptemplate.setStatus("I am sleeping")
        xmpptemplate.setNamespace(xmpp.NS_MUC_OWNER)

        message = xmpp.Presence()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))
        message.setType("unavailable")
        message.setShow("myShow msg")
        message.setStatus("I am sleeping")
        xmpptemplate.setNamespace(xmpp.NS_MUC_USER)

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertFalse(mt.match(message))

    def testXMPPIqMatchTrue(self):
        xmpptemplate = xmpp.Iq()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))
        xmpptemplate.setType("set")

        message = xmpp.Iq()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))
        message.setType("set")

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertTrue(mt.match(message))

    def testXMPPIqMatchFalse(self):
        xmpptemplate = xmpp.Iq()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))
        xmpptemplate.setType("set")

        message = xmpp.Iq()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv1@host"))
        message.setType("get")

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertFalse(mt.match(message))


    def testACLTemplateMatchAND(self):
        t1 = spade.Behaviour.ACLTemplate()
        t1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        t2 = spade.Behaviour.ACLTemplate()
        t2.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        t2.setPerformative("query")

        mt = spade.Behaviour.MessageTemplate(t1 & t2)

        m1= spade.ACLMessage.ACLMessage()
        m1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))

        self.assertFalse(mt.match(m1))

        m2= spade.ACLMessage.ACLMessage()
        m2.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        m2.setPerformative("query")

        self.assertFalse(mt.match(m2))

        m3= spade.ACLMessage.ACLMessage()
        m3.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        m3.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        m3.setPerformative("query")

        self.assertTrue(mt.match(m3))

    def testACLTemplateMatchOR(self):
        t1 = spade.Behaviour.ACLTemplate()
        t1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        t2 = spade.Behaviour.ACLTemplate()
        t2.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        t2.setPerformative("query")

        mt = spade.Behaviour.MessageTemplate(t1 | t2)

        m1= spade.ACLMessage.ACLMessage()
        m1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))

        self.assertTrue(mt.match(m1))

        m2= spade.ACLMessage.ACLMessage()
        m2.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        m2.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        m2.setPerformative("query")

        self.assertTrue(mt.match(m2))

        m3= spade.ACLMessage.ACLMessage()
        m3.setSender(aid(name="sender2@host", addresses=["sender2@host"]))
        m3.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        m3.setPerformative("inform")

        self.assertFalse(mt.match(m3))

    def testACLTemplateMatchNOT(self):
        t1 = spade.Behaviour.ACLTemplate()
        t1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        t1.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        t1.setPerformative("query")

        mt = spade.Behaviour.MessageTemplate( ~t1 )

        m1= spade.ACLMessage.ACLMessage()
        m1.setSender(aid(name="sender1@host", addresses=["sender1@host"]))

        self.assertTrue(mt.match(m1))

        m2= spade.ACLMessage.ACLMessage()
        m2.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        m2.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))

        self.assertTrue(mt.match(m2))

        m3= spade.ACLMessage.ACLMessage()
        m3.setSender(aid(name="sender1@host", addresses=["sender1@host"]))
        m3.addReceiver(aid(name="recv1@host", addresses=["recv1@host"]))
        m3.setPerformative("query")

        self.assertFalse(mt.match(m3))

if __name__ == "__main__":
    unittest.main()
