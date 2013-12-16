# -*- coding: utf-8 -*-
import sys
import time
import unittest

import spade
from spade.bdi import *
from spade.Agent import BDIAgent

host = "127.0.0.1"


def s1_method(Value):
        return {"Myoutput1": 1}


def s2_method(Myoutput1):
        return {"Myoutput2": 2}


def s3_method(Value3):
        return {"Myoutput3": 4}


def s4_method(Myoutput3):
        return {"Myoutput4": 5}


class PlanTestCase(unittest.TestCase):

    def setUp(self):

        self.a = BDIAgent("bdi@" + host, "secret")
        self.a.start()
        #self.a.setDebugToScreen()

    def tearDown(self):
        self.a.stop()
        del self.a

    def testAddBelieve(self):
        self.a.addBelieve(expr("Value(TestValue)"))

        self.assertTrue(self.a.askBelieve("Value(TestValue)"))

    def testAddGoal(self):
        g = Goal("Value(2)")
        self.a.addGoal(g)

        self.assertEqual(len(self.a.bdiBehav.goals), 1)
        self.assertEqual(self.a.bdiBehav.goals[0].expression, "Value(2)")


class BDITestCase(unittest.TestCase):

    def setUp(self):

        self.a = BDIAgent("bdi@" + host, "secret")
        #self.a.setDebugToScreen()
        self.a.start()

        self.s1 = spade.DF.Service(name="s1", owner=self.a.getAID(), inputs=["Value"], outputs=["Myoutput1"], P=["Var(Value,0,Int)"], Q=["Var(Myoutput1,1,Int)"])
        self.s2 = spade.DF.Service(name="s2", owner=self.a.getAID(), inputs=["Myoutput1"], outputs=["Myoutput2"], P=["Var(Myoutput1,1,Int)"], Q=["Var(Myoutput2,2,Int)"])
        self.s3 = spade.DF.Service(name="s3", owner=self.a.getAID(), inputs=["Value3"], outputs=["Myoutput3"], P=["Var(Value3,3,Int)"], Q=["Var(Myoutput3,4,Int)"])
        self.s4 = spade.DF.Service(name="s4", owner=self.a.getAID(), inputs=["Myoutput3"], outputs=["Myoutput4"], P=["Var(Myoutput3,4,Int)"], Q=["Var(Myoutput4,5,Int)"])

        time.sleep(1)

    def tearDown(self):
        s = spade.DF.Service()
        s.setOwner(self.a.getAID())
        self.a.deregisterService(s)
        self.a.stop()
        del self.a

    def testAddPlan(self):

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)

        self.a.bdiBehav.discover()
        result = self.a.addPlan(inputs=["Value"], outputs=["Myoutput2"], P=["Var(Value,0,Int)"], Q=["Var(Myoutput2,2,Int)"], services=["s1", "s2"])

        self.assertTrue(result)

    def goalCompletedCB(self, goal):
        self.goalCompleted = True

    def testSimpleGoalCompleted(self):

        self.goalCompleted = False
        self.a.registerService(self.s1, s1_method)

        self.a.saveFact("Value", 0)

        self.a.setGoalCompletedCB(self.goalCompletedCB)

        self.a.addGoal(Goal("Var(Myoutput1,1,Int)"))

        counter = 0
        while not self.goalCompleted and counter < 10:
            time.sleep(1)
            counter += 1

        self.assertTrue(self.goalCompleted)
        self.assertTrue(self.a.askBelieve("Var(Myoutput1,1,Int)"))
        assert self.a.getFact("Myoutput1") == 1

    def testGoalCompleted_withPlan(self):

        self.goalCompleted = False
        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)

        self.a.saveFact("Value", 0)

        self.a.setGoalCompletedCB(self.goalCompletedCB)

        self.a.addGoal(Goal("Var(Myoutput2,2,Int)"))

        counter = 0
        while not self.goalCompleted and counter < 10:
            time.sleep(1)
            counter += 1

        self.assertTrue(self.goalCompleted)
        self.assertTrue(self.a.askBelieve("Var(Myoutput2,2,Int)"))
        assert self.a.getFact("Myoutput2") == 2

    def serviceCompletedCB(self, service):
        s = service.getName()
        if s == "s1":
                self.s1Completed = True
        if s == "s2":
                self.s2Completed = True
        if s == "s3":
                self.s3Completed = True
        if s == "s4":
                self.s4Completed = True

    def testMultiGoalCompleted(self):
        self.s1Completed = False
        self.s3Completed = False

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s3, s3_method)

        self.a.saveFact("Value", 0)
        self.a.saveFact("Value3", 3)

        self.a.setServiceCompletedCB(self.serviceCompletedCB)

        self.a.addGoal(Goal("Var(Myoutput3,4,Int)"))
        self.a.addGoal(Goal("Var(Myoutput1,1,Int)"))

        counter = 0
        while counter < 10 and (self.s1Completed is False or self.s3Completed is False):
            time.sleep(1)
            counter += 1

        self.assertTrue(self.s1Completed)
        self.assertTrue(self.s3Completed)
        self.assertTrue(self.a.askBelieve("Var(Myoutput1,1,Int)"))
        assert self.a.getFact("Myoutput1") == 1
        self.assertTrue(self.a.askBelieve("Var(Myoutput3,4,Int)"))
        assert self.a.getFact("Myoutput3") == 4

    def testMultiGoalCompleted_withMultiServices(self):
        self.s2Completed = False
        self.s4Completed = False

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)
        self.a.registerService(self.s3, s3_method)
        self.a.registerService(self.s4, s4_method)

        self.a.saveFact("Value", 0)
        self.a.saveFact("Value3", 3)

        self.a.setServiceCompletedCB(self.serviceCompletedCB)

        self.a.addGoal(Goal("Var(Myoutput2,2,Int)"))
        self.a.addGoal(Goal("Var(Myoutput4,5,Int)"))

        counter = 0
        while counter < 10 and (self.s2Completed is False or self.s4Completed is False):
            time.sleep(1)
            counter += 1

        self.assertTrue(self.s2Completed)
        self.assertTrue(self.s4Completed)
        self.assertTrue(self.a.askBelieve("Var(Myoutput2,2,Int)"))
        assert self.a.getFact("Myoutput2") == 2
        self.assertTrue(self.a.askBelieve("Var(Myoutput4,5,Int)"))
        assert self.a.getFact("Myoutput4") == 5

class BDIPrologTestCase:
    def set_up(self):

        self.s1 = spade.DF.Service(name="s1", owner=self.a.getAID(), inputs=["Value"], outputs=["Myoutput1"], P=["var('Value',0,int)"], Q=["var('Myoutput1',1,int)"])
        self.s2 = spade.DF.Service(name="s2", owner=self.a.getAID(), inputs=["Myoutput1"], outputs=["Myoutput2"], P=["var('Myoutput1',1,int)"], Q=["var('Myoutput2',2,int)"])
        self.s3 = spade.DF.Service(name="s3", owner=self.a.getAID(), inputs=["Value3"], outputs=["Myoutput3"], P=["var('Value3',3,int)"], Q=["var('Myoutput3',4,int)"])
        self.s4 = spade.DF.Service(name="s4", owner=self.a.getAID(), inputs=["Myoutput3"], outputs=["Myoutput4"], P=["var('Myoutput3',4,int)"], Q=["var('Myoutput4',5,int)"])

        time.sleep(2)

    def tearDown(self):
        s = spade.DF.Service()
        s.setOwner(self.a.getAID())
        self.a.deregisterService(s)
        self.a.stop()
        del self.a

    def testAddPlan(self):

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)

        self.a.bdiBehav.discover()
        result = self.a.addPlan(inputs=["Value"], outputs=["Myoutput2"], P=["var('Value',0,int)"], Q=["var('Myoutput2',2,int)"], services=["s1", "s2"])

        self.assertTrue(result)

    def goalCompletedCB(self, goal):
        self.goalCompleted = True

    def testSimpleGoalCompleted(self):

        self.goalCompleted = False
        self.a.registerService(self.s1, s1_method)

        self.a.saveFact("Value", 0)

        self.a.setGoalCompletedCB(self.goalCompletedCB)

        self.a.addGoal(Goal("var('Myoutput1',1,int)"))

        counter = 0
        while not self.goalCompleted and counter < 30:
            time.sleep(1)
            counter += 1

        self.assertTrue(self.goalCompleted)
        self.assertTrue(self.a.askBelieve("var('Myoutput1',1,int)"))
        assert self.a.getFact("Myoutput1") == 1

    def testGoalCompleted_withPlan(self):

        self.goalCompleted = False
        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)

        self.a.saveFact("Value", 0)

        self.a.setGoalCompletedCB(self.goalCompletedCB)

        self.a.addGoal(Goal("var('Myoutput2',2,int)"))

        counter = 0
        while not self.goalCompleted and counter < 30:
            time.sleep(1)
            counter += 1

        self.assertTrue(self.goalCompleted)
        self.assertTrue(self.a.askBelieve("var('Myoutput2',2,int)"))
        assert self.a.getFact("Myoutput2") == 2

    def serviceCompletedCB(self, service):
        s = service.getName()
        if s == "s1":
                self.s1Completed = True
        if s == "s2":
                self.s2Completed = True
        if s == "s3":
                self.s3Completed = True
        if s == "s4":
                self.s4Completed = True

    def testMultiGoalCompleted(self):
        self.s1Completed = False
        self.s3Completed = False

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s3, s3_method)

        self.a.saveFact("Value", 0)
        self.a.saveFact("Value3", 3)

        self.a.setServiceCompletedCB(self.serviceCompletedCB)

        self.a.addGoal(Goal("var('Myoutput3',4,int)"))
        self.a.addGoal(Goal("var('Myoutput1',1,int)"))

        counter = 0
        while counter < 60 and (self.s1Completed is False or self.s3Completed is False):
            time.sleep(1)
            counter += 1

        self.assertTrue(self.s1Completed)
        self.assertTrue(self.s3Completed)
        self.assertTrue(self.a.askBelieve("var('Myoutput1',1,int)"))
        assert self.a.getFact("Myoutput1") == 1
        self.assertTrue(self.a.askBelieve("var('Myoutput3',4,int)"))
        assert self.a.getFact("Myoutput3") == 4

    def testMultiGoalCompleted_withMultiServices(self):
        self.s2Completed = False
        self.s4Completed = False

        self.a.registerService(self.s1, s1_method)
        self.a.registerService(self.s2, s2_method)
        self.a.registerService(self.s3, s3_method)
        self.a.registerService(self.s4, s4_method)

        self.a.saveFact("Value", 0)
        self.a.saveFact("Value3", 3)

        self.a.setServiceCompletedCB(self.serviceCompletedCB)

        self.a.addGoal(Goal("var('Myoutput2',2,int)"))
        self.a.addGoal(Goal("var('Myoutput4',5,int)"))

        counter = 0
        while counter < 30 and (self.s2Completed is False or self.s4Completed is False):
            time.sleep(1)
            counter += 1

        self.assertTrue(self.s2Completed)
        self.assertTrue(self.s4Completed)
        self.assertTrue(self.a.askBelieve("var('Myoutput2',2,int)"))
        assert self.a.getFact("Myoutput2") == 2
        self.assertTrue(self.a.askBelieve("var('Myoutput4',5,int)"))
        assert self.a.getFact("Myoutput4") == 5

class BDISWITestCase(BDIPrologTestCase, unittest.TestCase):
    def setUp(self):
	self.a = BDIAgent("bdi_swi@" + host, "secret")
	self.a.kb.configure("SWI")
        #self.a.setDebugToScreen()
        self.a.start()
	self.set_up()

class BDIXSBTestCase(BDIPrologTestCase, unittest.TestCase):
    def setUp(self):
	self.a = BDIAgent("bdi_xsb@" + host, "secret")
	self.a.kb.configure("XSB")
        #self.a.setDebugToScreen()
        self.a.start()
	self.set_up()


class BDIECLiPSeTestCase(BDIPrologTestCase, unittest.TestCase):
    def setUp(self):
	self.a = BDIAgent("bdi_eclipse@" + host, "secret")
	self.a.kb.configure("ECLiPSe")
        #self.a.setDebugToScreen()
        self.a.start()
	self.set_up()

class BDIFlora2TestCase(BDIPrologTestCase, unittest.TestCase):
    def setUp(self):
	self.a = BDIAgent("bdi_flora2@" + host, "secret")
	self.a.kb.configure("Flora2")
        #self.a.setDebugToScreen()
        self.a.start()
	self.set_up()

if __name__ == "__main__":
    unittest.main()
    sys.exit()
    '''suite = unittest.TestSuite()
    suite.addTest(BDITestCase('testAddPlan'))
    result = unittest.TestResult()

    suite.run(result)
    print str(result)
    for f in  result.errors:
        print f[0]
        print f[1]

    for f in  result.failures:
        print f[0]
        print f[1]'''
