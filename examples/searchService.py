#!/usr/bin/env python
# encoding: utf-8
#####################################
#  SEARCH SERVICE EXAMPLE           #
#####################################
'''
This file shows a simple agent that just searches for a
service, which type is "testservice", and prints it.
You need to be running a SPADE platform on the same host
'''


import sys
import os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

from spade import *
from spade.ACLMessage import *
from string import *
from time import sleep
from xmpp import *

class SearchService(Agent.Agent):
    class BehaviourDef(Behaviour.Behaviour):
        def _process(self):
            sleep(1)

        def onStart(self):
            dad = DF.DfAgentDescription()
            ds = DF.ServiceDescription()
            ds.setType("testservice")
            dad.addService(ds)
            search = self.myAgent.searchService(dad)
            print "SEARCH:",str(search)

    def _setup(self):
        db = self.BehaviourDef()
        self.addBehaviour(db, Behaviour.MessageTemplate(Behaviour.ACLTemplate()))


if __name__ == "__main__":
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
            host = "127.0.0.1"

    ag = SearchService("search@"+host, "secret")
    ag.setDebugToScreen()
    ag.start()

    while True:
		try:
			sleep(0.5)
		except:
			ag.stop()
			break
