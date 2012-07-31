#####################################
#  BDI EXAMPLE                      #
#####################################
'''
This file presents a server agent for the bdi example
It serves a service called "s1", which is registered in the DF
You need to be running a SPADE platform host
'''
import os
import sys
import unittest
sys.path.append('../..')
sys.path.append('..')

import spade
from spade.Agent import Agent

def s1_method(Value):
        return {"Myoutput1":1}

host = "127.0.0.1"

a = Agent("server1bdi@"+host,"secret")
a.setDebugToScreen()
a.start()

s1 = spade.DF.Service(name="s1", owner=a.getAID(), inputs=["Value"],outputs=["Myoutput1"],P=["Var(Value,0,Int)"],Q=["Var(Myoutput1,1,Int)"])

a.registerService(s1,s1_method)                

import time
tmp=True
while tmp:
    try:
        time.sleep(5)
    except:
        tmp=False

s = spade.DF.Service()
s.setOwner(a.getAID())
a.deregisterService(s)

a.stop()
sys.exit()

