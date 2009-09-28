import sys

sys.path.append("../..")
import spade


class EmisorBenchmark1(spade.Agent.Agent):
	
    
	def __init__(jid, password, nmsgtot, tmsg, ntotal=0, nemisor):
		spade.Agent.Agent.__init__(self, jid, password, p2p=True)
		self.nmsgtot=nmsgtot	#//nombre total de missatges a enviar
    	self.completat=0
    	self.tmsg = tmsg		#//tamany del missatge
        self.ntotal=ntotal	#//nombre total d'agents
        self.nemisor=nemisor	#//nombre del agent
        self.nreceptor=""	#//nombre del primer destinatari
        
    def _setup(self):
        self.addBehaviour(behav())
		
    class behav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
		    print "Soy "+self.myAgent.getName()+". Arranco"
    		#//Enviem missatge de Ready al agent controlador
    		controlador = spade.AID.aid("controlador@"+self.myAgent.getDomain(), ["xmpp://controlador@"+self.myAgent.getDomain()])
    		msgcont = self.myAgent.newMessage()
    		msgcont.setPerformative("request")
    		msgcont.setContent("Ready")
    		msgcont.setReceiver(controlador)
    		#msgcont.setSender(this.getAid());
    		print "Soy "+self.myAgent.getName()+". Envio mensaje a controlador"
    		self.myAgent.send(msgcont, method="p2ppy") #//Gustavo
		
		
    		self._receive(True)			#//esperem missatge Start des d'el controlador
		
    		#//creem missatge i contingut
    		cadena = ""
    		msg = = self.myAgent.newMessage()
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
    		msg.setReceiver(receiver)
    		#msg.setSender(this.getAid());
    		while self.myAgent.completat < self.myAgent.nmsgtot:
    			self.myAgent.send(msg, method="p2ppy")					#//enviem missatge
    			self._receive(True)		#//esperem a la resposta del receptor
    			self.myAgent.completat+=1
    			self.myAgent.nreceptor = (self.myAgent.nreceptor % self.myAgent.ntotal) + 1
    			if self.myAgent.nreceptor == self.myAgent.nemisor:
    			    self.myAgent.nreceptor = (self.myAgent.nreceptor % self.myAgent.ntotal) + 1
    			#receiver.name = "receptor"+nreceptor;
    			receiver.setName("receptor"+str(self.myAgent.nreceptor))
    			#receiver.host = "host"+nreceptor;
    			receiver.addAddress("xmpp://receptor"+str(self.myAgent.nreceptor)+"@"+self.myAgent.getDomain())
    		
    		self.myAgent.send(msgcont, method="p2ppy")					#//quan acaba la prova enviem missatge al controlador
    	
    
if __name__ == "__main__":
    a = EmisorBenchmark1(sys.argv[2], "s", sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    a.start()
    try:
        while True:
            time.sleep(1)
    except:
        a.stop()
        sys.exit(0)