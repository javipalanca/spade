# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade

host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.result = None
        #self.setDebugToScreen()

#with DAD


def Register_DAD(agent, param):

    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_1_" + param)
    sd.setType("unittest_type_1_" + param)

    dad = spade.DF.DfAgentDescription()
    dad.addService(sd)
    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_2_" + param)
    sd.setType("unittest_type_2" + param)
    dad.addService(sd)
    dad.setAID(agent.getAID())
    agent.result = agent.registerService(dad)


def DeRegister_DAD(agent, param):

    dad = spade.DF.DfAgentDescription()
    dad.setAID(agent.getAID())
    agent.result = agent.deregisterService(dad)


def Search_DAD(agent, param):

    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_1_" + param)
    #sd.setType("unittest_type_1")

    dad = spade.DF.DfAgentDescription()
    dad.addService(sd)

    #dad.setAID(agent.getAID())
    agent.result = agent.searchService(dad)


def Search_2_DAD(agent, param):

    dad = spade.DF.DfAgentDescription()

    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_1_" + param)
    #sd.setType("unittest_type_1")
    dad.addService(sd)

    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_2_" + param)
    #sd.setType("unittest_type_1")
    dad.addService(sd)

    dad.setAID(agent.getAID())
    agent.result = agent.searchService(dad)


def EmptySearch_DAD(agent):
    dad = spade.DF.DfAgentDescription()
    agent.result = agent.searchService(dad)


def Modify_DAD(agent, param):

    sd = spade.DF.ServiceDescription()
    sd.setName("unittest_name_1_" + param)
    sd.setType("unittest_type_1_modified_" + param)

    dad = spade.DF.DfAgentDescription()
    dad.addService(sd)

    dad.setAID(agent.getAID())
    agent.result = agent.modifyService(dad)


#with Service()
def Register(agent, param):

    s = spade.DF.Service()
    s.setName("unittest_name_1_" + param)
    s.setOwner(agent.getAID())
    s.addP("service_precondition")
    s.addQ("service_postcondition")
    s.setInputs(['login', 'password'])
    s.setOutputs(['account_id'])
    s.setDescription("Login Service")
    s.setOntology("account_managing")
    agent.result = agent.registerService(s)


def DeRegister(agent, param):

    s = spade.DF.Service()
    s.setOwner(agent.getAID())
    agent.result = agent.deregisterService(s)


def Search(agent, param):

    s = spade.DF.Service()
    s.setName("unittest_name_1_" + param)
    #s.setOwner(spade.AID.aid(param+"@"+host,["xmpp://"+param+"@"+host]))
    #s.setInputs(['login','password'])

    agent.result = agent.searchService(s)


def EmptySearch(agent):
    s = spade.DF.Service()
    agent.result = agent.searchService(s)


def Modify(agent, param):

    s = spade.DF.Service()
    s.setName("unittest_name_1_" + param)
    s.setOwner(agent.getAID())
    s.setOntology("new_ontology")

    agent.result = agent.modifyService(s)


class DFTestCase(unittest.TestCase):

    def setUp(self):

        self.a = MyAgent("a@" + host, "secret")
        #self.a._debug=True
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        #self.b._debug=True
        self.b.start()

    def tearDown(self):
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.a, "b")
        DeRegister_DAD(self.b, "a")
        DeRegister_DAD(self.b, "b")
        DeRegister(self.a, "a")
        DeRegister(self.a, "b")
        DeRegister(self.b, "a")
        DeRegister(self.b, "b")
        self.a.stop()
        self.b.stop()

    #with DAD
    def testRegisterService_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #register service
        Register_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search_2_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())
        self.assertEqual(len(self.a.result[0].getServices()), 2)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1_a', 'unittest_name_2_a']:
            self.fail()
        if self.a.result[0].getServices()[1].getName() not in ['unittest_name_1_a', 'unittest_name_2_a']:
            self.fail()

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search_DAD(self.a, "a")

        self.assertEqual(self.a.result, [])

    def testSameRegister_DAD(self):
        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.b, "a")

        #register service
        Register_DAD(self.a, "a")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        #register service
        Register_DAD(self.b, "a")
        self.assertEqual(self.b.result, True)
        self.b.result = None

        Search_DAD(self.a, "a")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 2)
        self.assertEqual(len(self.a.result[0].getServices()), 1)
        self.a.result = None

        Search_DAD(self.a, "b")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)
        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.b, "a")

    def testDoubleRegister_DAD(self):
        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.a, "b")

        #register service
        Register_DAD(self.a, "a")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        #register service
        Register_DAD(self.a, "b")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        Search_DAD(self.a, "a")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)
        self.a.result = None

        Search_DAD(self.a, "b")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)
        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.a, "b")

    def testSearchNotPresent_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.a, "b")

        #check service is not registered
        Search_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #register service
        Register_DAD(self.a, "b")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is not registered
        Search_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "b")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search_DAD(self.a, "b")
        self.assertEqual(self.a.result, [])

    def testModifyService_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #register service
        Register_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #modify service
        Modify_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is modified
        Search_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())

        self.assertEqual(len(self.a.result[0].getServices()), 1)

        self.assertEqual(self.a.result[0].getServices()[0].getType(), "unittest_type_1_modified_a")

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

    def testModifyNotAllowed_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #register service
        Register_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #modify service
        Modify_DAD(self.b, "a")

        self.assertEqual(self.b.result, False)

        self.b.result = None

        #check service is NOT modified
        Search_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getAID(), self.a.getAID())

        self.assertEqual(len(self.a.result[0].getServices()), 1)

        if self.a.result[0].getServices()[0].getName() not in ['unittest_name_1_a']:  # ,'unittest_name_2_a']:
            self.fail()

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

    def testModifyNotRegistered_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #check service is registered
        Search_DAD(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #modify service
        Modify_DAD(self.a, "a")

        self.assertEqual(self.a.result, False)

        self.a.result = None

        #check service is deregistered
        self.a.result = False
        Search_DAD(self.a, "a")
        self.assertEqual(self.a.result, [])
        self.assertEqual(len(self.a.result), 0)

    def testFullSearch_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #get zero services
        EmptySearch_DAD(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #register service
        Register_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check number of DADs is 1
        EmptySearch_DAD(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)
        #check number of services is 2
        self.assertEqual(len(self.a.result[0].getServices()), 2)

        self.a.result = None

        #register another service
        Register_DAD(self.b, "b")

        self.assertEqual(self.b.result, True)

        self.b.result = None

        #check number of services is 2
        EmptySearch_DAD(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 2)
        #check number of services is 4
        self.assertEqual(len(self.a.result[0].getServices()), 2)
        self.assertEqual(len(self.a.result[1].getServices()), 2)

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")
        DeRegister_DAD(self.b, "b")

    def testAlreadyRegistered_DAD(self):

        #deregister service
        DeRegister_DAD(self.a, "a")

        #register service
        Register_DAD(self.a, "a")

        #self.assertEqual(self.a.result, True)

        self.a.result = None

        #register service ALREADY registered
        Register_DAD(self.a, "a")

        self.assertEqual(self.a.result, False)

        self.a.result = None

        #deregister service
        DeRegister_DAD(self.a, "a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search_DAD(self.a, "a")
        self.assertEqual(self.a.result, [])

    #with Service()
    def testRegisterService(self):

        #deregister service
        DeRegister(self.a, "a")

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOwner(), self.a.getAID())

        if self.a.result[0].getName() not in ['unittest_name_1_a']:
            self.fail()

        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a, "a")

        self.assertEqual(self.a.result, [])

    def testSameRegister(self):
        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.b, "a")

        #register service
        Register(self.a, "a")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        #register service
        Register(self.b, "a")
        self.assertEqual(self.b.result, True)
        self.b.result = None

        Search(self.a, "a")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 2)
        self.a.result = None

        Search(self.a, "b")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)
        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.b, "a")

    def testDoubleRegister(self):
        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.a, "b")

        #register service
        Register(self.a, "a")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        #register service
        Register(self.a, "b")
        self.assertEqual(self.a.result, True)
        self.a.result = None

        Search(self.a, "a")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)
        self.a.result = None

        Search(self.a, "b")
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)
        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.a, "b")

    def testSearchNotPresent(self):

        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.b, "a")

        self.a.result = None

        #register service
        Register(self.a, "b")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is not registered
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #deregister service
        DeRegister(self.a, "b")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a, "b")
        self.assertEqual(self.a.result, [])

    def testModifyService(self):

        #deregister service
        DeRegister(self.a, "a")

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOwner(), self.a.getAID())
        self.assertEqual(len(self.a.result), 1)

        if self.a.result[0].getName() not in ['unittest_name_1_a']:
            self.fail()

        self.assertEqual(self.a.result[0].getOntology(), ["account_managing"])

        self.a.result = None

        #modify service
        Modify(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is modified
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOwner(), self.a.getAID())

        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOntology(), ["new_ontology"])

        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")

        self.assertEqual(self.a.result, True)

        #check service is deregistered
        self.a.result = False
        Search(self.a, "a")
        self.assertEqual(self.a.result, [])

    def testModifyNotAllowed(self):

        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.b, "a")

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check service is registered
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOwner(), self.a.getAID())

        if self.a.result[0].getName() not in ['unittest_name_1_a']:
            self.fail()

        self.assertEqual(self.a.result[0].getOntology(), ["account_managing"])

        self.a.result = None
        self.b.result = None

        #modify service
        Modify(self.b, "a")

        self.assertEqual(self.b.result, False)

        self.b.result = None

        #check service is NOT modified
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.assertEqual(self.a.result[0].getOwner(), self.a.getAID())

        if self.a.result[0].getName() not in ['unittest_name_1_a']:
            self.fail()

        self.assertEqual(self.a.result[0].getOntology(), ["account_managing"])

        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")

        self.assertEqual(self.a.result, True)

    def testModifyNotRegistered(self):
        #deregister service
        DeRegister(self.a, "a")

        #check service is not registered
        Search(self.a, "a")

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #modify service
        Modify(self.a, "a")

        self.assertEqual(self.a.result, False)

        self.a.result = None

        #check service is deregistered
        self.a.result = False
        Search(self.a, "a")
        self.assertEqual(self.a.result, [])
        self.assertEqual(len(self.a.result), 0)

    def testEmptySearch(self):
        #deregister service
        DeRegister(self.a, "a")
        DeRegister(self.a, "b")

        #get zero services
        EmptySearch(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 0)

        self.a.result = None

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check number of services is 1
        EmptySearch(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 1)

        self.a.result = None

        #register service
        Register(self.a, "b")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #check number of services is 2
        EmptySearch(self.a)

        self.assertNotEqual(self.a.result, None)
        self.assertEqual(len(self.a.result), 2)

        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")
        self.assertEqual(self.a.result, True)

        self.a.result = None

    def testAlreadyRegistered(self):

        #deregister service
        DeRegister(self.a, "a")

        #register service
        Register(self.a, "a")

        self.assertEqual(self.a.result, True)

        self.a.result = None

        #register service ALREADY registered
        Register(self.a, "a")

        self.assertEqual(self.a.result, False)

        self.a.result = None

        #deregister service
        DeRegister(self.a, "a")

        self.assertEqual(self.a.result, True)


if __name__ == "__main__":
    unittest.main()
    sys.exit()

    suite = unittest.TestSuite()
    suite.addTest(DFTestCase('testRegisterService'))
    result = unittest.TestResult()

    suite.run(result)
    for f in result.failures:
        print f[0]
        print f[1]
