#! /usr/bin/python

import sys
import os
import time
#sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')
from spade import *
class Example(Agent.Agent):
    def _setup(self):
        entry = "Starting Organization Behaviour"


	
        
    def _process(self):
	 pass
class MyOrganization(Organization_new.Organization_new):
    def _process(self):
	#u=MyUnit(agent=self.myAgent, nick="nic2", name="unit1",type="Hierarchy",password="pass",agentList=["agent2@apolo.dsic.upv.es"])
	#self.addUnit(u)
	#u=MyUnit(agent=self.myAgent, nick="nic2", name="unit2",type="Hierarchy",password="pass",agentList=["agent2@apolo.dsic.upv.es"])
      	u=MyUnit(agent=self.myAgent, nick="nic2", name="unit2",type="Hierarchy",password="pass",agentList=["agent@thx1138.dsic.upv.es"])
	self.addUnit(u)

	
class MyUnit(Unit_new.Unit_new):
    def _process(self):
	    if self.name=="unit1":
		    self.setMinAgents(10)
		    self.addAdmin("agent2@apolo.dsic.upv.es")
	    		
	    print self.getMemberList()
	    
if __name__ == "__main__":
    """
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
    """

    #agent = "agent@apolo.dsic.upv.es"
    agent = "agent@thx1138.dsic.upv.es"
    print "Agent "+agent+" registering"
    b = Example(agent,"pasword")
    b.start()
 
    o=MyOrganization(b,nick="nick", name="sala",type="Flat", goalList=[])
    b.createOrganization(o)

    





