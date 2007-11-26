import spade
import time

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.Behaviour):
		def onStart(self):
			print "Starting behaviour . . ."
			self.counter = 0

		def _process(self):
			print "Counter:", self.counter
			self.counter = self.counter + 1
			time.sleep(1)

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav()
		self.addBehaviour(b, None)

if __name__ == "__main__":
	a = MyAgent("agent@thx1138.dsic.upv.es", "secret")
	a.start()

