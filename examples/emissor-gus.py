#!/usr/bin/env python

import sys
import os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

from spade import *
from spade.ACLMessage import *
import time
from string import *
from threading import Lock
import threading

class emissor(Agent.Agent):
    nagents=0
    lock=Lock()
    go = threading.Condition()

    def incrementa_agents(self):
        emissor.lock.acquire()
        emissor.nagents=emissor.nagents+1
        emissor.lock.release()
	print "incrementa_agents: nagents = " + str(emissor.nagents)

    def decrementa_agents(self):
        emissor.lock.acquire()
        emissor.nagents=emissor.nagents-1
        emissor.lock.release()
	#print "decrementa_agents: nagents = " + str(emissor.nagents)


    class BehaviourDefecte(Behaviour.Behaviour):
        def _process(self):
	    self.myAgent.msg.setContent(self.myAgent.mode)
            #agafar temps
            t1=time.time()

            #print "Vaig a enviar un missatge"
	    #self.myAgent.msg.setContent("Missatge " +str( self.myAgent.nenviats))
            self.myAgent.send(self.myAgent.msg, method=self.myAgent.mode)
	    #print "Enviat: "+ str(self.myAgent.msg)

	    #print "Estic asperant ..."
            recv = self._receive(True)
            #agafar temps
            t2=time.time()

            if self.myAgent.nenviats < self.myAgent.nmsg:
                self.myAgent.mitjana = self.myAgent.mitjana + t2 - t1
            self.myAgent.nenviats=self.myAgent.nenviats+1
            #print "Missatge enviat"
            #print "Missatge",self.myAgent.nenviats
	    #time.sleep(1)

        def done(self):
            if self.myAgent.nenviats == self.myAgent.nmsg + 5: return True
            else: return False

	def onStart(self):
	    #asperem a la resta
	    emissor.go.acquire()
	    emissor.go.wait()
	    emissor.go.release()

        def onEnd(self):
            #posar estadistiques i si es l'ultim killall
            #print "Mitjana RTT",self.myAgent.mitjana/self.myAgent.nmsg
            
	    self.myAgent.rtt = (self.myAgent.mitjana / self.myAgent.nmsg)*1000
	    self.srtt = str((self.myAgent.mitjana / self.myAgent.nmsg)*1000) + "\n"
	    self.nom_fitxer = self.myAgent.mode.strip()+ "_"+ str(self.myAgent.getName()) + ".log"
	    f = open(self.nom_fitxer, "w")
	    #f.write(str(self.myAgent.getName()))
	    #f.write(" ")
	    f.write(self.srtt)
	    f.close()
	    
            self.myAgent.decrementa_agents()
            #pdb.set_trace()
            #if emissor.nagents == 0:
            #    os.system("killall -9 /usr/bin/python;killall -9 /usr/local/bin/jabberd;rm -f jabber.pid")#canviar!!




    def __init__(self,jid,passw,nagent,ntotal,tmsg,nmsg,multiemissor,mode="p2ppy",debug=[]):
        Agent.Agent.__init__(self,jid,passw, debug=debug)
        #self.addAddress("http://supu.com")
        self.ntotal = ntotal
        self.tmsg = tmsg
        self.nmsg = nmsg
        self.nagent = nagent
        self.multi = multiemissor
	self.mode = mode


    def _setup(self):
        self.mitjana = 0
        self.nenviats = 0
        self.msg = ACLMessage()
        self.msg.setPerformative("inform")
	self.msg.setSender(self.getAID())
        if self.multi:
            self.msg.addReceiver(AID.aid("receptor0@"+host,["xmpp://receptor0@"+host]))
        else:
            self.msg.addReceiver(AID.aid("receptor"+str(self.nagent)+self.sufix+"@"+host,["xmpp://receptor"+str(self.nagent)+self.sufix+"@"+host]))

        #string = ""
        #for i in range(self.tmsg):
        #    string = string + "a"
        #self.msg.setContent(string)


        #esperem a que estiguen tots els agents
        self.incrementa_agents()
	'''
        while emissor.nagents != self.ntotal:
            time.sleep(5)

        if self.nagent==4:
            time.sleep(20)
	'''
	#while not emissor.go:
	#	time.sleep(0.1)

	#self.addBehaviour(self.IqBehav())
        db = self.BehaviourDefecte()
	#self.addBehaviour(db)
        self.setDefaultBehaviour(db)


def test(mode, nagents, tmsg, nmsg):
    global host

    emissors = {}
    #nagents = atoi(sys.argv[1])
    #tmsg = atoi(sys.argv[2])
    #nmsg = atoi(sys.argv[3])
    multiemissor = 0

    #if len(sys.argv) == 5 and sys.argv[4] == "m":
    #    multiemissor = 1

    sufix = ''
    #try:
    #	sufix = sys.argv[4]
    #except:
    #	sufix=''

    for i in range(nagents-1):
        agent="emissor"+str(i)+sufix+"@"+host
        emissors[i] = emissor(agent,"secret",i,nagents,tmsg,nmsg,multiemissor,mode)
        print "agent "+agent+" registrant-se!!"
	emissors[i].sufix = sufix
        emissors[i].start()
        #time.sleep(20)

    agent="emissor"+str(nagents-1)+sufix+"@"+host
    ultim = emissor(agent,"secret",nagents-1,nagents,tmsg,nmsg,multiemissor,mode)
    print "agent "+agent+" registrant-se!!"
    #ultim.start_and_wait()
    ultim.sufix=sufix
    ultim.start()

    time.sleep(2)
    emissor.go.acquire()
    emissor.go.notifyAll()
    print "Go!"
    emissor.go.release()
    start_time = time.time()

    while emissor.nagents != 0:
    	try:
		#elapsed_time = time.time() - start_time
		#print "Tiempo transcurrido: " + str(elapsed_time)
		time.sleep(0.1)
    	except KeyboardInterrupt:
		print "Corten!"
		break

    elapsed_time = time.time() - start_time
    print "Tiempo total transcurrido: " + str(elapsed_time)
    print "Enviados en total " + str(nagents*nmsg*2) + " mensajes de " + str(tmsg) + " bytes"



    media = 0
    for i in range(nagents-1):
	media += emissors[i].rtt 
    	emissors[i].stop()
    media += ultim.rtt
    ultim.stop()
    print "TODOS DEBEN HABER MUERTO YA...."


    media /= nagents    

    return elapsed_time, media


if __name__ == "__main__":
	host = sys.argv[1]
	tmsg = 10
	for mode in ["p2ppy ", "p2p   ", "jabber"]:
		f = open(mode.strip()+".log", "a+")
		for nagents in [1,10,20,30,40,50,60,70,80,90,100]:
			for nmsg in [1,10,20,30,40,50,60,70,80,90,100]:
				print "Testing",mode,str(nagents),str(nmsg)
				results,media = test(mode=mode, nagents=nagents, tmsg=tmsg, nmsg=nmsg)
				#f.write( str(results/(nagents*nmsg*2)) + "\t" + str(nagents) + "\t" + str(nmsg) + "\n" )
				f.write(str(media) + "\t" + str(nagents) + "\t" + str(nmsg) + "\n")
				f.close()
				f = open(mode.strip()+".log", "a+")
				time.sleep(5)
        f.close()

# TODO:parametritzar el host del acc i del desti
