#!/usr/bin/env python

import sys
import os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

from spade import *
from spade.ACLMessage import *
from string import *
from time import sleep
from xmpp import *

class receptor(Agent.Agent):

    class BehaviourDefecte(Behaviour.Behaviour):

        def _process(self):
            msg = self._receive(True)
            if "ACLMessage" not in str(msg.__class__):
                print "BD RECEIVED A NON_FIPA MESSAGE"
                return

            emissor = msg.getSender()
            msg.removeReceiver(self.myAgent.getAID())
            msg.setSender(self.myAgent.getAID())
            msg.addReceiver(emissor)
            self.myAgent.send(msg, method=msg.getContent().strip())

        def onStart(self):
            #self.myAgent.getRoster()
            #print "RECEPTOR BEHAV: "+ str(self.getQueue())
            pass

    class EBehav(Behaviour.EventBehaviour):
        def _process(self):
            print "E BEHAV STARTED"
            i = 1
            try:
                msg = self._receive(True)
                while i < 10:
                    print "###RECIBIDO:", str(msg), str(i)
                    i = i + 1
                    sleep(1)

            except Exception, e:
                print "EXCEPTION: ", str(e)

    def _setup(self):
        #print "RECEPTOR: "+ str(self.getQueue())
        #self.setDefaultBehaviour(db)
        #self.addBehaviour(self.EBehav(), Behaviour.MessageTemplate(Message()))
        db = self.BehaviourDefecte()
        self.addBehaviour(db, Behaviour.MessageTemplate(Behaviour.ACLTemplate()))


if __name__ == "__main__":
    receptors = []
    host = sys.argv[1]
    nagents = atoi(sys.argv[2])
    if len(sys.argv)>2:
    	try:
		sufix = sys.argv[3]
    	except:
		sufix = ''
    else: sufix = ''
    for i in range(nagents):
        agent = "receptor"+str(i)+sufix+"@"+ host
	#print "registrant agent " + str(i)
        receptors.append( receptor(agent,"secret") )
        #print "agent "+agent+" registrant-se!!"
        receptors[i].start()

    while len(receptors) > 0:
		try:
			for a in receptors:
				if not a.isRunning():
					receptors.remove(a)
			sleep(0.1)
		except:
			while len(receptors) > 0:
				print "Stopping " + str(receptors[0].getName())
				receptors[0].stop()
				receptors.pop(0)
			break

