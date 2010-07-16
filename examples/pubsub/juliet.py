#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: Recognize error of "non-supported error creation"

import sys
sys.path.append("../..")
from xmpp.simplexml import Node
from spade.Agent import Agent
from spade.Behaviour import OneShotBehaviour
#from spade.pubsub import PubSub #, PubSubMessageTemplate

def asserteq(one, two):
    print one == two, '   ', one, ' == ', two
    assert one == two, 'not equal'

class MyAgent(Agent):
    class MyBehav(OneShotBehaviour):
        def onStart(self):
            self.myAgent.DEBUG("Starting behaviour . . .")

        def _process(self):
            #pubsub = PubSub(self.myAgent, self)

            try:

                while self.myAgent.subscribeToEvent('ExistsNode') == ('error', ['item-not-found']):
                    time.sleep(1)

                asserteq( self.myAgent.subscribeToEvent('ExistsNode'), ('error', ['not-authorized', 'presence-subscription-required']))
                asserteq( self.myAgent.unsubscribeFromEvent('ExistsNode'), ('error', ['unexpected-request', 'not-subscribeToEventd']))
                asserteq( self.myAgent.deleteEvent('ExistsNode'), ('error', ['forbidden']))
                asserteq( self.myAgent.createEvent('ExistsNode'), ('error', ['conflict']))
                asserteq( self.myAgent.publishEvent('ExistsNode', Node(tag='foo')), ('error', ['forbidden']))

                self.myAgent.setSocialItem('romeo@'+self.myAgent.server)
                self.myAgent._socialnetwork['romeo@'+self.myAgent.server].subscribe()

                time.sleep(10)
                print 'Sleeping 10 seconds...'

                asserteq( self.myAgent.subscribeToEvent('ExistsNode'), ('ok', []))
                #TODO: Check that the last published item is sent after subscription.

                #TODO: Check that the new item published by Romeo is received too.

                time.sleep(5)
                print 'Sleeping 5 seconds...'

                asserteq( self.myAgent.unsubscribeFromEvent('ExistsNode'), ('ok', []))
                asserteq( self.myAgent.subscribeToEvent('ExistsNode'), ('ok', [])) # OK
                #TODO: Check that the last published item is sent after subscription.
                asserteq( self.myAgent.subscribeToEvent('ExistsNode', jid='romeo@'+self.myAgent.server), ('error', ['bad-request', 'invalid-jid']))

                #TODO: Check that the notification of node deletion is received.

            except Exception,e:
                print e

        def onEnd(self):
            self.myAgent.DEBUG("Ending behaviour . . .")

    def _setup(self):
        self.DEBUG("MyAgent starting . . .")
        b = self.MyBehav()
        #FIXME: If we don't set it to default,
        # we will have problems with some replies.
        #self.addBehaviour(b, PubSubMessageTemplate())
        self.setDefaultBehaviour(b)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        host = "127.0.0.1"
    else:
        host = sys.argv[1]
    a = MyAgent("juliet@"+host, "secret")
    a.wui.start()
    a.setDebugToScreen()
    a.start()
    import time
    while True:
         try:
            time.sleep(1)
         except KeyboardInterrupt:
             break
    a.stop()
    sys.exit(0)

