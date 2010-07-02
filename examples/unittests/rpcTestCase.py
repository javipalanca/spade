import os
import sys
import time
import unittest

sys.path.append('../..')

import spade

host = "127.0.0.1"

class MyAgent(spade.Agent.Agent):

	def _setup(self):
		self.result  = None

def sumVec(param):
    r = 0
    for i in param:
       r+=int(i)
    return r

def CreateService(name, owner, params=None):
    return spade.DF.Service(name, owner, P=params)

def Invoke(agent, service):

    agent.result = agent.invokeService(service)

def RegisterService(agent, service, method):

    agent.result = agent.registerService(service,method)

def DeRegisterService(agent):
    service = spade.DF.DfAgentDescription()
    service.setAID(agent.getAID())
    #service = CreateService("VecSum",agent.getAID())
    agent.result = agent.deregisterService(service)
    
def SearchService(agent,service):
    agent.result = agent.searchService(service)
    return agent.result

class RPCTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.Aaid = spade.AID.aid("a@"+host,["xmpp://aa@"+host])
        self.Baid = spade.AID.aid("b@"+host,["xmpp://bb@"+host])

    	self.a = MyAgent("a@"+host, "secret")
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret")
    	#self.b.setDebugToScreen()
    	#self.a.setDebugToScreen()
    	self.b.start()
    	self.a.wui.start()
    	self.b.wui.start()
    	
    def tearDown(self):
        DeRegisterService(self.b)
        self.a.stop()
        self.b.stop()
        
    def testInvokeService(self):
        DeRegisterService(self.b)
        
        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        Invoke(self.a, s)
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)
        
        DeRegisterService(self.b)
        self.assertEqual(self.b.result,True)
        services = SearchService(self.a,s)
        self.assertEqual(len(services),0)
    
    def testInvokeOwnService(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        Invoke(self.b, s)
        self.assertNotEqual(self.b.result,None)
        self.assertNotEqual(self.b.result,False)
        self.assertEqual(len(self.b.result),1)
        self.assertEqual(self.b.result[0],30)
        
        DeRegisterService(self.b)
        self.assertEqual(self.b.result,True)
        
    def testSearchAndInvoke(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        s2 = CreateService("VecSum",self.b.getAID(),[10,20])
        services = SearchService(self.a,s2)
        self.assertNotEqual(services,None)
        self.assertEqual(len(services),1)
        
        Invoke(self.a, services[0])
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)
        
        DeRegisterService(self.b)
        self.assertEqual(self.b.result,True)
        
    def testInvokeBadParams(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        s2 = CreateService("VecSum",self.b.getAID(),["param1","param2"])
        Invoke(self.a, s2)
        self.assertEqual(self.a.result,False)
        
        DeRegisterService(self.b)
        
    def testInvokeNotExistingService(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum",self.b.getAID(),[10,20])

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result,None)
        self.assertEqual(self.a.result,False)
         
    def testInvokeTwice(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)


        DeRegisterService(self.b)
        self.assertEqual(self.b.result,True)
        services = SearchService(self.a,s)
        self.assertEqual(len(services),0)
        

if __name__ == "__main__":
    unittest.main()
    sys.exit()
    suite = unittest.TestSuite()
    suite.addTest(RPCTestCase('testSearchAndInvoke'))
    result = unittest.TestResult()
    
    suite.run(result)
    for f in  result.failures: 
        print f[0]
        print f[1]
