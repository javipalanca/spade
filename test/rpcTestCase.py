# -*- coding: utf-8 -*-
import os
import sys
import time
import types
import unittest

import spade
from spade.kb import *
host = "127.0.0.1"


class MyAgent(spade.Agent.Agent):

    def _setup(self):
        self.result = None


def sumVec(vec):
    r = 0
    for i in vec:
        r += int(i)
    return {"sum": r}


def CreateService(name, owner, inputs=[], outputs=[]):
    return spade.DF.Service(name, owner, inputs=inputs, outputs=outputs)


def Invoke(agent, service, inputs=None):

    agent.result = agent.invokeService(service, inputs)


def RegisterService(agent, service, method):

    agent.result = agent.registerService(service, method)


def DeRegisterService(agent):
    service = spade.DF.DfAgentDescription()
    service.setAID(agent.getAID())
    #service = CreateService("VecSum",agent.getAID())
    agent.result = agent.deregisterService(service)


def SearchService(agent, service):
    agent.result = agent.searchService(service)
    return agent.result


class RPCTestCase(unittest.TestCase):

    def setUp(self):

        self.Aaid = spade.AID.aid("a@" + host, ["xmpp://a@" + host])
        self.Baid = spade.AID.aid("b@" + host, ["xmpp://b@" + host])

        self.a = MyAgent("a@" + host, "secret")
        self.a.start()
        self.b = MyAgent("b@" + host, "secret")
        #self.b.setDebugToScreen()
        #self.a.setDebugToScreen()
        self.b.start()
        #self.a.wui.start()
        #self.b.wui.start()

    def tearDown(self):
        DeRegisterService(self.b)
        self.a.stop()
        self.b.stop()

    def testInvokeService(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        Invoke(self.a, s, inputs={"vec": [10, 20]})
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(type(self.a.result), types.DictType)
        self.assertEqual(self.a.result, {"sum": 30})

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

    def testInvokeService_withPostCondition(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        s.addQ("Var(sum,x,Int)")
        RegisterService(self.b, s, sumVec)

        Invoke(self.a, s, inputs={"vec": [10, 20]})
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(type(self.a.result), types.DictType)
        self.assertEqual(self.a.result, {"sum": 30})

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

    def testInvokeOwnService(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        Invoke(self.b, s, inputs={"vec": [10, 20]})
        self.assertNotEqual(self.b.result, None)
        self.assertNotEqual(self.b.result, False)
        self.assertEqual(type(self.b.result), types.DictType)
        self.assertEqual(self.b.result, {"sum": 30})

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)

    def testSearchAndInvoke(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        s2 = CreateService("VecSum", self.b.getAID(), inputs=["vec"])
        services = SearchService(self.a, s2)
        self.assertNotEqual(services, None)
        self.assertEqual(len(services), 1)

        Invoke(self.a, services[0], inputs={"vec": [10, 20]})
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(type(self.a.result), types.DictType)
        self.assertEqual(self.a.result, {"sum": 30})

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)

    def testInvokeBadParams(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        s2 = CreateService("VecSum", self.b.getAID())
        Invoke(self.a, s2, inputs={"vec": ["param1", "param2"]})
        #self.assertEqual(self.a.result,False)
        if self.a.result is not False:
            self.fail(str(self.a.result))

        DeRegisterService(self.b)

    def testInvokeNotExistingService(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"])

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(self.a.result, False)

    def testInvokeTwice(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        Invoke(self.a, s, inputs={"vec": [10, 20]})
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(self.a.result, {"sum": 30})

        Invoke(self.a, s, inputs={"vec": [20, 20]})
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(self.a.result, {"sum": 40})

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

    def testInvokeService_withKB(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        self.a.kb.set("vec", [10, 20])

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(self.a.kb.get("sum"), 30)

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

        #del self.a.KB["sum"]
        #del self.a.KB["vec"]
        self.a.kb.configure(typ="Spade")

    def testInvokeServiceMissingParams_withKB(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        RegisterService(self.b, s, sumVec)

        Invoke(self.a, s)
        self.assertEqual(self.a.result, False)
        if self.a.kb.get("sum") is not None:
            self.fail()

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

    def testInvokeService_withKB_withPreCondition(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        s.addP("Var(vec,x,List)")
        RegisterService(self.b, s, sumVec)

        self.a.kb.set("vec", [10, 20])

        Invoke(self.a, s)

        self.assertNotEqual(self.a.result, None)
        self.assertNotEqual(self.a.result, False)
        self.assertEqual(self.a.kb.get("sum"), 30)

        DeRegisterService(self.b)

        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)

        self.assertEqual(len(services), 0)

        #del self.a.KB["sum"]
        #del self.a.KB["vec"]
        self.a.kb.configure(typ="Spade")

    def testInvokeService_withKB_withFailedPreCondition(self):
        DeRegisterService(self.b)

        s = CreateService("VecSum", self.b.getAID(), inputs=["vec"], outputs=["sum"])
        s.addP("Var(MyVec,x,List)")
        RegisterService(self.b, s, sumVec)

        self.a.kb.set("vec", [10, 20])

        Invoke(self.a, s)
        self.assertNotEqual(self.a.result, None)
        self.assertEqual(self.a.result, False)

        DeRegisterService(self.b)
        self.assertEqual(self.b.result, True)
        services = SearchService(self.a, s)
        self.assertEqual(len(services), 0)

        #del self.a.KB["sum"]
        #del self.a.KB["vec"]
        self.a.kb.configure(typ="Spade")


if __name__ == "__main__":
    unittest.main()
    sys.exit()
    '''suite = unittest.TestSuite()
    suite.addTest(RPCTestCase('testInvokeService_withKB_withPreCondition'))
    result = unittest.TestResult()

    suite.run(result)
    print str(result)
    for f in  result.errors:
        print f[0]
        print f[1]

    for f in  result.failures:
        print f[0]
        print f[1]'''
