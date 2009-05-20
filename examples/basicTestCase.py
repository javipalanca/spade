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
		self.pi = None

class GetPIBehav(spade.Behaviour.OneShotBehaviour):

	def _process(self):
		self.myAgent.pi = self.myAgent.getPlatformInfo()
		
class SendMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@"+host,["xmpp://b@"+host]))
        msg.setContent("UNITTEST")
        
        self.myAgent.send(msg)

class RecvMsgBehav(spade.Behaviour.OneShotBehaviour):

    def _process(self):
        self.myAgent.msg = None
        self.myAgent.msg = self._receive(block=True,timeout=10)


class BasicTestCase(unittest.TestCase):
    
    def setUp(self):

    	self.a = MyAgent("a@"+host, "secret")
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret")
    	self.b.start()
    	
    	self.rdf = """<rdf:ap-description><rdf:ap-services><rdf:ap-service><rdf:type>fipa.agent-management.ams</rdf:type><rdf:addresses>acc.127.0.0.1</rdf:addresses><rdf:name>xmpp://ams.127.0.0.1</rdf:name></rdf:ap-service></rdf:ap-services><rdf:name>xmpp://acc.127.0.0.1</rdf:name></rdf:ap-description>"""
    	
    	#self.pi = spade.content.RDFXML2CO(self.rdf)

    def tearDown(self):
        self.a.stop()
        self.b.stop()
        
    def testGetPlatformInfo(self):
        self.a.addBehaviour(GetPIBehav(), None)
        while self.a.pi == None: time.sleep(2)
        #print self.a.pi
        self.assertEqual( str(self.a.pi),  self.rdf) # 'Incorrect Platform Info'
        
    def testSendMsg(self):
        template = spade.Behaviour.ACLTemplate()
        template.setSender(spade.AID.aid("a@"+host,["xmpp://a@"+host]))
        t = spade.Behaviour.MessageTemplate(template)
        self.b.addBehaviour(RecvMsgBehav(),t)
        self.a.addBehaviour(SendMsgBehav(),None)
        counter = 0
        while self.b.msg == None and counter < 10:
            time.sleep(1)
            counter += 1
        self.assertNotEqual(self.b.msg,None)

if __name__ == "__main__":
    unittest.main()



