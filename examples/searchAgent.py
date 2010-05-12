#####################################
#  SEARCH AGENT EXAMPLE             #
#####################################
'''
This file shows a simple agent which just searches for
an agent. Then it prints the results to the screen.
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
			print "Starting behaviour . . ."

		def _process(self):
			print "I'm going to search for an agent"
			aad = spade.AMS.AmsAgentDescription()
			search = self.myAgent.searchAgent(aad)
			for a in search:
				print a.asRDFXML()

		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav()
		self.addBehaviour(b, None)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		host = "127.0.0.1"
	else:
		host = sys.argv[1]
		
	a = MyAgent("agent@"+host, "secret")
	a.setDebugToScreen()
	a.start()
	print "Agent started"

	alive = True
	import time
	while alive:
	    try:
	        time.sleep(1)
	    except KeyboardInterrupt:
	        alive=False
	a.stop()
	sys.exit(0)
