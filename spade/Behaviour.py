import time
import ACLMessage
import MessageReceiver
import threading


class ACLTemplate:
	"""
	Template for message matching
	"""
	def __init__(self):
		self.performative = None
		self.sender = None
		self.receivers = []
		self.reply_to = []
		self.content = None
		self.reply_with = None
		self.reply_by = None
		self.in_reply_to = None
		self.encoding = None
		self.language = None
		self.ontology = None
		self.protocol = None
		self.conversation_id = None
		#self.userDefProps = None

	def reset(self):
		self.__init__()

	def setSender(self, sender):
		self.sender = sender

	def getSender(self):
		return self.sender

	def addReceiver(self, recv):
		self.receivers.append(recv)

	def removeReceiver(self, recv):
		if recv in self.receivers:
			self.receivers.remove(recv)

	def getReceivers(self):
		return self.receivers


	def addReplyTo(self, re):
		if isinstance(re,AID.aid):
			self.reply_to.append(re)

	def removeReplyTo(self, re):
		if re in self.reply_to:
			self.reply_to.remove(re)

	def getReplyTo(self):
		return self.reply_to

	def setPerformative(self, p):
		self.performative = p

	def getPerformative(self):
		return self.performative

	def setContent(self,c):
		self.content = c

	def getContent(self):
		return self.content

	def setReplyWith(self,rw):
		self.reply_with = rw

	def getReplyWith(self):
		return self.reply_with
	
	def setInReplyTo(self, reply):
		self.in_reply_to = reply
	
	def getInReplyTo(self,reply):
		return self.in_reply_to

	def setEncoding(self,e):
		self.encoding = e

	def getEncoding(self):
		return self.encoding

	def setLanguage(self,e):
		self.language = e

	def getLanguage(self):
		return self.language
	def setOntology(self,e):
		self.ontology = e

	def getOntology(self):
		return self.ontology
	def setReplyBy(self,e):
		self.reply_by = e

	def getReplyBy(self):
		return self.reply_by

	def setProtocol(self,e):
		self.protocol = e

	def getProtocol(self):
		return self.protocol
	def setConversationId(self,e):
		self.conversation_id = e

	def getConversationId(self):
		return self.conversation_id





class BehaviourTemplate:
	"""
	Template operators
	"""
	def __init__(self):
		pass
	def match(self, message):
		return False
		
	def __and__(self, other):
		"""Implementation of & operator"""
		return ANDTemplate(self, other)
	def __rand__(self, other):
		"""Implementation of &= operator"""
		return (self & other)
	
	def __or__(self, other):
		"""Implementation of | operator"""
		return ORTemplate(self, other)
	def __ror__(self, other):
		"""Implementation of |= operator"""
		return (self | other)
	
	def __xor__(self, other):
		"""Implementation of ^ operator"""
		return XORTemplate(self, other)
	def __rxor__(self, other):
		"""Implementation of ^= operator"""
		return (self ^ other)
	def __invert__(self):
		"""Implementation of ~ operator"""
		return NOTTemplate(self)
		
		

class NOTTemplate(BehaviourTemplate):
	def __init__(self, expr):
		self.expr = expr
	def match(self, message):
		return (not(self.expr.match(message)))

class ORTemplate(BehaviourTemplate):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	def match(self, message):
		return (self.expr1.match(message) | self.expr2.match(message))

class ANDTemplate(BehaviourTemplate):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	def match(self, message):
		return (self.expr1.match(message) & self.expr2.match(message))

class XORTemplate(BehaviourTemplate):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	def match(self, message):
		return (self.expr1.match(message) ^ self.expr2.match(message))



class MessageTemplate(BehaviourTemplate):
	def __init__(self, ACLTemplate):
		self.template =ACLTemplate
		
	def match(self, message):
		if (self.template.performative != None): 
			if (self.template.performative != message.performative): return False
		if (self.template.sender != None): 
			if (self.template.sender != message.sender): return False
		if (self.template.receivers != []): 
			if (self.template.receivers != message.receivers): return False
		if (self.template.reply_to != []): 
			if (self.template.reply_to != message.reply_to): return False
		if (self.template.content != None): 
			if (self.template.content != message.content): return False
		if (self.template.reply_with != None): 
			if (self.template.reply_with != message.reply_with): return False
		if (self.template.reply_by != None): 
			if (self.template.reply_by != message.reply_by): return False
		if (self.template.in_reply_to != None): 
			if (self.template.in_reply_to != message.in_reply_to): return False
		if (self.template.encoding != None): 
			if (self.template.encoding != message.encoding): return False
		if (self.template.language != None): 
			if (self.template.language != message.language): return False
		if (self.template.ontology != None): 
			if (self.template.ontology != message.ontology): return False
		if (self.template.protocol != None): 
			if (self.template.protocol != message.protocol): return False
		if (self.template.conversation_id != None): 
			if (self.template.conversation_id != message.conversation_id): return False
		return True
	
	
	






class Behaviour(MessageReceiver.MessageReceiver):
	def __init__(self):
		MessageReceiver.MessageReceiver.__init__(self)
		self.myParent = None
		self.myAgent = None
		self._forceKill = threading.Event()
	
	def setParent(self, parent):
		self.myParent = parent
	def getParent(self):
		return self.myParent
	def setAgent(self, agent):
		"""
		sets the agent which controls the behavior
		"""
		self.myAgent = agent

		self.setName(str(self.myAgent.getName()) + " Behaviour")

	def getAgent(self):
		"""
		returns the agent which controls the behavior
		"""
		return self.myAgent
	def root(self):
		if (self.myParent != None):
			return self.myParent.root()
		else:
			return self
	
	def done(self):
		"""
		returns True if the behavior has finished
		else returns False
		"""
		return False
	
	def _process(self):
		"""
		main loop
		must be overridden
		"""
		raise NotImplementedError
	
	def kill(self):
		"""
		stops the behavior
		"""
		try:
			self._forceKill.set()
		except:
			#Behavior is already dead
			pass
		
	def onStart(self):
		"""
		this method runs when the behavior starts
		"""
		pass
	def onEnd(self):
		"""
		this method runs when the behavior stops
		"""
		pass
	def exitCode(self):
		"""
		returns the default exit code for the behavior
		"""
		return 0
		
	def run(self):
		self.onStart()
		while (not(( self.done() | self._forceKill.isSet() ))):
			self._process()
			#time.sleep(0)
		self.onEnd()
		self.myAgent.removeBehaviour(self)
		
class OneShotBehaviour(Behaviour):
	"""
	this behavior is only executed one time
	"""
	def __init__(self):
		Behaviour.__init__(self)
		self._firsttime = True
	def done(self):
		if (self._firsttime == True):
			self._firsttime = False
			return False
		return True
			



class PeriodicBehaviour(Behaviour):
	"""
	this behavior runs periodically with a period
	"""
	def __init__(self, period, timestart = None):
		Behaviour.__init__(self)
		self._period = period
		if (timestart == None):
			self._nextActivation = time.time()
		else:
			self._nextActivation = timestart
		
	def getPeriod(self):
		return self._period
	def setPeriod(self, period):
		self._period = period
		
	def _process(self):
		if (time.time() >= self._nextActivation):
			self._onTick()
			while (self._nextActivation <= time.time()):
				self._nextActivation += self._period
		else:
			t = self._nextActivation - time.time()
			if t > 0:
				time.sleep(t)
			
	def _onTick(self):
		"""
		this method is executed every period
		must be overridden
		"""
		raise NotImplementedError


class TimeOutBehaviour(PeriodicBehaviour):
	"""
	this behavior is executed only one time after a timeout
	"""
	def __init__(self, timeout):		
		PeriodicBehaviour.__init__(self, timeout, time.time()+timeout)
		self._stop = False
		
	def getTimeOut(self):
		return self.getPeriod()
	def stop(self):
		"""
		cancels the programmed execution
		"""
		self._stop = True		
	def done(self):
		return self._stop
	
	def _onTick(self):
		if (self._stop == False):
			self.timeOut()
		self.stop()
		
	def timeOut(self):
		"""
		this method is executed after the timeout
		must be overridden
		"""
		raise NotImplementedError





class FSMBehaviour(Behaviour):
	"""
	this behavior is executed according to a Finite State Machine
	"""
	def __init__(self):
		Behaviour.__init__(self)
		self._firstStateName = None
		self._lastStatesNames = []
		self._states = dict()
		self._transitions = dict()
		self._actualState = None
		self._lastexitcode = 0

	def setAgent(self, agent):
		"""
		sets the parent agent
		"""
		self.setAgent(agent)
		for b in self._states:
			self._states[b].setAgent(agent)
	
	def registerState(self, behaviour, name):
		"""
		registers a state with a behavior
		"""
		behaviour.setPatent(self)
		self._states[name]=behaviour
		self._transitions[name]=dict()
		
	def registerFirstState(self, behaviour, name):
		"""
		sets the first state of the fsm
		"""
		self.registerState(behaviour, name)
		self._firstStateName = name
		
	def registerLastState(self, behaviour, name):
		"""
		sets the final state of the fsm
		"""
		self.registerState(behaviour, name)
		self._lastStatesNames += [name]
	
	def registerTransition(self, fromname, toname, event):
		"""
		registers a transition between two states
		"""
		self._transitions[fromname][event] = toname
	
	def getState(self, name):
		return self._states[name]

	#def onStart(self):
	#	self._actualState = self._firstStateName
	#	self._actualState.start()
	#	for b in self._states:
	#		self._states[b].start()
	#def onEnd(self):
	#	for b in self._states:
	#		self._states[b].kill()
	
	def exitCode(self):
		return self._lastexitcode
	
	def done(self):
		try:
			self._lastStatesNames.index(self._actualState)
			return True
		except ValueError:
			return False
		
	def _transitionTo(self,newState):
		try:
			b = self._states[self._actualState]
			b.onEnd()
		except KeyError:
			pass
		self._actualState == newState
		try:
			b = self._states[self._actualState]
			b.onStart()
		except KeyError:
			pass
	
	def _process(self):
		if (self._actualState == None):
			self._transitionTo(self._firstStateName)
		msg = self._receive(True)
		b = self._states[self._actualState]
		b.postMessage(msg)
		b._process()
		if (b.done() == True):
			self._lastexitcode = b.exitCode()
			self._transitionTo(self._transitions[b][self._lastexitcode])





if __name__ == "__main__":
	class TestBehaviour(PeriodicBehaviour):
		def __init__(self, time):
			PeriodicBehaviour.__init__(self, time)
		def _onTick(self):
			print "Tick: " + str(time.time())
	
	a = TestBehaviour(5)
	a.start()
