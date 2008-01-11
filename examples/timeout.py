import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.TimeOutBehaviour):
		def onStart(self):
			print "Starting behaviour . . ."

		def timeOut(self):
			print "The timeout has ended"

		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav(5)
		self.addBehaviour(b, None)

if __name__ == "__main__":
	a = MyAgent("agent@thx1138.dsic.upv.es", "secret")
	a.start()

