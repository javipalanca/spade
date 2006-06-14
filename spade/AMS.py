import Agent
import AID
import Behaviour
from SL0Parser import *


class AMS(Agent.PlatformAgent):
	"""
	Agent Management System
	"""

	class DefaultBehaviour(Behaviour.Behaviour):

		def __init__(self):
			Behaviour.Behaviour.__init__(self)
			self.sl0parser = SL0Parser()

			t = Behaviour.PresenceTemplate(type="subscribed")
			self.registerPresenceHandler(t, self.subscribedCB)
			t = Behaviour.PresenceTemplate(type="unsubscribed")
			tt = Behaviour.PresenceTemplate(type="unavailable")
			self.registerPresenceHandler(t, self.unsubscribedCB)
			self.registerPresenceHandler(tt, self.unsubscribedCB)

		def subscribedCB(self, frm, type, status, show):

			aad = AmsAgentDescription()
			aad.name = frm
			if status: aad.state = status
			if show: aad.ownership = show
			else: aad.ownership = frm

			if not self.myAgent.agentdb.has_key(frm.getName()):
				self.myAgent.agentdb[frm.getName()] = aad
			elif self.myAgent.agentdb[frm.getName()].getOwnership() == aad.getOwnership():
				self.myAgent.agentdb[frm.getName()] = aad
			else:
				presence = Presence(frm,type="unsubscribe")
				self.myAgent.jabber.send(presence)

		def unsubscribedCB(self, frm, type, status, show):

			aad = AmsAgentDescription()
			aad.name = frm
			if status: aad.state = status
			if show: aad.ownership = show
			else: aad.ownership = frm


			if self.myAgent.agentdb.has_key(frm.getName()):
				del self.myAgent.agentdb[frm.getName()]
			else:
				presence = Presence(frm,type="error", show="not-registered")
				self.myAgent.jabber.send(presence)

			#print "Agent " + frm.getName() + " deregistered from AMS"


		def _process(self):
			error = False
			msg = self._receive(True)
			#print ">>>>>>>>>>>>>>>>>>>AMS MSG RECEIVED"
			if msg != None:
				if msg.getPerformative().lower() == 'request':
					if msg.getOntology().lower() == "fipa-agent-management":
						if msg.getLanguage().lower() == "fipa-sl0":
							#print str(msg.getContent())
							content = self.sl0parser.parse(msg.getContent())
							ACLtemplate = Behaviour.ACLTemplate()
							ACLtemplate.setConversationId(msg.getConversationId())
							ACLtemplate.setSender(msg.getSender())
							template = (Behaviour.MessageTemplate(ACLtemplate))
							
							if "action" in content:
								if "register" in content.action \
								or "deregister" in content.action:
									#print ">>>>>>>>AMS REGISTER REQUEST"
									self.myAgent.addBehaviour(AMS.RegisterBehaviour(msg,content), template)
								elif "get-description" in content.action:
									self.myAgent.addBehaviour(AMS.PlatformBehaviour(msg,content), template)
								elif "search" in content.action:
									self.myAgent.addBehaviour(AMS.SearchBehaviour(msg,content), template)
								elif "modify" in content.action:
									self.myAgent.addBehaviour(AMS.ModifyBehaviour(msg,content), template)
							else:
								reply = msg.createReply()
								reply.setSender(self.myAgent.getAID())
								reply.setPerformative("refuse")
								reply.setContent("( "+msg.getContent() +"(unsuported-function "+ content.keys()[0] +"))")
								self.myAgent.send(reply)

								return -1


	
						else: error = "(unsupported-language "+msg.getLanguage()+")"
					else: error = "(unsupported-ontology "+msg.getOntology()+")"

				
				# By adding 'not-understood' to the following list of unsupported acts, we prevent an
				# infinite loop of counter-answers between the AMS and the registering agents
				elif msg.getPerformative().lower() not in ['failure','refuse','not-understood']:
						error = "(unsupported-act " + msg.getPerformative() + ")"
				if error:
					reply = msg.createReply()
					reply.setSender(self.myAgent.getAID())
					reply.setPerformative("not-understood")
					reply.setContent("( "+msg.getContent() + error+")")
					self.myAgent.send(reply)
					return -1
				

			return 1

	class RegisterBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content

		def _process(self):

			#The AMS agrees and then informs dummy of the successful execution of the action
			error = False

			try:
				if "register" in self.content.action:
					aad = AmsAgentDescription(self.content.action.register['ams-agent-description'])
				else:
					aad = AmsAgentDescription(self.content.action.deregister['ams-agent-description'])
			except KeyError: #Exception,err:
				error = "(missing-argument ams-agent-description)" 


			if error:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("refuse")
				reply.setContent("( "+self.msg.getContent() + error + ")")
				self.myAgent.send(reply)

				return -1

			else:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("agree")
				reply.setContent("(" + str(self.msg.getContent()) + " true)")
				self.myAgent.send(reply)




			if "register" in self.content.action:
				if not self.myAgent.agentdb.has_key(aad.getAID().getName()):
	
					try:
						self.myAgent.agentdb[aad.getAID().getName()] = aad
					except Exception, err:
						reply.setPerformative("failure")
						reply.setContent("("+self.msg.getContent() + "(internal-error))")
						self.myAgent.send(reply)
						return -1

					

					reply.setPerformative("inform")
					reply.setContent("(done "+self.msg.getContent() + ")")
					self.myAgent.send(reply)

					return 1

				else:
					reply.setPerformative("failure")
					reply.setContent("("+self.msg.getContent() + "(already-registered))")
					self.myAgent.send(reply)
					return -1

			elif "deregister" in self.content.action:

				if self.myAgent.agentdb.has_key(aad.getAID().getName()):
					try:
						del self.myAgent.agentdb[aad.getAID().getName()]
					except Exception, err:
						reply.setPerformative("failure")
						reply.setContent("("+self.msg.getContent() + '(internal-error "could not deregister agent"))')
						self.myAgent.send(reply)
						return -1

					

					reply.setPerformative("inform")
					reply.setContent("(done "+self.msg.getContent() + ")")
					self.myAgent.send(reply)

					return 1

				else:
					reply.setPerformative("failure")
					reply.setContent("("+self.msg.getContent() + "(not-registered))")
					self.myAgent.send(reply)
					return -1

	class PlatformBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content

		def _process(self):

			reply = self.msg.createReply()
			reply.setSender(self.myAgent.getAID())
			reply.setPerformative("agree")
			reply.setContent("(" + str(self.msg.getContent()) + " true)")
			self.myAgent.send(reply)

			content = "(ap-description :name xmpp://"+self.myAgent.getSpadePlatformJID()+ " :ap-services  (set "
			
			#TODO acceso al nombre de la plataforma y los servicios ofertados (df, ams, etc...)
			"""
			for s in "TODO_SERVICES":
				content += "(ap-service :name " + s.name
				content += " :type " + s.type
				content += " :addresses (sequence "
				for ad in s.addresses:
					content += ad + " "
				content += "))"
			"""

			content += "(ap-service :name xmpp://"+ str(self.myAgent.getAMS().getName())
			content += " :type fipa.agent-management.ams " #TODO
			content += " :addresses (sequence " + str(self.myAgent.getSpadePlatformJID()) + ")"
			content + " ) )"


			content += ")"
			

			reply.setPerformative("inform")
			reply.setContent(content)
			self.myAgent.send(reply)

			return 1

	class SearchBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content

		def _process(self):

			error = False

			reply = self.msg.createReply()
			reply.setSender(self.myAgent.getAID())
			reply.setPerformative("agree")
			reply.setContent("(" + str(self.msg.getContent()) + " true)")
			self.myAgent.send(reply)

			max = 1000
			if "search-constraints" in self.content.action.search:
				if "max-results" in self.content.action.search["search-constraints"]:
					try:
						max = int(self.content.action.search["search-constraints"]["max-results"])
					except Exception, err:
						error = '(internal-error "max-results is not an integer")'
			if error:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("failure")
				reply.setContent("( "+self.msg.getContent() + error+")")
				self.myAgent.send(reply)
				return -1


			result = []
			if "ams-agent-description" in self.content.action.search:
				aad = AmsAgentDescription(self.content.action.search['ams-agent-description'])
				#print str( self.myAgent.agentdb.values())
				for a in self.myAgent.agentdb.values():
					if max >= 0:
						#print "comparo " +str(a)+ " con " +str(aad)
						if a == aad:
							#print "TRUE!"
							result.append(a)
							max -= 1
					else: break

			else:
				result = self.myAgent.agentdb.values()
			
			content = "((result " #TODO: + self.msg.getContent()
			#print "He encontrado: " + str(len(result))
			if len(result)>0:
				content += " (set "
				for i in result:
					content += str(i) + " "
				content += ")"
			else:
				content+= 'None'
			content += "))"


			reply.setPerformative("inform")
			reply.setContent(content)
			self.myAgent.send(reply)

			return 1

	class ModifyBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content

		def _process(self):

			#The AMS agrees and then informs dummy of the successful execution of the action
			error = False
			aad = None
			try:
					aad = AmsAgentDescription(self.content.action.modify['ams-agent-description'])
			except Exception,err:
				error = "(missing-argument ams-agent-description)" 

			#print "aad: " + str(aad.getAID().getName())
			#print "aid: " + str(self.msg.getSender())

			if aad and (not aad.getAID() == self.msg.getSender()):
				error = "(unauthorised)"

			if error:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("refuse")
				reply.setContent("( "+self.msg.getContent() + error + ")")
				self.myAgent.send(reply)

				return -1

			else:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("agree")
				reply.setContent("(" + str(self.msg.getContent()) + " true)")
				self.myAgent.send(reply)




			if self.myAgent.agentdb.has_key(aad.getAID().getName()):
	
				try:
					self.myAgent.agentdb[aad.getAID().getName()] = aad
				except Exception, err:
					reply.setPerformative("failure")
					reply.setContent("("+self.msg.getContent() + "(internal-error))")
					self.myAgent.send(reply)
					return -1

					

				reply.setPerformative("inform")
				reply.setContent("(done "+self.msg.getContent() + ")")
				self.myAgent.send(reply)

				return 1

			else:
				reply.setPerformative("failure")
				reply.setContent("("+self.msg.getContent() + "(not-registered))")
				self.myAgent.send(reply)
				return -1


	def __init__(self,node,passw,server="localhost",port=5347):
		Agent.PlatformAgent.__init__(self,node,passw,server,port)


	def _setup(self):
		self.agentdb = dict()

		AAD = AmsAgentDescription()
		AAD.name = self.getAID()
		AAD.ownership = "SPADE"
		AAD.state = "active"

		self.agentdb[self.getAID().getName()] = AAD

		if self.getDF():
			AAD = AmsAgentDescription()
			AAD.name = self.getDF()
			AAD.ownership = "SPADE"
			AAD.state = "active"
			self.agentdb[self.getDF().getName()] = AAD

		db = self.DefaultBehaviour()
		#db.setPeriod(0.25)
		self.setDefaultBehaviour(db)


class AmsAgentDescription:
	"""
	Agent Descriptor for AMS registering
	"""

	def __init__(self, content = None):
		"""
		AAD constructor
		Optionally accepts a string containing a SL definition of the AAD
		"""
			
		self.name = None #AID.aid()
		self.ownership = None
		self.state = None

		if content != None:
			self.loadSL0(content)

	def getAID(self):
		"""
		returns the AID class
		"""
		return self.name

	def getOwnership(self):
		"""
		returns the ownership
		"""
		return self.ownership

	def getState(self):
		"""
		returns the state of the agent
		"""
		return self.state


	def __eq__(self,y):
		"""
		equal operator (==)
		returns False if the AADs are different
		else returns True
		"""

		if not self.name == y.getAID() \
		and self.name != None and y.getAID() != None:
			return False
		if self.ownership!= y.getOwnership() \
		and self.ownership != None and y.getOwnership() != None:
			return False
		if self.state != y.getState() \
		and self.state != None and y.getState() != None:
			return False

		return True

	def __ne__(self,y):
		"""
		non equal operator (!=)
		returns True if the AADs are different
		else returns False
		"""
		return not self == y


	def loadSL0(self,content):
		"""
		inits the AAD with a SL string representation
		"""
		if content != None:
			if "name" in content:
				self.name = AID.aid()
				self.name.loadSL0(content.name)

			if "ownership" in content:
				self.ownership = content.ownership[0]

			if "state" in content:
				self.state = content.state[0]

	def __str__(self):
		"""
		returns a printable version of the AAD in SL format)
		"""

		if ( (self.name == None) and (self.ownership == None) and (self.state == None) ):
			return "None"
		sb = "(ams-agent-description\n"
		if (self.name != None):
			sb = sb + ":name " + str(self.name) + "\n"

		if self.ownership != None:
			sb += ":ownership " + self.ownership +"\n"

		if self.state != None:
			sb += ":state " + str(self.state)

		sb = sb + ")\n"
		return sb

