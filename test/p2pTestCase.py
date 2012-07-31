import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"

class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.msg  = None


        
class p2pSendMsgBehav(spade.Behaviour.OneShotBehaviour):
    
    def __init__(self,method):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        msg.setContent("testSendMsg")
        
        self.myAgent.send(msg,method=self.method)

class p2pRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self,method):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method

    def _process(self):
        self.myAgent.msg = self._receive(block=True,timeout=10)

class p2pSendAndRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self,method):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        msg.setContent("testSendAndRecvMsg")

        self.myAgent.send(msg, method=self.method)
        self.myAgent.msg = None
        self.myAgent.msg = self._receive(block=True,timeout=10)

class p2pAnswerMsgBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self,method):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method

    def _process(self):
        msg = None
        msg = self._receive(block=True,timeout=10)
        if msg != None:
            content = msg.getContent()
            msg = msg.createReply()
            msg.setContent(content)
            self.myAgent.send(msg, method=self.method)

class p2pSendMultiMsgBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self,method, nmsg=1):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method
        self.nmsg = int(nmsg)

    def _process(self):
        self.myAgent.routeTag = []
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        
        socket = None

        for i in range (self.nmsg):
            msg.setContent(str(i+1))
            self.myAgent.send(msg,method=self.method)
            if i==0:
                socket = self.myAgent.p2p_routes["b@"+host]["socket"]
            else:
                if socket != self.myAgent.p2p_routes["b@"+host]["socket"]:
                    self.myAgent.routeTag.append(str(i+1))

class p2pRecvMultiMsgBehav(spade.Behaviour.OneShotBehaviour):

    def __init__(self,method, nmsg=1):
        spade.Behaviour.OneShotBehaviour.__init__(self)
        self.method = method
        self.nmsg = int(nmsg)

    def _process(self):
        self.myAgent.receivedmsg = 0
        self.myAgent.errorTag = []
        
        for i in range(self.nmsg):
            self.myAgent.msg = None
            self.myAgent.msg = self._receive(block=True,timeout=20)
            if self.myAgent.msg.getContent()!=str(i+1):
                self.myAgent.errorTag.append(i+1)
            if self.myAgent.msg: self.myAgent.receivedmsg+=1

class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.Aaid = spade.AID.aid("a@"+host,["xmpp://a@"+host])
        self.Baid = spade.AID.aid("b@"+host,["xmpp://b@"+host])

        self.a = MyAgent("a@"+host, "secret",p2p=True)
        #self.a._debug = True
        self.a.start()
        self.b = MyAgent("b@"+host, "secret",p2p=True)
        #self.b._debug=True
        self.b.start()

    def tearDown(self):
        self.a.stop()
        self.b.stop()
        
    def testSendMsgP2P(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pRecvMsgBehav("p2p"),t)
        self.a.addBehaviour(p2pSendMsgBehav("p2p"),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg,None)
        self.assertEqual(self.b.msg.getContent(),"testSendMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()),1)
        self.assertEqual(self.b.msg.getReceivers()[0], self.Baid)
        self.assertEqual(self.b.msg._attrs["method"],"p2p")

    def testSendMsgP2PPY(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pRecvMsgBehav("p2ppy"),t)
        self.a.addBehaviour(p2pSendMsgBehav("p2ppy"),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg,None)
        self.assertEqual(self.b.msg.getContent(),"testSendMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()),1)
        self.assertEqual(self.b.msg.getReceivers()[0], self.Baid)
        self.assertEqual(self.b.msg._attrs["method"],"p2ppy")

    def testSendAndRecvMsgP2P(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pAnswerMsgBehav("p2p"),t)
        template.setSender(self.Baid)
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(p2pSendAndRecvMsgBehav("p2p"),t)
        counter = 0
        while self.a.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.msg,None)
        self.assertEqual(self.a.msg.getContent(),"testSendAndRecvMsg")
        self.assertEqual(self.a.msg._attrs["method"],"p2p")

    def testSendAndRecvMsgP2PPY(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pAnswerMsgBehav("p2ppy"),t)
        template.setSender(self.Baid)
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(p2pSendAndRecvMsgBehav("p2ppy"),t)
        counter = 0
        while self.a.msg == None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.msg,None)
        self.assertEqual(self.a.msg.getContent(),"testSendAndRecvMsg")
        self.assertEqual(self.a.msg._attrs["method"],"p2ppy")
        
    def testSendMultiMsgP2P(self):
        nmsg=100
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pRecvMultiMsgBehav("p2p",nmsg),t)
        self.a.addBehaviour(p2pSendMultiMsgBehav("p2p",nmsg),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1

        self.assertEqual(self.b.receivedmsg,nmsg)
        self.assertNotEqual(self.b.msg,None)
        self.assertEqual(self.b.msg._attrs["method"],"p2p")
        self.assertEqual(self.b.errorTag,[])
        self.assertEqual(self.a.routeTag,[])

    def testSendMultiMsgP2PPY(self):
        nmsg=100
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pRecvMultiMsgBehav("p2ppy",nmsg),t)
        self.a.addBehaviour(p2pSendMultiMsgBehav("p2ppy",nmsg),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg,None)

        self.assertEqual(self.b.msg._attrs["method"],"p2ppy")
        self.assertEqual(self.b.receivedmsg,nmsg)
        self.assertEqual(self.b.errorTag,[])
        self.assertEqual(self.a.routeTag,[])


if __name__ == "__main__":
    unittest.main()



