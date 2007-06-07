#! python
from spade import *
import os, sys
import time

host = "tatooine.dsic.upv.es"

class OracleEmissorAgent (Agent.Agent):
  class SubscriberBehaviour(Behaviour.Behaviour):
    """Behaviour that handles everything"""
    def __init__(self):
	Behaviour.Behaviour.__init__(self)
	self.initialized = False

    def _process(self):
	# OneShot does not work
	if self.initialized:
		time.sleep(1)
		return

	# FD - subscribe protocol
	self.myAgent.msg = ACLMessage.ACLMessage()
        self.myAgent.msg.setSender( self.myAgent.getAID() )
	self.myAgent.msg.addReceiver(  AID.aid(name="oracle@"+host, addresses=["xmpp://oracle@"+host]) )
	self.myAgent.msg.setPerformative("subscribe")
	self.myAgent.send(self.myAgent.msg)
	print "Subscription sent"
	
	self.myAgent.reply = self._receive(True)
	perf = self.myAgent.reply.getPerformative()
	if perf == "refuse":
		print "Subscription refused"
	elif perf == "agree":
		print "Subscription accepted"

	self.myAgent.subscribed = True
        
	self.myAgent.oracle = self.myAgent.OracleBehaviour()
	self.myAgent.addBehaviour( self.myAgent.oracle )
	self.myAgent.setDefaultBehaviour( self.myAgent.oracle )

	self.initialized = True

	time.sleep(0.25)


  class OracleBehaviour(Behaviour.Behaviour):
    """Behaviour that asks advice"""
    def __init__(self):
	Behaviour.Behaviour.__init__(self)
	self.x = 5
	self.y = 5

    def _process(self):
	print "OracleBehaviour started"
	# FD - query protocol
	self.myAgent.msg.setPerformative("query-ref")
	self.myAgent.msg.setContent(str(self.x) + " " + str(self.y))
	self.myAgent.send(self.myAgent.msg)
	self.myAgent.reply = self._receive(True)
	
	if self.myAgent.reply.getPerformative() == "agree":
		print "The oracle wants to speak!!"
		self.myAgent.reply = self._receive(True)
		print "The oracle has spoken!! : ", self.myAgent.reply.getContent()

	self.x = self.x + 5
	self.y = self.y + 5

	time.sleep(3)
			
  def __init__ (self, agentjid, passwd):
  	Agent.Agent.__init__(self, agentjid, passwd)

  def _setup (self):
	self.subscribers = []

	#ACLtemplate = ACLMessage.ACLMessage()
        #ACLtemplate.setPerformative('subscribe')
        #template = Behaviour.MessageTemplate(ACLtemplate)
	self.subscribed = False
	self.subscriber = self.SubscriberBehaviour()

        #ACLtemplate.setPerformative('query-ref')
        #template = Behaviour.MessageTemplate(ACLtemplate)

	self.setDefaultBehaviour(self.subscriber)


if __name__ == "__main__":
	oagent = OracleEmissorAgent("emissor@"+host, "secret")
	oagent.start()
	try:
		while True:
			time.sleep(0.5)
	except:
		oagent.stop()
