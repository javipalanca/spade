import sys
sys.path.append("/home/magentix/pybenchmarks/spade/")
import spade
import time

class ReceptorBenchmark1(spade.Agent.Agent):
	
	def __init__(self, jid, password, smethod="p2p"):
		spade.Agent.Agent.__init__(self, jid, password, p2p=True)
		self.nemisores = 0
                self.smethod = str(smethod)
		self._debug = True

	def _setup(self):
            temp = spade.Behaviour.ACLTemplate()
            temp.setPerformative("request")
	    t = spade.Behaviour.MessageTemplate(spade.Behaviour.ACLTemplate())
	    self.addBehaviour(self.behav(),t)
	
	class behav(spade.Behaviour.OneShotBehaviour):
	
	    def _process(self):

    		print "Soy "+self.myAgent.getName()+". Arranco"

    		ntotal = 0
                while True:
    			msg = self._receive(True)  #//esperem missatge des de'l emisor
    			self.DEBUG("Llego mensaje de "+msg.getSender().getName(), "info")
                        msg = msg.createReply()
    			#msg.addReceiver(msg.getSender())		#//tornem el missatge al emisor
                        self.myAgent.send(msg, self.myAgent.smethod)
    			ntotal+=1
    		
		
    	
    
if __name__ == "__main__":
    if sys.argv[1] not in ["jabber", "p2p", "p2ppy"]:
        smethod = "p2p"
    else:
        smethod = sys.argv[1]
    a = ReceptorBenchmark1(sys.argv[2], "s", smethod=smethod)
    #a.wui.start()
    a.start()
    try:
        while True:
            time.sleep(0.1)
    except:
        a.stop()
    sys.exit(0)
        
