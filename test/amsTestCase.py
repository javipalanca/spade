# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.search = None


class SearchBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self, s):
        self.s = s
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def _process(self):

        aad = spade.AMS.AmsAgentDescription()
        aad.setAID(spade.AID.aid(self.s + "@" + host, ["xmpp://" + self.s + "@" + host]))
        self.myAgent.search = self.myAgent.searchAgent(aad)


class ModifyBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self, s):
        self.s = s
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def _process(self):

        aad = spade.AMS.AmsAgentDescription()
        #aad.setAID(spade.AID.aid(self.s+"@"+host,["xmpp://"+self.s+"@"+host]))
        aad.ownership = "UNITTEST"
        self.myAgent.result = self.myAgent.modifyAgent(aad)

        aad = spade.AMS.AmsAgentDescription()
        aad.setAID(spade.AID.aid(self.s + "@" + host, ["xmpp://" + self.s + "@" + host]))
        self.myAgent.search = self.myAgent.searchAgent(aad)


class NotModifyBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self, s):
        self.s = s
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def _process(self):

        aad = spade.AMS.AmsAgentDescription()
        aad.setAID(spade.AID.aid(self.s + "@" + host, ["xmpp://" + self.s + "@" + host]))
        aad.ownership = "NOT_ALLOWED"
        self.myAgent.result = self.myAgent.modifyAgent(aad)

        aad = spade.AMS.AmsAgentDescription()
        aad.setAID(spade.AID.aid(self.s + "@" + host, ["xmpp://" + self.s + "@" + host]))
        self.myAgent.search = self.myAgent.searchAgent(aad)


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.a = MyAgent("a@" + host, "secret")
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        self.b.start()

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testSearchMe(self):
        self.a.addBehaviour(SearchBehav("a"), None)
        counter = 0
        while self.a.search is None and counter < 20:
            time.sleep(1)
            counter += 1

        if len(self.a.search) > 1:
            self.fail("Too many agents found")
        if len(self.a.search) == 0:
            self.fail("No agents found")

        self.assertEqual(self.a.search[0].getAID().getName(), "a@" + host)

    def testSearchOther(self):
        self.a.addBehaviour(SearchBehav("b"), None)
        counter = 0
        while self.a.search is None and counter < 20:
            time.sleep(1)
            counter += 1

        if len(self.a.search) > 1:
            self.fail("Too many agents found")
        if len(self.a.search) == 0:
            self.fail("No agents found")

        self.assertEqual(self.a.search[0].getAID().getName(), "b@" + host)

    def testSearchNotPresent(self):
        self.b.stop()
        for agent in ["notpresent", "b"]:
            self.a.addBehaviour(SearchBehav(agent), None)
            counter = 0
            while self.a.search is None and counter < 20:
                time.sleep(1)
                counter += 1

            self.assertEqual(len(self.a.search), 0)

    def testModifyAllowed(self):
        self.a.addBehaviour(ModifyBehav("a"), None)
        counter = 0
        while self.a.search is None and counter < 20:
            time.sleep(1)
            counter += 1

        self.assertEqual(self.a.result, True)
        self.assertEqual(len(self.a.search), 1)
        #self.assertEqual(self.a.search[0]["fipa:ownership"], "UNITTEST")
        self.assertEqual(self.a.search[0].getOwnership(), "UNITTEST")

    def testModifyNotAllowed(self):

        self.a.addBehaviour(NotModifyBehav("b"), None)
        counter = 0
        while self.a.search is None and counter < 20:
            time.sleep(1)
            counter += 1

        self.assertEqual(self.a.result, False)
        self.assertEqual(len(self.a.search), 1)
        self.assertNotEqual(self.a.search[0].getOwnership(), "NOT_ALLOWED")


if __name__ == "__main__":
    unittest.main()
