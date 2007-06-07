#! python
from spade import *
import time


# En este ejemplo, se puede ver como hacer un agente PingAgent con un comportamiento!
class PingAgentOneBehaviour(Agent.Agent):
	class WaitPingAndReplyBehaviour(Behaviour.Behaviour):
		def __init__(self):
			Behaviour.Behaviour.__init__(self)
		def process(self):
			msg = self.blockingReceive(1)
			if (msg != None):
				if (msg.getPerformative() != 'not-understood'):
					reply = msg.createReply()
					reply.setSender(self.myAgent.getAID())
					if (msg.getPerformative() == 'query-ref'):
						if (msg.getContent() == "ping"):
							reply.setPerformative('inform')
							reply.setContent("alive")
						else:
							reply.setPerformative('not-understood')
							reply.setContent("( UnexpectedContent (expected ping))")
					else:
						reply.setPerformative('not-understood')
						reply.setContent("( (Unexpected-act " + msg.getPerformative()+") ( expected (query-ref :content ping)))")
					
					self.myAgent.send(reply)
				else:
					print "PingAgent: A msg with 'not-understood' performative has arrival" 
	
	def __init__(self, agentjid, passwd):
		Agent.Agent.__init__(self, agentjid, passwd)
	def setup(self):
		self.setDefaultBehaviour(self.WaitPingAndReplyBehaviour())
"""
# En este ejemplo, se puede ver como hacer un agente PingAgent con mas de un comportamiento!
class PingAgentMoreBehaviour(Agent.Agent):
	class ReplyBehaviour(Behaviour.Behaviour):
		def __init__(self):
			Behaviour.Behaviour.__init__(self)
		def process(self):
			msg = self.receive()
			if (msg != None):
				reply = msg.createReply()
				reply.setSender(self.myAgent.getAID())
				if (msg.getPerformative() == 'query-ref'):
					if (msg.getContent() == "ping"):
						reply.setPerformative('inform')
						reply.setContent("alive")
					else:
						reply.setPerformative('not-understood')
						reply.setContent("( UnexpectedContent (expected ping))")
				else:
					reply.setPerformative('not-understood')
					reply.setContent("( (Unexpected-act " + msg.getPerformative()+") ( expected (query-ref :content ping)))")
				
				self.myAgent.send(reply)
				print "Enviada respuesta..."
				
	class DefaultBehaviour(Behaviour.Behaviour):
		def __init__(self):
			Behaviour.Behaviour.__init__(self)
		def process(self):
			msg = self.receive()
			if (msg != None):
				print "PingAgent: A msg with 'not-understood' performative has arrival" 

	
	def __init__(self, agentjid, passwd):
		Agent.Agent.__init__(self, agentjid, passwd)
	def setup(self):
		ACLtemplate = ACLMessage.ACLMessage()
		ACLtemplate.setPerformative('not-understood')
		template = (~Behaviour.MessageTemplate(ACLtemplate))
		
		self.addBehaviour(self.ReplyBehaviour(), template)
		self.setDefaultBehaviour(self.DefaultBehaviour())






class PingSender(Agent.Agent):
	class PingBehaviour(Behaviour.PeriodicBehaviour):
		def __init__(self, time):
			Behaviour.PeriodicBehaviour.__init__(self, time)
			self._msg = ACLMessage.ACLMessage()
			self._msg.addReceiver(AID.aid("test1@localhost", [ "xmpp://platform@jabber.org" ]))
			self._msg.setPerformative('query-ref')
			self._msg.setContent("ping")
		def onTick(self):
			self._msg.setSender(self.myAgent.getAID())
			self.myAgent.send(self._msg)
		
	class DefBehaviour(Behaviour.Behaviour):
		def process(self):
			msg = self.receive()
			if (msg != None):
				print "Msg: " + msg.getContent()
			
	
	def __init__(self, agentjid, passwd):
		Agent.Agent.__init__(self, agentjid, passwd)
	def setup(self):
		self.addBehaviour(self.PingBehaviour(5))
		self.setDefaultBehaviour(self.DefBehaviour())

"""
# Ahora un pequeño ejemplo.
if __name__ == "__main__":
	print "Start PingAgent..."
	#pingagent = PingAgentOneBehaviour("ping@tatooine.dsic.upv.es", "secret")
	pingagent = PingAgentOneBehaviour("ping@endor", "secret")
	#pingsender = PingSender("test2@localhost", "test2")
	pingagent.start()
	#pingsender.start()

	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		pingagent.stop()

