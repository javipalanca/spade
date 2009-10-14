import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade
from spade.bdi import *

agent = BDIAgent("bdi@127.0.0.1","secret")
agent.setDebug()
agent.addBelieve(expr("Value(0)"))

g = Goal(expr("Value(2)"))

class Serv1(Service):
    def run(self):
        print "Servicio 1 ejecutandose"
        self.addBelieve(expr("Value(1)"))
class Serv2(Service):
    def run(self):
        print "Servicio 2 ejecutandose"
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
    pass
