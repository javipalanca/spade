# -*- coding: utf-8 -*-
import unittest

from spade.tbcbp import *
from spade.DF import Service
from spade.kb import KB
from spade.bdi import Goal


class tbcbpCasesTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasicCase(self):
        case = Case(P=["P1", "P2"], Q=["Q1"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])

        assert case.getP() == ["P1", "P2"]
        assert case.getQ() == ["Q1"]
        assert case.getInputs() == ["invar1", "invar2"]
        assert case.getOutputs() == ["outvar1"]
        assert case.services == ["s1", "s2", "s3"]
        assert case.getTime() == 0
        assert case.getQoS() == 1

    def testAddCase(self):
        case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case2 = Case(P=["P3", "P4"], Q=["Q3"], inputs=["outvar1"], outputs=["outvar1"], services=["s4", "s5", "s6"])

        case3 = case1 + case2

        assert case3.getP() == ["P1", "P2"]
        assert case3.getQ() == ["Q3"]
        assert case3.getInputs() == ["invar1", "invar2"]
        assert case3.getOutputs() == ["outvar1"]

        assert case3.services == ["s1", "s2", "s3", "s4", "s5", "s6"]

    def testIAddCase(self):
        case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case2 = Case(P=["P3", "P4"], Q=["Q3"], inputs=["outvar1"], outputs=["outvar1"], services=["s4", "s5", "s6"])

        case1 += case2

        assert case1.getP() == ["P1", "P2"]
        assert case1.getQ() == ["Q3"]
        assert case1.getInputs() == ["invar1", "invar2"]
        assert case1.getOutputs() == ["outvar1"]

        assert case1.services == ["s1", "s2", "s3", "s4", "s5", "s6"]

    def testEqualCase(self):
        case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case2 = Case(P=["P2", "P1"], Q=["Q2", "Q1"], inputs=["invar2", "invar1"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case3 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s2", "s1", "s3"])
        case4 = Case(P=["P2", "P1"], Q=["Q2", "Q1"], inputs=["invar3", "invar1"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case5 = Case(P=["P4", "P1"], Q=["Q2", "Q1"], inputs=["invar2", "invar1"], outputs=["outvar1"], services=["s1", "s2", "s3"])

        assert case1 == case2
        assert case1 != case3
        assert case1 != case4
        assert case1 != case5
        assert case1 != {"P": ["P1", "P2"], "Q": ["Q1", "Q2"], "inputs": ["invar1", "invar2"], "outputs": ["outvar1"], "services": ["s1", "s2", "s3"]}

    def testRewardCase(self):
        case = Case(P=[], Q=[], inputs=[], outputs=[], services=["s1", "s2", "s3"])

        case.reward()
        assert case.trust == 1
        case.reward()
        assert case.trust == 1
        case.punish()
        assert case.trust == float(1) / float(3)
        case.punish()
        assert case.trust == 0.0
        case.reward()
        assert case.trust == float(1) / float(5)
        for i in range(1000):
            case.reward()
        assert case.trust <= 1.0


class tbcbpPlansTestCase(unittest.TestCase):

    def setUp(self):
        self.case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        self.case2 = Case(P=["P3", "P4"], Q=["Q3"], inputs=["outvar1"], outputs=["outvar2"], services=["s4", "s5", "s6"])
        self.case3 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s2", "s1", "s3"])

    def testBasicPlan(self):

        plan = Plan(cases=[self.case1, self.case2])

        assert plan.getP() == ["P1", "P2"]
        assert plan.getQ() == ["Q3"]
        assert plan.getInputs() == ["invar1", "invar2"]
        assert plan.getOutputs() == ["outvar2"]

        assert plan.getCases() == [self.case1, self.case2]

    def testBadPlanConstructor(self):
        #can't create a plan with an empty list of cases
        self.assertRaises(Exception, Plan, [])

    def testGetCase(self):
        plan = Plan(cases=[self.case1, self.case2])
        assert plan.getCase() == self.case1 + self.case2

        plan = Plan(cases=[self.case1])
        del plan.cases[0]
        assert plan.getCase() is None

    def testGetServices(self):
        plan = Plan(cases=[self.case1, self.case2])
        assert plan.getServices() == ["s1", "s2", "s3", "s4", "s5", "s6"]

        assert plan.getServices() != ["s3", "s6", "s4", "s2", "s5", "s1"]

    def testInsertCase(self):

        plan = Plan(cases=[self.case2])

        assert plan.getP() == ["P3", "P4"]
        assert plan.getQ() == ["Q3"]
        assert plan.getInputs() == ["outvar1"]
        assert plan.getOutputs() == ["outvar2"]
        assert plan.getCases() == [self.case2]

        plan.insertCase(self.case1)

        assert plan.getP() == ["P1", "P2"]
        assert plan.getQ() == ["Q3"]
        assert plan.getInputs() == ["invar1", "invar2"]
        assert plan.getOutputs() == ["outvar2"]
        assert plan.getCases() == [self.case1, self.case2]

    def testInsertCaseException(self):

        plan = Plan(cases=[self.case1])

        self.assertRaises(Exception, plan.insertCase, self.case3)

    def testGetPlanTime(self):
        case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case2 = Case(P=["P3", "P4"], Q=["Q3"], inputs=["outvar1"], outputs=["outvar2"], services=["s4", "s5", "s6"])

        case1.time = 11
        case2.time = 4
        plan = Plan(cases=[case1, case2])

        assert plan.getTime() == 15

    def testGetNextService(self):

        plan = Plan([self.case1, self.case2])

        assert plan.getNextService() == "s1"
        assert plan.getNextService() == "s2"
        assert plan.getNextService() == "s3"
        assert plan.getNextService() == "s4"
        assert plan.getNextService() == "s5"
        assert plan.getNextService() == "s6"
        assert plan.getNextService() is None
        assert plan.getNextService() == "s1"
        assert plan.getNextService() == "s2"

    def testLenPlan(self):
        plan = Plan([self.case1, self.case2])

        assert len(plan) == 2


class tbcbpTBCBPTestCase(unittest.TestCase):

    def setUp(self):
        self.s1 = Service(name="s1", P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"])
        self.s1_1 = Service(name="s1_1", P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"])
        self.s2 = Service(name="s2", P=["p3", "p4"], Q=["q3", "q4"], inputs=["o1"], outputs=["o2"])

    def testRegisterService(self):
        tbcbp = TBCBP()
        tbcbp.registerService(self.s1)

        s = tbcbp.getService("s1")

        assert s == self.s1

    def testGetServiceInfo(self):

        tbcbp = TBCBP()
        tbcbp.registerService(self.s1, time=13)

        s = tbcbp.getServiceInfo("s1")

        assert s["s"] == self.s1
        assert s["P"] == ["p1", "p2"]
        assert s["Q"] == ["q1", "q2"]
        assert s["inputs"] == ["i1"]
        assert s["outputs"] == ["o1"]
        assert s["time"] == 13
        assert s["QoS"] == 1

        case = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"], services=["s1"])

        assert tbcbp.getCases(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"])[0] == case

    def testAddCase(self):
        tbcbp = TBCBP()
        tbcbp.registerService(self.s1)
        tbcbp.registerService(self.s2)
        tbcbp.registerService(self.s1_1)

        case1 = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o2"], services=["s1", "s2"])
        case2 = Case(P=["p3", "p4"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"], services=["s2", "s1"])
        case1_1 = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o2"], services=["s1_1", "s2"])

        #adding a case
        assert tbcbp.addCase(case1) is not False

        #adding a case with unregistered services
        self.assertFalse(tbcbp.addCase(Case(services=["s1", "s3"])))

        #check added cases
        assert tbcbp.getCase(case1) == case1
        assert tbcbp.getCase(case1) != case2
        assert tbcbp.getCase(Case(services=["s2"])) is None

        #adding similar cases
        assert tbcbp.addCase(case1_1) is not False
        assert tbcbp.getCase(case1_1) != case1
        assert tbcbp.getCase(case1_1) == case1_1

    def testGetCaseOfService(self):
        tbcbp = TBCBP()
        tbcbp.registerService(self.s1)
        tbcbp.registerService(self.s1_1)

        case1 = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"], services=["s1"])
        case1_1 = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"], services=["s1_1"])

        assert tbcbp.getCaseOfService("s1") == case1
        assert tbcbp.getCaseOfService("s1") != case1_1
        assert tbcbp.getCaseOfService("s1_1") == case1_1
        assert tbcbp.getCaseOfService("s1_1") != case1

    def testPlanMatchesInKB(self):
        tbcbp = TBCBP()
        case1 = Case(P=["P(P1)", "P(P2)"], Q=["Q(Q1)", "Q(Q2)"], inputs=["i1"], outputs=["o1"], services=["s1"])
        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        self.assertTrue(tbcbp.planMatchesInKB(case1, kb0))

        case2 = Case(P=["P(P3)", "P(P2)"], Q=["q1", "q2"], inputs=["i1"], outputs=["o1"], services=["s1"])
        self.assertFalse(tbcbp.planMatchesInKB(case2, kb0))

        case3 = Case(P=["P(P1)", "P(P2)"], Q=["q1", "q2"], inputs=["i2"], outputs=["o1"], services=["s1"])
        self.assertFalse(tbcbp.planMatchesInKB(case3, kb0))

    def testAddPlan(self):
        case1 = Case(P=["P1", "P2"], Q=["Q1", "Q2"], inputs=["invar1", "invar2"], outputs=["outvar1"], services=["s1", "s2", "s3"])
        case2 = Case(P=["P3", "P4"], Q=["Q3"], inputs=["outvar1"], outputs=["outvar2"], services=["s4", "s5", "s6"])
        plan = Plan(cases=[case1, case2])
        tbcbp = TBCBP()

        tbcbp.addPlan(plan)

        tbcbp.getCase(case1 + case2) == case1 + case2

    def testComposePlan1Case(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)"], inputs=["i1"], outputs=["o1"], name="s1")
        tbcbp.registerService(s1)

        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        g = Goal("Q(Q1)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0)

        assert plan is not None
        assert plan.getQ() == ["Q(Q1)"]
        assert plan.getP() == ["P(P1)", "P(P2)"]
        assert len(plan) == 1

    def testComposePlan2Cases(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)", "Q(Q2)"], inputs=["i1"], outputs=["o1"], name="s1")
        s2 = Service(P=["P(P3)", "P(P4)"], Q=["Q(Q3)"], inputs=["o1"], outputs=["o2"], name="s2")
        tbcbp.registerService(s1)
        tbcbp.registerService(s2)

        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        g = Goal("Q(Q3)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0)

        assert plan is not None
        assert plan.getQ() == ["Q(Q3)"]
        assert plan.getP() == ["P(P1)", "P(P2)"]
        assert len(plan) == 2

    def testComposePlan1CaseNoP(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)"], inputs=["i1"], outputs=["o1"], name="s1")
        tbcbp.registerService(s1)

        kb0 = KB()
        kb0.tell("P(P1)")
        #Missing kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        g = Goal("Q(Q1)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0)

        assert plan is None

    def testComposePlan1CaseNoInputs(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)"], inputs=["i1"], outputs=["o1"], name="s1")
        tbcbp.registerService(s1)

        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        #Missing kb0.set("i1", 1024)

        g = Goal("Q(Q1)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0)

        assert plan is None

    def testComposePlanNoCases(self):
        tbcbp = TBCBP()
        kb0 = KB()

        g = Goal("Q(Q1)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0)

        assert plan is None

    def testComposePlanBestTime(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)", "Q(Q2)"], inputs=["i1"], outputs=["o1"], name="s1")
        s2 = Service(P=["P(P3)", "P(P4)"], Q=["Q(Q3)"], inputs=["o1"], outputs=["o2"], name="s2")
        s3 = Service(P=["P(P3)", "P(P4)"], Q=["Q(Q3)"], inputs=["o1"], outputs=["o2"], name="s3")

        tbcbp.registerService(s1, time=10, QoS=1)
        tbcbp.registerService(s2, time=200, QoS=1)
        tbcbp.registerService(s3, time=20, QoS=1)

        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        g = Goal("Q(Q3)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0, use_rl=False)

        for s in plan.getServices():
            assert s in ["s1", "s3"]
            assert s != "s2"

    def testComposePlanBestQoS(self):
        tbcbp = TBCBP()
        s1 = Service(P=["P(P1)", "P(P2)"], Q=["Q(Q1)", "Q(Q2)"], inputs=["i1"], outputs=["o1"], name="s1")
        s2 = Service(P=["P(P3)", "P(P4)"], Q=["Q(Q3)"], inputs=["o1"], outputs=["o2"], name="s2")
        s3 = Service(P=["P(P3)", "P(P4)"], Q=["Q(Q3)"], inputs=["o1"], outputs=["o2"], name="s3")

        tbcbp.registerService(s1, time=1, QoS=1)
        tbcbp.registerService(s2, time=1, QoS=1)
        tbcbp.registerService(s3, time=1, QoS=100)

        kb0 = KB()
        kb0.tell("P(P1)")
        kb0.tell("P(P2)")
        kb0.set("i1", 1024)

        g = Goal("Q(Q3)")

        plan = tbcbp.composePlan(Goal=g, kb=kb0, use_rl=False)

        for s in plan.getServices():
            assert s in ["s1", "s3"]
            assert s != "s2"

    def testRewardAndPunishCase(self):
        tbcbp = TBCBP()
        tbcbp.registerService(self.s1, QoS=2)

        case1 = Case(P=["p1", "p2"], Q=["q1", "q2"], inputs=["i1"], outputs=["o2"], services=["s1"])
        tbcbp.addCase(case1)
        assert tbcbp.getCase(case1), getQoS() == 2

        tbcbp.getCase(case1).reward()
        assert tbcbp.getCase(case1).getQoS() == 1.0

        tbcbp.getCase(case1).reward()
        assert tbcbp.getCase(case1).getQoS() == 1.0

        tbcbp.getCase(case1).punish()
        assert tbcbp.getCase(case1).getQoS() >= 0.333333333333

        tbcbp.getCase(case1).punish()
        assert tbcbp.getCase(case1).getQoS() == 0.0

        tbcbp.getCase(case1).reward()
        assert tbcbp.getCase(case1).getQoS() == 0.2


if __name__ == "__main__":
    unittest.main()
