#! /usr/bin/python

import sys
import os
import time
#sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')
from spade import *
class Example(Agent.Agent):
    def _setup(self):
        #entry = "Starting Organization Behaviour"
        #self.addBehaviour(Organization.AgentOrganization(self,nick="nick", name="sala", goalList=[],agentList=["agent@apolo.dsic.upv.es"]))
	pass
    def _process(self):
	    pass
class MyOrganization(Organization_new.Organization_new):
    def _process(self):
	u=self.getUnitList()
	print u
	for i in u:
          u=MyUnit(self.myAgent,nick="nickos", name=i,password="pass")
          self.joinUnit(u)
	
	
class MyUnit(Unit_new.Unit_new):
    def _process(self):
	self.sendMessage("Hola")
	print "Nombre"+self.name+" "+str(self.getOwnerList())
	u=MyUnit2(agent=self.myAgent, nick="nic2", name="unit11",type="Hierarchy",password="pass",agentList=["agent2@apolo.dsic.upv.es"])
      	self.addUnit(u)
	pass
class MyUnit2(Unit_new.Unit_new):
    def _process(self):
	print "Nombre"+self.name+" "+str(self.getOwnerList())
	pass	
	
if __name__ == "__main__":
    """
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
    """
#agent = "agent2@apolo.dsic.upv.es"
agent = "agent@thx1138.dsic.upv.es"
print "Agent "+agent+" registering"
b = Example(agent,"pasword")
b.start()
lista= b.getOrganizationList()
print lista
try:
	for i in lista:
		b.getOrganizationInfo(i)
		o=MyOrganization(b,nick="nick2", name=i)
		b.joinOrganization(o)
except: 
	pass


