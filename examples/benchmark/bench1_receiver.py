import sys
sys.path.append("../..")
import spade
import time

class ReceptorBenchmark1(spade.Agent.Agent):
	
	def __init__(self, jid, password):
		spade.Agent.Agent.__init__(self, jid, password, p2p=True)
		self.nemisores = 0
		
	def _setup(self):
	    self.addBehaviour(behav())
	
	class behav(spade.Behaviour.OneShotBehaviour):
	
	    def _process(self):

    		print "Soy "+self.myAgent.getName()+". Arranco"

    		ntotal = 0
    		while True:
    			msg = self._receive(True)  #//esperem missatge des de'l emisor
    			msg.setReceiver(msg.getSender())		#//tornem el missatge al emisor
    			self.myAgent.send(msg, method="p2ppy")
    			ntotal+=1
    		
		
    	
    
if __name__ == "__main__":
    a = ReceptorBenchmark1(sys.argv[2], "s")
    a.start()
    try:
        while True:
            time.sleep(1)
    except:
        a.stop()
        sys.exit(0)
        