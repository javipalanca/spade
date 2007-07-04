#! /usr/bin/python

from spade import *
from spade.ACLMessage import *
import os
import time
import sys
import pdb
from string import *
from threading import Lock

class emissor(Agent.Agent):

    class BehaviourDefecte(Behaviour.Behaviour):
                
        def _process(self):
            #agafar temps

	    if self.myAgent.nmsg != 0:
	            #print "Vaig a enviar un missatge"
		    self.myAgent.send(self.myAgent.msg)
           
		    #print "Estic asperant ..." 
	            recv = self._receive(True)
	            #print "He rebut la contestacio"

		    print str(recv)
		    self.myAgent.nmsg = self.myAgent.nmsg-1

    def __init__(self,jid,passw,nmsg,debug=[]):
        Agent.Agent.__init__(self,jid,passw, debug=debug)
        self.nmsg = nmsg
           

    def _setup(self):
        
	self.msg = ACLMessage()
	self.msg.addReceiver(AID.aid("ping@endor",["xmpp://ping@endor"]))
	self.msg.setPerformative("query-ref")
	self.msg.setContent("ping")

        db = self.BehaviourDefecte()
        self.setDefaultBehaviour(db)

        

if __name__ == "__main__":
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
            host = "sandoval.dsic.upv.es"
            print "No s'ha pogut obtindre nom de host, utilitzant: "+host+" per defecte"

    nmsg = atoi(sys.argv[1])
        
    agent="emissor-ping@"+host
    e = emissor(agent,"secret",nmsg)
    print "agent "+agent+" registrant-se!!"
    #ultim.start_and_wait()
    e.start()
    try:
	    while True:
		#elapsed_time = time.time() - start_time
		#print "Tiempo transcurrido: " + str(elapsed_time)
		time.sleep(0.1)
    except:
	e.stop()

# TODO:parametritzar el host del acc i del desti
