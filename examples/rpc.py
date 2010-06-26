#####################################
#  RPC EXAMPLE                    #
#####################################
'''
This file shows a simple agent which just asks for the 
Platform Information (pi) to the AMS agent and prints it 
to the debug system.
It uses a OneShot Behaviour
You need to be running a SPADE platform on the same host
'''

import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.OneShotBehaviour):
	    
		def onStart(self):
			self.myAgent.DEBUG("Starting behaviour . . .",'ok')
			
			s = spade.DF.Service(name="RPCmethod",owner=self.myAgent.getAID(),P="P")			
			
			self.myAgent.registerService(s,self.myAgent.RPCmethod)
			
			self.myAgent.DEBUG("Service registered "+str(s),'ok')

		def _process(self):
		    self.myAgent.DEBUG("Starting process . . .")
		    
		    s = self.myAgent.searchService(spade.DF.Service(name="RPCmethod"))
		    self.myAgent.DEBUG("Found service " + str(s[0]),'ok')
		    self.myAgent.DEBUG("Invoking service",'ok')
		    p = self.myAgent.invokeService(s[0])
		    self.myAgent.DEBUG("Service returned "+ str(p),'ok')


		def onEnd(self):
			self.myAgent.DEBUG("Ending behaviour . . .",'ok')
			s = self.myAgent.searchService(spade.DF.Service(name="RPCmethod"))
			if s: self.myAgent.deregisterService(s[0])

        def _setup(self):
            self.DEBUG("MyAgent starting . . .")
            b = self.MyBehav()
            self.addBehaviour(b, None)

        def RPCmethod(self,P):
            s = ""
            for p in P:
                s+=p+"_"
            return [s+"_processed",1000]

if __name__ == "__main__":
	if len(sys.argv) < 2:
		host = "127.0.0.1"
	else:
		host = sys.argv[1]
	a = MyAgent("agent@"+host, "secret")
	a.wui.start()
	a.setDebugToScreen()
	a.start()
	
	alive = True
	import time
	while alive:
	    try:
	        time.sleep(1)
	    except KeyboardInterrupt:
	        alive=False
	a.stop()
	sys.exit(0)
	    

