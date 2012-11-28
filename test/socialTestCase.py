# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"

class SocialAgent(spade.Agent.Agent):
    def availableHandler(self, msg):
        if msg.getFrom() == "b@" + host:
            self.recvAvailable = msg

    def unavailableHandler(self, msg):
        if msg.getFrom() == "b@" + host:
            self.recvUnavailable = msg

class SubscribeBehaviour(spade.Behaviour.EventBehaviour):

    def _process(self):
        msg = self._receive(True)
        self.myAgent.eventmsg = msg


class socialTestCase(unittest.TestCase):

    def setUp(self):

        self.jida = "a@" + host
        self.jidb = "b@" + host

        self.a = SocialAgent(self.jida, "secret")
        self.a.start()
        #self.a.setDebugToScreen()

        self.b = SocialAgent(self.jidb, "secret") #, "OTHER")
        self.b.start()
        #self.b.setDebugToScreen()
        #self.b2 = SocialAgent(self.jidb, "secret", "FIRST")
        #self.b2.start()        

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

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1

        # check that subscription has been done in both ways
        assert self.a.roster.checkSubscription(self.jidb) == 'both'
        assert self.b.roster.checkSubscription(self.jida) == 'both'

    def testUnsubscribeFromOrigin(self):
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1

        # Now unsubscribe from a
        self.a.roster.unsubscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'from' and counter>0:
            time.sleep(1)
            counter-=1

        assert self.a.roster.checkSubscription(self.jidb) == 'from'

    def testUnsubscribeFromDestination(self):
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1

        # Now unsubscribe from b
        self.b.roster.unsubscribe(self.jida)

        # Wait until updated roster arrives
        counter = 5
        while self.b.roster.checkSubscription(self.jida) != 'from' and counter>0:
            time.sleep(1)
            counter-=1
        assert self.b.roster.checkSubscription(self.jida) == 'from'

    def testUnsubscribeFromBoth(self):
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and self.b.roster.checkSubscription(self.jida) != 'both' and counter>0:
            time.sleep(1)
            counter-=1

        # Now unsubscribe from a and b
        self.a.roster.unsubscribe(self.jidb)
        self.b.roster.unsubscribe(self.jida)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) == 'both' and self.b.roster.checkSubscription(self.jida) == 'both' and counter>0:
            time.sleep(1)
            counter-=1
        assert self.a.roster.checkSubscription(self.jidb) == 'none'
        assert self.b.roster.checkSubscription(self.jida) == 'none'

    def testAvailable(self):
        self.a.recvAvailable = None
        self.a.roster.subscribe(self.jidb)
        self.b.roster.sendPresence(typ='available', priority=1, show="MyShowMsg", status="Do Not Disturb")

        #wait for subscription
        counter=5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            assert not self.a.roster.isAvailable(self.jidb)
            time.sleep(1)
            counter-=1

        counter = 5
        assert self.a.roster.isAvailable(self.jidb)
        while self.a.recvAvailable == None and counter>0:
            time.sleep(0.5)
            counter-=1

        item = self.a.roster.getContact(self.jidb)
        assert item != None
        assert self.a.roster.isAvailable(self.jidb)
        assert self.a.roster.getPriority(self.jidb) == '1'
        assert self.a.roster.getShow(self.jidb) == "MyShowMsg"
        assert self.a.roster.getStatus(self.jidb) == "Do Not Disturb"

    def testUnavailable(self):
        self.a.recvUnavailable = None

        self.a.roster.subscribe(self.jidb)
        self.b.roster.subscribe(self.jida)

        self.b.roster.sendPresence('available')

        #wait for subscription
        counter=5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1

        counter = 5
        while not self.a.roster.isAvailable(self.jidb) and counter>0:
            time.sleep(1)
            counter-=1
        assert self.a.roster.isAvailable(self.jidb)
        
        self.b.roster.sendPresence("unavailable")
        
        counter=5
        while self.a.roster.isAvailable(self.jidb) and counter>0:
            time.sleep(1)
            counter-=1
        assert not self.a.roster.isAvailable(self.jidb)

if __name__ == "__main__":
    unittest.main()
    sys.exit()
