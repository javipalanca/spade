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
			pi = self.myAgent.getPlatformInfo()
			#print pi
			#print type(pi)
			receiver = spade.AID.aid(name="OMS@clapton:1099/JADE", 
                                     addresses=["http://clapton.dsic.upv.es:7778/acc"])
			
			# Second, build the message
			self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
			self.msg.setPerformative("request")        # Set the "inform" FIPA performative
			self.msg.addReceiver(receiver)            # Add the message receiver
			#self.msg.setContent("http://localhost:8080/OMS/OWLS//RegisterUnitProcess.owl UnitID=miunidad1 ParentUnitID= Type=flat Goal=ConquerWorld")
			self.msg.setContent("http://localhost:8080/OMS/OWLS//SearchService.owl ServicePurpose=")
			
			# Third, send the message with the "send" method of the agent
			self.myAgent.send(self.msg)			
			print "Message sent to THOMAS"
			self.rep = ""
			self.rep = self._receive(True, 10)
			if self.rep:
				print "Message from THOMAS:", self.rep
			self.rep = ""
			self.rep = self._receive(True, 10)
			if self.rep:
				print "Message from THOMAS:", self.rep
			


		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		self.getAID().addAddress("http://thx1138.dsic.upv.es:2099/acc")
		b = self.MyBehav()
		#self.addBehaviour(b, None)
		self.setDefaultBehaviour(b)

if __name__ == "__main__":
	a = MyAgent("agent@thx1138.dsic.upv.es", "secret")
	a.start()

