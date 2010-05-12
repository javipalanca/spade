#####################################
#  FSM EXAMPLE                      #
#####################################
'''
This file shows a simple agent which runs
a Finite State Machine Behaviour (FSM).
You need to be running a SPADE platform on the same host
'''

import sys,os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade
import time

class MyAgent(spade.Agent.Agent):
	class StateOne(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			print "This is State One..."
			self.myAgent.counter = self.myAgent.counter + 1
			if self.myAgent.counter > 2:
				self._exitcode = self.myAgent.TRANSITION_TO_TWO
			else:
				self._exitcode = self.myAgent.TRANSITION_DEFAULT

 	class StateTwo(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			print "This is State Two..."
			self.myAgent.counter = self.myAgent.counter + 1
			if self.myAgent.counter > 5:
				self._exitcode = self.myAgent.TRANSITION_TO_THREE
			else:
				self._exitcode = self.myAgent.TRANSITION_DEFAULT
 
	class StateThree(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			print "This is State Three..."
			self.myAgent.counter = self.myAgent.counter + 1
			if self.myAgent.counter > 8:
				self._exitcode = self.myAgent.TRANSITION_TO_FOUR
			else:
				self._exitcode = self.myAgent.TRANSITION_DEFAULT
 
	class StateFour(spade.Behaviour.OneShotBehaviour):
		def _process(self):
			print "This is State Four..."
			self.myAgent.counter = self.myAgent.counter + 1
			if self.myAgent.counter > 11:
				print "Counter ", self.myAgent.counter
				print "Bye Bye"
				self.myAgent._kill()
			else:
				self._exitcode = self.myAgent.TRANSITION_DEFAULT
 
	def _setup(self):
		time.sleep(2)
		print "AdvancedAgent starting . . ."
		self.counter = 0

		self.STATE_ONE_CODE 	= 1
		self.STATE_TWO_CODE 	= 2
		self.STATE_THREE_CODE 	= 3
		self.STATE_FOUR_CODE 	= 4

		self.TRANSITION_DEFAULT		= 0
		self.TRANSITION_TO_ONE 		= 10
		self.TRANSITION_TO_TWO 		= 20
		self.TRANSITION_TO_THREE	= 30
		self.TRANSITION_TO_FOUR 	= 40

		b = spade.Behaviour.FSMBehaviour()
		b.registerFirstState(self.StateOne(), self.STATE_ONE_CODE)
		b.registerState(self.StateTwo(), self.STATE_TWO_CODE)
		b.registerState(self.StateThree(), self.STATE_THREE_CODE)
		b.registerLastState(self.StateFour(), self.STATE_FOUR_CODE)
		
		b.registerTransition(self.STATE_ONE_CODE, self.STATE_ONE_CODE, self.TRANSITION_DEFAULT)
		b.registerTransition(self.STATE_ONE_CODE, self.STATE_TWO_CODE, self.TRANSITION_TO_TWO)
		b.registerTransition(self.STATE_TWO_CODE, self.STATE_TWO_CODE, self.TRANSITION_DEFAULT)
		b.registerTransition(self.STATE_TWO_CODE, self.STATE_THREE_CODE, self.TRANSITION_TO_THREE)
		b.registerTransition(self.STATE_THREE_CODE, self.STATE_THREE_CODE, self.TRANSITION_DEFAULT)
		b.registerTransition(self.STATE_THREE_CODE, self.STATE_FOUR_CODE, self.TRANSITION_TO_FOUR)
		b.registerTransition(self.STATE_FOUR_CODE, self.STATE_FOUR_CODE, self.TRANSITION_DEFAULT)
	
		self.addBehaviour(b, None)

if __name__ == "__main__":
	a = MyAgent("agent@127.0.0.1", "secret")
	a.setDebugToScreen()
	a.start()
	alive = True

	while alive:
	    try:
	        time.sleep(1)
	    except KeyboardInterrupt:
	        alive=False
	a.stop()
	sys.exit(0)
