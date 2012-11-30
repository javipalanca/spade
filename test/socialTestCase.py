# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"


class PresenceBehavior(spade.Behaviour.EventBehaviour):
    def _process(self):
        msg = self._receive(False)
        if msg.getSender().getName() == "b@" + host:
            if msg.getProtocol() == "available":
                self.myAgent.recvAvailable = msg
            elif msg.getProtocol() == "unavailable":
                self.myAgent.recvUnavailable = msg

class AcceptSubscriptionBehavior(spade.Behaviour.EventBehaviour):
    def _process(self):
        msg = self._receive(False)
        if str(msg.getSender().getName()) != "ams."+host:
            self.myAgent.roster.acceptSubscription(str(msg.getSender().getName()))

class AcceptAndAnswerSubscriptionBehavior(spade.Behaviour.EventBehaviour):
    def _process(self):
        msg = self._receive(False)
        if "a@" + host in  str(msg.getSender().getName()):
            self.myAgent.roster.acceptSubscription(str(msg.getSender().getName()))
            self.myAgent.roster.subscribe(str(msg.getSender().getName()))

class DeclineSubscriptionBehavior(spade.Behaviour.EventBehaviour):
    def _process(self):
        msg = self._receive(False)
        if "a@" + host in  str(msg.getSender().getName()):
            self.myAgent.roster.declineSubscription(str(msg.getSender().getName()))

class ReceiveDeclinationBehavior(spade.Behaviour.EventBehaviour):
    def _process(self):
        msg = self._receive(False)
        if "b@" + host in  str(msg.getSender().getName()):
            self.myAgent.receivedDeclination = True


class socialTestCase(unittest.TestCase):

    def setUp(self):

        self.jida = "a@" + host
        self.jidb = "b@" + host

        self.a = spade.Agent.Agent(self.jida, "secret")
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Presence")
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(PresenceBehavior(), t)
        self.a.start()
        #self.a.setDebugToScreen()

        self.b = spade.Agent.Agent(self.jidb, "secret")
        self.b.start()
        #self.b.setDebugToScreen()

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

    def testSubscribeAlways(self):
        self.a.roster.acceptAllSubscriptions()
        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1
        
        # check that subscription has been done in both ways
        assert self.a.roster.checkSubscription(self.jidb) == 'both'
        assert self.b.roster.checkSubscription(self.jida) == 'both'

    def testSubscribeFrom(self):
        #self.b.setDebugToScreen()
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Presence")
        template.setProtocol("subscribe")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(AcceptSubscriptionBehavior(), t)
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'to' and counter>0:
            time.sleep(1)
            counter-=1
        
        # check that subscription has been done in both ways
        assert self.a.roster.checkSubscription(self.jidb) == 'to'
        assert self.b.roster.checkSubscription(self.jida) == 'from'

    def testSubscribeFromAndTo(self):
        #self.a.setDebugToScreen()
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Presence")
        template.setProtocol("subscribe")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(AcceptAndAnswerSubscriptionBehavior(), t)
        self.a.addBehaviour(AcceptSubscriptionBehavior(), t)
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
            time.sleep(1)
            counter-=1
        
        # check that subscription has been done in both ways
        assert self.a.roster.checkSubscription(self.jidb) == 'both'
        assert self.b.roster.checkSubscription(self.jida) == 'both'

    def testDeclineSubscription(self):
        #self.a.setDebugToScreen()
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Presence")
        template.setProtocol("subscribe")
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(DeclineSubscriptionBehavior(), t)
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Presence")
        template.setProtocol("unsubscribed")
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(ReceiveDeclinationBehavior(), t)
        self.a.receivedDeclination = False
        self.a.roster.subscribe(self.jidb)

        # Wait until updated roster arrives
        counter = 5
        while self.a.receivedDeclination is False and counter>0:
            time.sleep(1)
            counter-=1
        
        # check that subscription has been done in both ways
        assert self.a.receivedDeclination is True
        assert self.a.roster.checkSubscription(self.jidb) == 'none'
        assert self.b.roster.checkSubscription(self.jida) == 'none'

    def testUnsubscribeFromOrigin(self):
        self.a.roster.acceptAllSubscriptions()
        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
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
        self.a.roster.acceptAllSubscriptions()
        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
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
        self.a.roster.acceptAllSubscriptions()
        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
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
        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
        self.a.roster.subscribe(self.jidb)
        self.b.roster.sendPresence(typ='available', priority=1, show="MyShowMsg", status="Do Not Disturb")

        #wait for subscription
        counter=5
        while self.a.roster.checkSubscription(self.jidb) != 'both' and counter>0:
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

        self.b.roster.acceptAllSubscriptions()
        self.b.roster.followbackAllSubscriptions()
        self.a.roster.acceptAllSubscriptions()
        self.a.roster.followbackAllSubscriptions()

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

    suite = unittest.TestSuite()
    suite.addTest(socialTestCase('testDeclineSubscription'))
    result = unittest.TestResult()

    suite.run(result)
    print str(result)
    for f in  result.errors:
        print f[0]
        print f[1]

    for f in  result.failures:
        print f[0]
        print f[1]
