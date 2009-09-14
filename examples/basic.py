import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.OneShotBehaviour):
		def onStart(self):
			self.myAgent.DEBUG("Starting behaviour . . .")

		def _process(self):
			print "Hello World from a OneShot"
			pi = self.myAgent.getPlatformInfo()
			self.myAgent.DEBUG(str(pi))

		def onEnd(self):
			self.myAgent.DEBUG("Ending behaviour . . .")

	def _setup(self):
		self.DEBUG("MyAgent starting . . .")
		b = self.MyBehav()
		self.addBehaviour(b, None)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		host = "127.0.0.1"
	else:
		host = sys.argv[1]
	a = MyAgent("agent@"+host, "secret")
	a.wui.start()
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
	    

