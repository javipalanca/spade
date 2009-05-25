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
            self.result = None
            
class RegisterBehav(spade.Behaviour.OneShotBehaviour):

        def __init__(self, s):
            self.s = s
            spade.Behaviour.OneShotBehaviour.__init__(self)
    
        def _process(self):
            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_1")
            sd.setType("unittest_type_1")

            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)
            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_2")
            sd.setType("unittest_type_2")
            dad.addService(sd)
            dad.setAID(self.myAgent.getAID())
            self.myAgent.result = self.myAgent.registerService(dad)
            
class DeRegisterBehav(spade.Behaviour.OneShotBehaviour):

        def __init__(self, s):
            self.s = s
            spade.Behaviour.OneShotBehaviour.__init__(self)

        def _process(self):

            dad = spade.DF.DfAgentDescription()
            dad.setAID(self.myAgent.getAID())
            self.myAgent.result = self.myAgent.deregisterService(dad)
            
class SearchBehav(spade.Behaviour.OneShotBehaviour):
    
        def __init__(self, s):
            self.s = s
            spade.Behaviour.OneShotBehaviour.__init__(self)

        def _process(self):
            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_1")
            sd.setType("unittest_type_1")

            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            dad.setAID(self.myAgent.getAID())
            self.myAgent.result = self.myAgent.searchService(dad)

            
class ModifyBehav(spade.Behaviour.OneShotBehaviour):

        def __init__(self, s):
            self.s = s
            spade.Behaviour.OneShotBehaviour.__init__(self)

        def _process(self):

            aad = spade.AMS.AmsAgentDescription()
            aad.setAID(spade.AID.aid(self.s+"@"+host,["xmpp://"+self.s+"@"+host]))
            aad.ownership = "UNITTEST" 
            self.myAgent.result = self.myAgent.modifyAgent(aad)

            aad = spade.AMS.AmsAgentDescription()
            aad.setAID(spade.AID.aid(self.s+"@"+host,["xmpp://"+self.s+"@"+host]))
            self.myAgent.search = self.myAgent.searchAgent(aad)[0]
            
            



class BasicTestCase(unittest.TestCase):
    
    def setUp(self):

    	self.a = MyAgent("a@"+host, "secret")
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret")
    	self.b.start()
    	
    def tearDown(self):
        self.a.stop()
        self.b.stop()
        
    def wait(self,item):
        counter = 0
        while item == None and counter < 20:
            time.sleep(1)
            counter += 1
        
    def testRegisterService(self):
        self.a.addBehaviour(RegisterBehav("a"),None)
        counter = 0
        self.wait(self.a.result)
            
        self.assertEqual(self.a.result, True)
        
        self.a.addBehaviour(SearchBehav("a"),None)
        counter = 0
        self.wait(self.a.result)
        
        self.assertNotEqual(self.a.result, None)    
        self.assertEqual(len(self.a.result), 1)

        
    def testSearchNotPresent(self):
        self.b.stop()
        for agent in ["notpresent","b"]:
            self.a.addBehaviour(SearchBehav(agent), None)
            counter = 0
            while self.a.search == None and counter < 20:
                time.sleep(1)
                counter +=1

            self.assertEqual(len(self.a.search), 0)
            
    def testModifyAllowed(self):

        self.a.addBehaviour(ModifyBehav("a"), None)
        counter = 0
        while self.a.search == None and counter < 20:
            time.sleep(1)
            counter +=1

        self.assertEqual(self.a.result, True)
        self.assertEqual(self.a.search[0]["ownership"], "UNITTEST")

    def testModifyNotAllowed(self):

        self.a.addBehaviour(ModifyBehav("b"), None)
        counter = 0
        while self.a.search == None and counter < 20:
            time.sleep(1)
            counter +=1

        self.assertEqual(self.a.result, False)
        self.assertNotEqual(self.a.search[0]["ownership"], "UNITTEST")


if __name__ == "__main__":
    unittest.main()



