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

        self.jida = "a@" + host
        self.jidb = "b@" + host

        self.a = spade.Agent.Agent(self.jida, "secret")
        self.a.start()
        self.a.setDebugToScreen()

        self.b = spade.Agent.Agent(self.jidb, "secret")
        self.b.start()

        self.a.roster.unsubscribe(self.jidb)
        self.b.roster.unsubscribe(self.jida)

    def tearDown(self):
        self.a.roster.unsubscribe(self.jidb)
        self.b.roster.unsubscribe(self.jida)
        self.a.stop()
        self.b.stop()

    def testGetRoster(self):
        assert 'ams.'+host in self.a.roster.getContacts()
        assert 'a@'+host in self.a.roster.getContacts()

        #for i in self.a.roster.getContacts():
        item = self.a.roster.getContact(self.jida)
        assert 'ask' in item
        assert item['ask'] == None
        assert 'resources' in item
        assert item['resources'] == {}
        assert 'name' in item
        assert item['name'] in [None, 'b']
        assert 'groups' in item
        #assert item['groups'] == []
        assert item['groups'] == None
        assert 'subscription' in item
        #assert item['subscription'] == 'none'
        assert item['subscription'] == None

    def testSubscribe(self):
        self.a.roster.subscribe(self.jidb)
        self.a.roster.requestRoster(True)

        # Wait until updated roster arrives
        counter = 5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='both' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)

        # check that subscription has been done in both ways
        b = self.a.roster.getContact(self.jidb)
        assert b['subscription'] == 'both'

        a = self.b.roster.getContact(self.jida)
        assert a['subscription'] == 'both'

    def testUnsubscribeFromOrigin(self):
        self.a.roster.subscribe(self.jidb)
        self.a.roster.requestRoster(True)

        # Wait until updated roster arrives
        import time
        counter = 5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='both' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)

        # Now unsubscribe from a
        self.a.roster.unsubscribe(self.jidb)
        self.a.roster.requestRoster(True)

        # Wait until updated roster arrives
        import time
        counter = 5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='from' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)
        assert b['subscription'] == 'from'

    def testUnsubscribeFromDestination(self):
        self.a.roster.subscribe(self.jidb)
        self.a.roster.requestRoster(True)

        # Wait until updated roster arrives
        counter = 5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='both' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)

        # Now unsubscribe from b
        self.b.roster.unsubscribe(self.jida)
        self.b.roster.requestRoster(True)

        # Wait until updated roster arrives
        counter = 5
        b = self.b.roster.getContact(self.jida)
        while b['subscription']!='from' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.b.roster.getContact(self.jida)
        assert b['subscription'] == 'from'

    def testUnsubscribeFromBoth(self):
        self.a.roster.subscribe(self.jidb)
        self.a.roster.requestRoster(True)

        # Wait until updated roster arrives
        counter = 5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='both' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)

        # Now unsubscribe from a and b
        self.a.roster.unsubscribe(self.jidb)
        self.b.roster.unsubscribe(self.jida)
        self.a.roster.requestRoster(True)
        self.b.roster.requestRoster(True)

        # Wait until updated roster arrives
        counter = 5
        a = self.b.roster.getContact(self.jida)
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='none' and a['subscription']!='none' and counter>0:
            time.sleep(1)
            counter-=1
            a = self.b.roster.getContact(self.jida)
            b = self.a.roster.getContact(self.jidb)
        assert b['subscription'] == 'none'
        assert a['subscription'] == 'none'

    def testAvailable(self):
        self.a.roster.subscribe(self.jidb)
        self.b.roster.sendPresence(typ='available', priority=1, show="MyShowMsg", status="Do Not Disturb")

        #wait for subscription
        counter=5
        b = self.a.roster.getContact(self.jidb)
        while b['subscription']!='both' and counter>0:
            time.sleep(1)
            counter-=1
            b = self.a.roster.getContact(self.jidb)

        item = self.a.roster.getContact(self.jidb)
        assert item != None

        assert self.a.roster.getPriority(self.jidb) == 1
        assert self.a.roster.getShow(self.jidb) == "MyShowMsg"
        assert self.a.roster.getStatus(self.jidb) == "Do Not Disturb"

if __name__ == "__main__":
    unittest.main()
    sys.exit()
