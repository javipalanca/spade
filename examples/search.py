#!/usr/bin/env python
# encoding: utf-8
import sys
import os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

from spade import *
from spade.ACLMessage import *
from string import *
from time import sleep
from xmpp import *

class SearchAgent(Agent.Agent):
    class BehaviourDefecte(Behaviour.Behaviour):
        def _process(self):
            sleep(1)

        def onStart(self):
            dad = DF.DfAgentDescription()
            ds = DF.ServiceDescription()
            ds.setType("testservice")
            #ds.addProperty({'item':self._item})
            dad.addService(ds)
            search = self.myAgent.searchService(dad)
            print "SEARCH:",str(search)

    def _setup(self):
        db = self.BehaviourDefecte()
        self.addBehaviour(db, Behaviour.MessageTemplate(Behaviour.ACLTemplate()))


if __name__ == "__main__":
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
            host = "thx1138.dsic.upv.es"
            print "No s'ha pogut obtindre nom de host, utilitzant: "+host+" per defecte"

    ag = SearchAgent("search@"+host, "secret")
    ag.start()

    while True:
		try:
			sleep(0.5)
		except:
			ag.stop()
			break
