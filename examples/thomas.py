import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class TravelAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.OneShotBehaviour):
		def onStart(self):
			print "Starting behaviour . . ."

		def _process(self):
			# Show platform info
			pi = self.myAgent.getPlatformInfo()
			print pi

			# Set the receiver data
			receiver = spade.AID.aid(name="OMS@clapton:1099/JADE", 
                                     addresses=["http://clapton.dsic.upv.es:7778/acc"])
			
			# Build the message to register in THOMAS
			self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
			#self.msg.setPerformative("inform")       # Set the "request" FIPA performative
			self.msg.addReceiver(receiver)            # Add the message receiver
			#self.msg.setContent("http://localhost:8080/OMS/OWLS//RegisterUnitProcess.owl UnitID=miunidad1 ParentUnitID= Type=flat Goal=ConquerWorld")
			#self.msg.setContent("http://localhost:8080/OMS/OWLS//SearchService.owl ServicePurpose=")
			self.msg.setContent("AcquireRole('Virtual','Member')")
			
			# Third, send the message with the "send" method of the agent
			self.myAgent.send(self.msg)			
			print "> Register message sent to THOMAS"
			self.rep = ""
			self.rep = self._receive(True, 10)
			if self.rep:
				print "> Message from THOMAS:", self.rep
			self.rep = ""
			self.rep = self._receive(True, 10)
			if self.rep:
				print "> Message from THOMAS:", self.rep
			


		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		self.getAID().addAddress("http://luke.dsic.upv.es:2099/acc")
		b = self.MyBehav()
		#self.addBehaviour(b, None)
		self.setDefaultBehaviour(b)

if __name__ == "__main__":
	a = TravelAgent("agent@luke.dsic.upv.es", "secret")
	a.start()

