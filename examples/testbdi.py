#####################################
#  BDI EXAMPLE                      #
#####################################
'''
This file shows a simple BDI agent.
It runs a plan composed of the sequence Service 1 and Service 2.
The plan achieves the goal "Value(2)", which is the goal of
the agent "BDIAgent".
You need to be running a SPADE platform on the same host
'''

import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade
from spade.bdi import *

agent = BDIAgent("bdi@127.0.0.1","secret")
agent.setDebugToScreen()
agent.addBelieve(expr("Value(0)"))

g = Goal(expr("Value(2)"))

class Serv1(Service):
    def run(self):
        print "Service 1 running"
        self.addBelieve(expr("Value(1)"))
class Serv2(Service):
    def run(self):
        print "Service 2 running"
        self.addBelieve(expr("Value(2)"))
        
s1 = Serv1(P=expr("Value(0)"),Q=expr("Value(1)"))
s2 = Serv2(P=expr("Value(1)"),Q=expr("Value(2)"))

p = Plan(P=expr("Value(0)"),Q=expr("Value(2)"))
p.appendService(s1)
p.appendService(s2)

agent.addPlan(p)
agent.addGoal(g)

agent.start()

import time
try:
    while True:
        time.sleep(1)
except:
    agent.stop()

sys.exit(0)
