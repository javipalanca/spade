#####################################
#  TIMEOUT EXAMPLE                  #
#####################################
'''
This file shows a simple agent which just runs a TimeOut
Behaviour that waits for 5 seconds before expiring.
You need to be running a SPADE platform on the same host
'''

import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.TimeOutBehaviour):
		def onStart(self):
			print "Starting behaviour . . ."

		def timeOut(self):
			print "The timeout has expired"

		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav(5)
		self.addBehaviour(b, None)

if __name__ == "__main__":
	a = MyAgent("agent@127.0.0.1", "secret")
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