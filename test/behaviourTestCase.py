# -*- coding: utf-8 -*-
import unittest

import spade
from spade.AID import aid
import xmpp

host = "127.0.0.1"


class BehaviourTestCase(unittest.TestCase):

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

        self.assertFalse(mt.match(message))

    def testXMPPMessageMatchFalse(self):
        xmpptemplate = xmpp.Message()
        xmpptemplate.setFrom(xmpp.JID("sender1@host"))
        xmpptemplate.setTo(xmpp.JID("recv1@host"))

        message = xmpp.Message()
        message.setFrom(xmpp.JID("sender1@host"))
        message.setTo(xmpp.JID("recv2@host"))

        mt = spade.Behaviour.MessageTemplate(xmpptemplate)

        self.assertFalse(mt.match(message))

if __name__ == "__main__":
    unittest.main()
