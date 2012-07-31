#####################################
#  BDI EXAMPLE                      #
#####################################
'''
This file shows a simple client agent which
activates a Goal to be pursued.
The needed services are provided by the two
agents contained in server1BDI.py and server2BDI.py
This agent uses a BDI Behaviour
You need to be running a SPADE platform host
'''
import os
import sys
import unittest
sys.path.append('../..')
sys.path.append('..')

import spade
from spade.bdi import Goal
from spade.Agent import BDIAgent

def MygoalCompletedCB(goal):
    global goalCompleted
    goalCompleted = True


host = "127.0.0.1"

a = BDIAgent("clientbdi@"+host,"secret")
a.setDebugToScreen()
a.start()

goalCompleted=False

a.saveFact("Value",0)

a.setGoalCompletedCB(MygoalCompletedCB)

a.addGoal(Goal("Var(Myoutput2,2,Int)"))

import time
counter = 0
while not goalCompleted and counter<10:
    time.sleep(1)
    counter+=1

a.stop()
sys.exit()