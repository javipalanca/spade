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
            #self.myAgent.setSocialItem('sandra@'+self.myAgent.server)
            #self.myAgent._socialnetwork['sandra@'+self.myAgent.server].subscribe()
            #frm = self.myAgent.getAID().getName()
            #to = self.myAgent.getSpadePlatformJID()
            #pubsub = PubSub(self.myAgent, self)

            try:
                asserteq(self.myAgent.subscribeToEvent('NENode'), ('error', ['item-not-found']))

                asserteq(self.myAgent.unsubscribeFromEvent('NENode'), ('error', ['item-not-found']))
                asserteq(self.myAgent.deleteEvent('NENode'), ('error', ['item-not-found']))

                res = self.myAgent.publishEvent('NENode', Node(tag='foo'))
                asserteq(res[0], 'ok')
                asserteq(len(res[1]), 2)
                asserteq(res[1][0], 'NENode')
                asserteq(type(res[1][1]), unicode)

                asserteq(self.myAgent.createEvent('ExistsNode'), ('ok', ['ExistsNode']))

                self.myAgent.setSocialItem('juliet@'+self.myAgent.server)
                self.myAgent._socialnetwork['juliet@'+self.myAgent.server].subscribe()

                time.sleep(15)
                print 'Sleeping 15 seconds...'

                self.myAgent.publishEvent('ExistsNode', Node(tag='foo')) #OK

                asserteq(self.myAgent.unsubscribeFromEvent('ExistsNode', jid='juliet@'+self.myAgent.server), ('error', ['bad-request', 'invalid-jid']))

                time.sleep(5)
                print 'Sleeping 5 seconds...'

                asserteq(self.myAgent.deleteEvent('ExistsNode'), ('ok', []))

            except Exception,e:
                print 'Exception'
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
    a = MyAgent("romeo@"+host, "secret")
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

