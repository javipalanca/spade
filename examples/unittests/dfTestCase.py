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



def Register(agent, param):


            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_1")
            sd.setType("unittest_type_1")

            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)
            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_2")
            sd.setType("unittest_type_2")
            dad.addService(sd)
            dad.setAID(spade.AID.aid(param+"@"+host,["xmpp://"+param+"@"+host]))
            agent.result = agent.registerService(dad)

def DeRegister(agent, param):


            dad = spade.DF.DfAgentDescription()
            dad.setAID(spade.AID.aid(param+"@"+host,["xmpp://"+param+"@"+host]))
            agent.result = agent.deregisterService(dad)

def Search(agent, param):


            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_1")
            #sd.setType("unittest_type_1")

            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            dad.setAID(spade.AID.aid(param+"@"+host,["xmpp://"+param+"@"+host]))
            agent.result = agent.searchService(dad)

def EmptySearch(agent):
            dad = spade.DF.DfAgentDescription()
            agent.result = agent.searchService(dad)

def Modify(agent, param):

            sd = spade.DF.ServiceDescription()
            sd.setName("unittest_name_1")
            sd.setType("unittest_type_1_modified")

            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            dad.setAID(spade.AID.aid(param+"@"+host,["xmpp://"+param+"@"+host]))
            agent.result = agent.modifyService(dad)





class DFTestCase(unittest.TestCase):

    def setUp(self):

    	self.a = MyAgent("a@"+host, "secret")
    	#self.a._debug=True
    	self.a.start()
    	self.b = MyAgent("b@"+host, "secret")
    	#self.b._debug=True
    	self.b.start()

    def tearDown(self):
        self.a.stop()
        self.b.stop()

    def testRegisterService(self):

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())
        self.assertEqual(len(self.a.result[0].getServices()), 2)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()

        self.a.result = None

        #deregister service
        DeRegister(self.a,"a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a,"a")
        
        self.assertEqual(self.a.result, [])



    def testSearchNotPresent(self):
        #check service is not registered
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #register service
        Register(self.a,"b")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is not registered
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #deregister service
        DeRegister(self.a,"b")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a,"b")
        self.assertEqual(self.a.result, [])



    def testModifyService(self):
            #register service
            Register(self.a,"a")

            self.assertEqual(self.a.result, True)

            self.a.result = None

            #check service is registered
            Search(self.a,"a")

            self.assertNotEqual(self.a.result, None)
            self.assertEqual(len(self.a.result), 1)

            self.assertEqual(self.a.result[0].getAID(), self.a.getAID())
            self.assertEqual(len(self.a.result[0].getServices()), 2)

            if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1','unittest_name_2']:
                self.fail()
            if self.a.result[0].getServices()[1].getName() not in ['unittest_name_1','unittest_name_2']:
                self.fail()

            self.a.result = None

            #modify service
            Modify(self.a,"a")

            self.assertEqual(self.a.result, True)

            self.a.result = None

            #check service is modified
            Search(self.a,"a")

            self.assertNotEqual(self.a.result, None)
            self.assertEqual(len(self.a.result), 1)

            self.assertEqual(self.a.result[0].getAID(), self.a.getAID())

            self.assertEqual(len(self.a.result[0].getServices()), 1)

            self.assertEqual(self.a.result[0].getServices()[0].getType(),"unittest_type_1_modified")

            self.a.result = None

            #deregister service
            DeRegister(self.a,"a")

            self.assertEqual(self.a.result, True)

            #check service is deregistered
            self.a.result = False
            Search(self.a,"a")
            self.assertEqual(self.a.result, [])




    def testModifyNotAllowed(self):
        #register service
        Register(self.a,"a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())
        self.assertEqual(len(self.a.result[0].getServices()), 2)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()
        if self.a.result[0].getServices()[1].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()

        self.a.result = None
        self.b.result = None

        #modify service
        Modify(self.b,"a")

        self.assertEqual(self.b.result, False)

        self.b.result = None

        #check service is NOT modified
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())

        self.assertEqual(len(self.a.result[0].getServices()), 2)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()
        if self.a.result[0].getServices()[1].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()

        self.a.result = None

        #deregister service
        DeRegister(self.a,"a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a,"a")
        self.assertEqual(self.a.result, [])


    def testEmptySearch(self):
        #get zero services
        EmptySearch(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #register service
        Register(self.a,"a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check number of services is 1
        EmptySearch(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.a.result = None

        #deregister service
        DeRegister(self.a,"a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a,"a")
        self.assertEqual(self.a.result, [])


    def testAlreadyRegistered(self):
        #register service
        Register(self.a,"a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a,"a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())
        self.assertEqual(len(self.a.result[0].getServices()), 2)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1','unittest_name_2']:
            self.fail()

        self.a.result = None

        #register service ALREADY registered
        Register(self.a,"a")

        self.assertEqual(self.a.result, False)

        self.a.result = None


        #deregister service
        DeRegister(self.a,"a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a,"a")
        self.assertEqual(self.a.result, [])



if __name__ == "__main__":
    unittest.main()



