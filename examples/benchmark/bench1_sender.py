import sys

sys.path.append("/home/magentix/pybenchmarks/spade/")
import spade
import time


class EmisorBenchmark1(spade.Agent.Agent):
	
    
	def __init__(self, jid, password, nmsgtot, tmsg, ntotal=0, nemisor=0, smethod="p2p"):
		spade.Agent.Agent.__init__(self, jid, password, p2p=True)
		self.nmsgtot=int(nmsgtot)	#//nombre total de missatges a enviar
    		self.completat=0
    		self.tmsg = int(tmsg)		#//tamany del missatge
        	self.ntotal=int(ntotal)	#//nombre total d'agents
        	self.nemisor=int(nemisor)	#//nombre del agent
        	self.nreceptor=""	#//nombre del primer destinatari
                self.theend = False
                self.smethod = smethod
		self._debug=True
        
    	def _setup(self):
                t = spade.Behaviour.MessageTemplate(spade.Behaviour.ACLTemplate())
        	self.addBehaviour(self.behav(),t)
		
	class behav(spade.Behaviour.OneShotBehaviour):
            def _process(self):
		#print "Soy "+self.myAgent.getName()+". Arranco"
                time.sleep(3)
    		#//Enviem missatge de Ready al agent controlador
    		controlador = spade.AID.aid("controlador@"+self.myAgent.getDomain(), ["xmpp://controlador@"+self.myAgent.getDomain()])
    		msgcont = self.myAgent.newMessage()
    		msgcont.setPerformative("request")
    		msgcont.setContent("Ready")
    		msgcont.addReceiver(controlador)
    		#msgcont.setSender(this.getAid());
    		#print "Soy "+self.myAgent.getName()+". Envio mensaje a controlador" + str(controlador)
    		self.myAgent.send(msgcont, self.myAgent.smethod) #//Gustavo
		self.DEBUG("Enviado mensaje a controlador","ok")
		
    		self._receive(True)			#//esperem missatge Start des d'el controlador
    		self.myAgent.DEBUG("The controller said START!", "ok")

		#//creem missatge i contingut
    		cadena = ""
    		msg = self.myAgent.newMessage()
    		msg.setPerformative("request")

    		for i in range(0, self.myAgent.tmsg):
    			cadena = cadena + "a"
    		msg.setContent(cadena)
    		#//destinatari
    		receiver = spade.AID.aid()
    		#receiver.protocol = "qpid";
    		#receiver.port = "8080";
    		self.myAgent.nreceptor = (self.myAgent.nemisor % self.myAgent.ntotal) + 1
    		#receiver.name = "receptor"+self.myAgent.nreceptor;
    		receiver.setName("receptor"+str(self.myAgent.nreceptor))
    		#receiver.host = "host"+nreceptor;
    		receiver.addAddress("xmpp://receptor"+str(self.myAgent.nreceptor)+"@"+self.myAgent.getDomain())
    		msg.addReceiver(receiver)
    		#msg.setSender(this.getAid());
    		while self.myAgent.completat < self.myAgent.nmsgtot:
    			self.myAgent.send(msg, self.myAgent.smethod)		#//enviem missatge
    			self._receive(True)		#//esperem a la resposta del receptor
    			self.myAgent.completat+=1
    			self.myAgent.nreceptor = (self.myAgent.nreceptor % self.myAgent.ntotal) + 1
    			if self.myAgent.nreceptor == self.myAgent.nemisor:
    			    self.myAgent.nreceptor = (self.myAgent.nreceptor % self.myAgent.ntotal) + 1
    			#receiver.name = "receptor"+nreceptor;
                        receiver = spade.AID.aid()
    			receiver.setName("receptor"+str(self.myAgent.nreceptor))
    			#receiver.host = "host"+nreceptor;
    			receiver.addAddress("xmpp://receptor"+str(self.myAgent.nreceptor)+"@"+self.myAgent.getDomain())
			#print "Envio mensaje "+str(msg)
    		
    		self.myAgent.send(msgcont, self.myAgent.smethod)  #//quan acaba la prova enviem missatge al controlador
                self.DEBUG(self.myAgent.getName() + ": Enviado mensaje de finalizacion al controlador")
                self.myAgent.theend = True
    
if __name__ == "__main__":

    if sys.argv[1] not in ["jabber", "p2p", "p2ppy"]:
        smethod = "p2p"
    else:
        smethod = sys.argv[1]

    a = EmisorBenchmark1(sys.argv[2], "s", sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], smethod=smethod)
    a.start()
    try:
        while not a.theend:
            time.sleep(0.1)
    except:
        a.stop()
    print "Emisor " + sys.argv[2] + " muriendo..."
    sys.exit(0)
