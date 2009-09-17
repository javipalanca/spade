import os
import sys
import time
import unittest

sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

host = "127.0.0.1"

class MyAgent(spade.Agent.Agent):

	def _setup(self):
		self.pi  = None
		self.msg  = None


		
class p2pSendMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        msg.setContent("testSendMsg")
        
        self.myAgent.send(msg,method="p2ppy")

class p2pRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        self.myAgent.msg = self._receive(block=True,timeout=10)

class p2pSendAndRecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        msg.setContent("testSendAndRecvMsg")

        self.myAgent.send(msg, method="p2ppy")
        self.myAgent.msg = None
        self.myAgent.msg = self._receive(block=True,timeout=10)

class p2pAnswerMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = None
        msg = self._receive(block=True,timeout=10)
        if msg != None:
			content = msg.getContent()
			msg = msg.createReply()
			msg.setContent(content)
			self.myAgent.send(msg, method="p2ppy")



class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.Aaid = spade.AID.aid("a@"+host,["xmpp://a@"+host])
        self.Baid = spade.AID.aid("b@"+host,["xmpp://b@"+host])

    	self.a = MyAgent("a@"+host, "secret",p2p=True)
    	self.a._debug = True
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret",p2p=True)
    	self.b._debug=True
    	self.b.start()
    	
    	#self.rdf = """<rdf:ap-description><rdf:ap-services><rdf:ap-service><rdf:type>fipa.agent-management.ams</rdf:type><rdf:addresses>acc.127.0.0.1</rdf:addresses><rdf:name>xmpp://ams.127.0.0.1</rdf:name></rdf:ap-service></rdf:ap-services><rdf:name>xmpp://acc.127.0.0.1</rdf:name></rdf:ap-description>"""
    	self.rdf = """<rdf:RDF xmlns:fipa="http://www.fipa.org/schemas/fipa-rdf0#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:ap-description><rdf:ap-services list="true"><rdf:ap-services><rdf:ap-service><rdf:type>fipa.agent-management.ams</rdf:type><rdf:addresses list="true"><rdf:addresses>acc.127.0.0.1</rdf:addresses></rdf:addresses><rdf:name>xmpp://ams.127.0.0.1</rdf:name></rdf:ap-service></rdf:ap-services></rdf:ap-services><rdf:name>xmpp://acc.127.0.0.1</rdf:name></rdf:ap-description></rdf:RDF>"""
    	#self.pi = spade.content.RDFXML2CO(self.rdf)

    def tearDown(self):
        self.a.stop()
        self.b.stop()
        
    def testSendMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pRecvMsgBehav(),t)
        self.a.addBehaviour(p2pSendMsgBehav(),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg,None)
        self.assertEqual(self.b.msg.getContent(),"testSendMsg")
        self.assertEqual(self.b.msg.getSender(), self.Aaid)
        self.assertEqual(len(self.b.msg.getReceivers()),1)
        self.assertEqual(self.b.msg.getReceivers()[0], self.Baid)

    def testSendAndRecvMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(self.Aaid)
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(p2pAnswerMsgBehav(),t)
        template.setSender(self.Baid)
        t = spade.Behaviour.MessageTemplate(template)
        self.a.addBehaviour(p2pSendAndRecvMsgBehav(),t)
        counter = 0
        while self.a.msg == None and counter < 20:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.a.msg,None)
        self.assertEqual(self.a.msg.getContent(),"testSendAndRecvMsg")


if __name__ == "__main__":
    unittest.main()



