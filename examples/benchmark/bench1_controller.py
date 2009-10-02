import sys

sys.path.append("/home/magentix/pybenchmarks/spade/")
import spade

import time

class ControladorBenchmark1(spade.Agent.Agent):
	
	def __init__(self, jid, password, ntotal=1, smethod="p2p"):
            spade.Agent.Agent.__init__(self, jid, password, p2p=True)
            self.ntotal = int(ntotal)
	    self.nagents=0
	    self.nacabats = 0
	    self._debug=True
            self.smethod = str(smethod)
            self.theend = False
	
	def _setup(self):
	    t = spade.Behaviour.MessageTemplate(spade.Behaviour.ACLTemplate())	    
	    self.addBehaviour(self.behav(),t)

	class behav(spade.Behaviour.OneShotBehaviour):
            def _process(self):
		self.myAgent.DEBUG("Soy "+self.myAgent.getName()+". Arranco","ok")
    		#Esperem a rebre el Ready de tots els agents emisors
    		while self.myAgent.nagents < self.myAgent.ntotal:
    			self._receive(block=True)
			self.myAgent.DEBUG("Recibido agente emisor "+str(self.myAgent.nagents+1),"ok")
  			self.myAgent.nagents+=1

                self.DEBUG("Recibidos todos los arranques de los emisores","ok")		
    		msg = self.myAgent.newMessage()
    		msg.setPerformative("request")
    		msg.setContent("Start!")
    		#msg.setSender(self.getAID())
    		#receiver.protocol = "qpid";
    		#receiver.port = "8080";
    		#//enviem un missatge a cada emisor per a que comencen a emetre missatges
		self.myAgent.DEBUG("Envio mensaje de START","ok")
    		t1 = time.time()
    		for i in range(1, self.myAgent.ntotal+1):
                        receiver = spade.AID.aid()
    			#receiver.host = "host"+i;
    			#receiver.name = "emisor"+i;
    			receiver.setName("emisor"+str(i)+"@"+self.myAgent.getDomain())
    			receiver.addAddress("xmpp://emisor"+str(i)+"@"+self.myAgent.getDomain())
    			msg.addReceiver(receiver)
    			self.myAgent.send(msg, self.myAgent.smethod)
    		
                self.myAgent.DEBUG("Soy "+self.myAgent.getName()+". Mensajes enviados a emisores","ok")
    
    		#//this.send_multicast(msg);
    		
		
    		#//esperem a que ens responguen tots amb ok
    		while self.myAgent.nacabats < self.myAgent.ntotal:
    			self._receive(True)
    			self.myAgent.nacabats += 1
                self.myAgent.DEBUG("Acabados agentes "+str(self.myAgent.nacabats),"ok")    		
		
    		#//Mostrem resultat per pantalla
    		t2 = time.time()
    		print "Prova acabada!"
    		print "Bench Time (s): "+ str(t2 - t1)
		self.myAgent.theend = True
    	
    
if __name__ == "__main__":
    if sys.argv[1] not in ["jabber", "p2p", "p2ppy"]:
        smethod = "p2p"
    else:
        smethod = sys.argv[1]

    a = ControladorBenchmark1(sys.argv[2], "s", sys.argv[3], smethod=smethod)
    #a.wui.start()
    a.start()
    try:
        while not a.theend:
            time.sleep(0.1)
    except:
        a.stop()
    print "Controller muriendo..."
    sys.exit(0)
