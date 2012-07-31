#####################################
#  BDI EXAMPLE                      #
#####################################
'''
This file presents a server agent for the bdi example
It serves a service called "s2", which is registered in the DF
You need to be running a SPADE platform host
'''
import os
import sys
import unittest
sys.path.append('../..')
sys.path.append('..')

import spade
from spade.Agent import Agent

def s2_method(Myoutput1):
        return {"Myoutput2":2}

host = "127.0.0.1"

a = Agent("server2bdi@"+host,"secret")
a.setDebugToScreen()
a.start()

s2 = spade.DF.Service(name="s2", owner=a.getAID(), inputs=["Myoutput1"],outputs=["Myoutput2"],P=["Var(Myoutput1,1,Int)"],Q=["Var(Myoutput2,2,Int)"])

a.registerService(s2,s2_method)

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

