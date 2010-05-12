#! /usr/bin/python

#####################################
#  EXTERNAL EXAMPLE                 #
#####################################
'''
This file communicates a SPADE Agent with
the JADE DF agent, both running on the same host.
The SPADE agent registers a service on the JADE
platform.
You need to be running a SPADE platform and 
a JADE platform on the same host
'''

import sys
import os

sys.path.append('..')

from spade import *
from spade.ACLMessage import *
from string import *
from time import sleep
from xmpp import *

class external(Agent.Agent):
    class SenderBehav(Behaviour.OneShotBehaviour):
        def _process(self):
            sleep(2)
            msg = ACLMessage()
            msg.setPerformative("request")
            msg.addReceiver(AID.aid("external@"+self.myAgent.host, ["http://"+self.myAgent.host+":1099/JADE"]))
            msg.setSender(self.myAgent.getAID())
            msg.setContent("MESSAGE")
            self.myAgent.send(msg)
            print "SENT HTTP MESSAGE"
    

    class RegisterBehav(Behaviour.OneShotBehaviour):
        def _process(self):
            print "REGISTER BEHAV"
            # Register service in DF
            sd = DF.ServiceDescription()
            sd.setName("EXTERNAL_SERVICE")
            sd.setType("organization")
            sd.addProperty({"name":"topology","value":"coallition"})
            dad = DF.DfAgentDescription()
            dad.addService(sd)
            dad.setAID(self.myAgent.getAID())
            #print dad
            otherdf = AID.aid("df@"+self.myAgent.host+":1099/JADE", ["http://"+self.myAgent.host+":7778/acc"])
            res = self.myAgent.registerService(dad, otherdf=otherdf)
            print "DF Register sent: ", str(res)
        
	def onEnd(self):
	    sleep(4)
	    print "DEREGISTER BEHAV"
	    # Register service in DF
            sd = DF.ServiceDescription()
            sd.setName("EXTERNAL_SERVICE")
            sd.setType("organization")
            sd.addProperty({"name":"topology","value":"coallition"})
            dad = DF.DfAgentDescription()
            dad.addService(sd)
            dad.setAID(self.myAgent.getAID())
            #print dad
            otherdf = AID.aid("df@"+self.myAgent.host+":1099/JADE", ["http://"+self.myAgent.host+":7778/acc"])
            res = self.myAgent.deregisterService(dad, otherdf=otherdf)
            print "DF Register sent: ", str(res)
	    print "SERVICE DEREGISTERED"   
	 
    class RecvBehav(Behaviour.Behaviour):
        def _process(self):
            msg = self._receive(True)
            if msg:
                print "Message Received", str(msg)
            
    def _setup(self):
        self.getAID().addAddress("http://"+self.host+":2099/acc")
        self.setDefaultBehaviour(self.RecvBehav())
        self.addBehaviour(self.RegisterBehav())
        self.addBehaviour(self.SenderBehav())


if __name__ == "__main__":
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
            host = "127.0.0.1"
            print "Using: "+host+" as default hostname"
            
    ext = external("external@"+host, "secret")
    ext.host = host
    ext.setDebugToScreen()
    ext.start()

    try:
        while(True):
            sleep(0.1)
    except:
        ext.stop()
        
    sys.exit(0)
