import sys

sys.path.append("../..")
import spade

import time

class ControladorBenchmark1(spade.Agent.Agent):
	

	def __init__(self, jid, password, ntotal=0):
        spade.Agent.Agent.__init__(self, jid, password, p2p=True)
        self.ntotal = ntotal
	    self.nagents=0
	    self.nacabats = 0
	
	def _setup(self):
	    self.addBehaviour(behav())

    class behav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
		    print "Soy "+self.myAgent.getName()+". Arranco"
    		#Esperem a rebre el Ready de tots els agents emisors
    		while self.myAgent.nagents < self.myAgent.ntotal:
    			self._receive(block=True)
    			nagents+=1
		
    		msg = self.myAgent.newMessage()
    		msg.setPerformative("request")
    		msg.setContent("Start!")
    		#msg.setSender(self.getAID())
    		receiver = spade.AID.aid()
    		#receiver.protocol = "qpid";
    		#receiver.port = "8080";
    		#//enviem un missatge a cada emisor per a que comencen a emetre missatges
    		t1 = time.time()
    		for i in range(1, self.myAgent.ntotal):
    			#receiver.host = "host"+i;
    			#receiver.name = "emisor"+i;
    			receiver.setName("emisor"+str(i)+"@"+self.myAgent.getDomain())
    			receiver.addAddress("xmpp://emisor"+str(i)+"@"+self.myAgent.getDomain())
    			msg.setReceiver(receiver)
    			self.myAgent.send(msg, method="p2ppy")
    		
            print "Soy "+self.myAgent.getName()+". Mensajes enviados a receptores"
    
    		#//this.send_multicast(msg);
    		
		
    		#//esperem a que ens responguen tots amb ok
    		while self.myAgent.nacabats < self.myAgent.ntotal:
    			self._receive(True)
    			#self.myAgent.nacabats += 1
    		
		
    		#//Mostrem resultat per pantalla
    		t2 = time.time()
    		print "Prova acabada!"
    		print "Bench Time (s): "+ str(t2 - t1)
    	
    
if __name__ == "__main__":
    a = ControladorBenchmark1(sys.argv[2], "s", sys.argv[3])
    a.start()
    try:
        while True:
            time.sleep(1)
    except:
        a.stop()
        sys.exit(0)
        