import os
import sys
import unittest
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade
from spade.bdi import *

host = "127.0.0.1"

class Serv1(Service):
    def run(self):
        self.addBelieve(expr("Value(1)"))
class Serv2(Service):
    def run(self):
        self.addBelieve(expr("Value(2)"))

class MServ(Service):
	def  __init__(self, P=None, Q=None, inputs={},outputs={}, belief=""):
		Service.__init__(self,P, Q, inputs,outputs)
		self.belief = str(belief)
	def run(self):
	    self.addBelieve(expr("Value("+self.belief+")"))
	
class BDITestCase(unittest.TestCase):
	
	def setUp(self):

		self.a = BDIAgent("bdi@"+host,"secret")

	def tearDown(self):
		#self.a.stop()
		pass
		
	def testAddBelief(self):
		self.a.addBelieve(expr("Value(0)"))
		
		self.assertEqual(self.a.askBelieve(expr("Value(0)")), {})

	def testAddGoal(self):
		g = Goal(expr("Value(2)"))
		self.a.addGoal(g)

		self.assertEqual(len(self.a.goals),1)
		self.assertEqual(self.a.goals[0].expression,expr("Value(2)"),{})

	def testAddService(self):
		p = Plan(P=expr("Value(0)"),Q=expr("Value(2)"))
		s1 = Serv1(P=expr("Value(0)"),Q=expr("Value(1)"))
		s2 = Serv2(P=expr("Value(1)"),Q=expr("Value(2)"))
		
		p.appendService(s1)
		self.assertEqual(len(p.services),1)
		
		p.appendService(s2)
		self.assertEqual(len(p.services),2)
		
	def testAddPlan(self):
		p = Plan(P=expr("Value(0)"),Q=expr("Value(2)"))
		self.a.addPlan(p)

		self.assertEqual(len(self.a.plans),1)
		self.assertEqual(self.a.plans[0].P,expr("Value(0)"))
		self.assertEqual(self.a.plans[0].Q,expr("Value(2)"))
	
	def testSimpleGoalCompleted(self):
		self.a.addBelieve(expr("Value(0)"))
		self.a.addGoal(Goal(expr("Value(1)")))
		p = Plan(P=expr("Value(0)"),Q=expr("Value(1)"))
		s1 = Serv1(P=expr("Value(0)"),Q=expr("Value(1)"))
		p.appendService(s1)
		self.a.addPlan(p)
		
		self.assertNotEqual(self.a.askBelieve(expr("Value(1)")),{})
		self.assertEqual(self.a.askBelieve(expr("Value(0)")), {})

		self.a.start()

		import time
		time.sleep(2)

		self.assertEqual(self.a.askBelieve(expr("Value(1)")), {})

	def testMultiGoalCompleted(self):
		self.a.addBelieve(expr("Value(0)"))
		self.a.addGoal(Goal(expr("Value(10)")))
		p = Plan(P=expr("Value(0)"),Q=expr("Value(10)"))
		for i in range(0,10):
			s = MServ(P=expr("Value("+str(i)+")"),Q=expr("Value("+str(i+1)+")"),belief=i+1)
			p.appendService(s)
		self.a.addPlan(p)

		self.assertNotEqual(self.a.askBelieve(expr("Value(10)")),{})
		self.assertEqual(self.a.askBelieve(expr("Value(0)")), {})

		self.a.start()

		import time
		time.sleep(4)

		self.assertEqual(self.a.askBelieve(expr("Value(10)")), {})

if __name__ == "__main__":
    unittest.main()