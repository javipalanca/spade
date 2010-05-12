#####################################
#  MODIFY EXAMPLE                   #
#####################################
'''
This file shows a simple agent which just modifies its
own information stored in the AMS agent.
You need to be running a SPADE platform on the same host
'''

import sys,os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.OneShotBehaviour):
		def onStart(self):
			print "Starting behaviour . . ."

		def _process(self):
			print "I'm going to modify my data"
			aad = spade.AMS.AmsAgentDescription()
			#aad.setAID(spade.AID.aid("agent@127.0.0.1",["xmpp://agent@127.0.0.1"]))
			aad.ownership = "FREE" 
			result = self.myAgent.modifyAgent(aad)
			if result:
				print "Modification OK"
			print "I'm going to check the modification"
			search = self.myAgent.searchAgent(aad)
                        print search

		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav()
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
