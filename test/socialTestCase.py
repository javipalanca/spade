# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"


class SubscribeBehaviour(spade.Behaviour.EventBehaviour):

    def _process(self):
        msg = self._receive(True)
        self.myAgent.eventmsg = msg


class socialTestCase(unittest.TestCase):

    def setUp(self):

        self.Aaid = spade.AID.aid("a@" + host, ["xmpp://a@" + host])
        self.Baid = spade.AID.aid("b@" + host, ["xmpp://b@" + host])

        self.a = spade.Agent.Agent("a@" + host, "secret")
        self.a.start()
        #self.a.setDebugToScreen()

        self.b = spade.Agent.Agent("b@" + host, "secret")
        self.b.start()

        self.a.setSocialItem('b@' + host)
        #self.a._socialnetwork['b@'+host].unsubscribe()
        del self.a._socialnetwork['b@' + host]
        self.b.setSocialItem('a@' + host)
        #self.b._socialnetwork['a@'+host].unsubscribe()
        del self.b._socialnetwork['a@' + host]

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testNoSocialItem(self):
        jid = 'b@' + host

        self.assertFalse(jid in self.a._socialnetwork)
        self.assertFalse(jid in self.a._roster)

    def testSetSocialItem(self):
        jid = 'b@' + host
        self.a.setSocialItem(jid)

        self.assertTrue(jid in self.a._socialnetwork)

        assert self.a._socialnetwork[jid].getPresence() == ""

        assert self.a._socialnetwork[jid]._subscription == "none"

        self.assertFalse(jid in self.a._roster)

if __name__ == "__main__":
    unittest.main()
    sys.exit()
