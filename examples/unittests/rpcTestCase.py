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

def CreateService(name, owner=None, params=None):
    return spade.DF.Service(name, owner, P=params)

def Invoke(agent, service):

    agent.result = agent.invokeService(service)

def RegisterService(agent, service, method):

    agent.result = agent.registerService(service,method)

def DeRegisterService(agent):
    service = spade.DF.DfAgentDescription()
    service.setAID(agent.getAID())
    agent.result = agent.deregisterService(service)
    
def SearchService(agent,service):
    agent.result = agent.searchService(service)
    return agent.result

class RPCTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.Aaid = spade.AID.aid("a@"+host,["xmpp://a@"+host])
        self.Baid = spade.AID.aid("b@"+host,["xmpp://b@"+host])

    	self.a = MyAgent("a@"+host, "secret")
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret")
    	#self.b.setDebugToScreen()
    	#self.a.setDebugToScreen()
    	self.b.start()
    	self.a.wui.start()
    	self.b.wui.start()
    	
    def tearDown2(self):
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
        DeRegisterService(self.a)
        s = CreateService("VecSum",self.a.getAID(),[10,20])
        RegisterService(self.a, s, sumVec)
        
        Invoke(self.a, s)
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)
        
        DeRegisterService(self.a)
        
    def testSearchAndInvoke(self):
        DeRegisterService(self.b)
        s = CreateService("VecSum",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        s2 = CreateService("VecSum")
        services = SearchService(self.a,s2)
        self.assertNotEqual(services,None)
        self.assertEqual(len(services),1)
        
        Invoke(self.a, services[0])
        self.assertNotEqual(self.a.result,None)
        self.assertNotEqual(self.a.result,False)
        self.assertEqual(len(self.a.result),1)
        self.assertEqual(self.a.result[0],30)
        
        DeRegisterService(self.b)
        
    def testInvokeBadParams(self):
        DeRegisterService(self.b)
        s = CreateService("service",self.b.getAID(),[10,20])
        RegisterService(self.b, s, sumVec)
        
        s2 = CreateService("service",self.b.getAID(),["param1","param2"])
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
    suite.addTest(RPCTestCase('testInvokeTwice'))
    result = unittest.TestResult()
    
    suite.run(result)
    for f in  result.failures: 
        print f[0]
        print f[1]
    print "Done."    
    alive = True
    import time
    while alive:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            alive=False
    sys.exit(0)

