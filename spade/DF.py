from Agent import PlatformAgent
import AID
import Behaviour
import BasicFipaDateTime
from SL0Parser import *


class DF(PlatformAgent):
	"""
	Directory Facilitator Agent
	"""

	class DefaultBehaviour(Behaviour.Behaviour):

		def __init__(self):
			Behaviour.Behaviour.__init__(self)
			self.sl0parser = SL0Parser()

		def _process(self):
			error = False
			msg = self._receive(True)
			if msg != None:
				#print "DF RECEIVED A MESSAGE", str(msg)
				if msg.getPerformative().lower() == 'request':
					if msg.getOntology().lower() == "fipa-agent-management":
						if msg.getLanguage().lower() == "fipa-sl0":
							content = self.sl0parser.parse(msg.getContent())
							ACLtemplate = Behaviour.ACLTemplate()
							ACLtemplate.setConversationId(msg.getConversationId())
							#ACLtemplate.setSender(msg.getSender())
							template = (Behaviour.MessageTemplate(ACLtemplate))

							if "action" in content:
								if "register" in content.action or "deregister" in content.action:
									self.myAgent.addBehaviour(DF.RegisterBehaviour(msg,content), template)
								elif "search" in content.action:
									self.myAgent.addBehaviour(DF.SearchBehaviour(msg,content), template)
								elif "modify" in content.action:
									self.myAgent.addBehaviour(DF.ModifyBehaviour(msg,content), template)
							else:
								reply = msg.createReply()
								reply.setSender(self.myAgent.getAID())
								reply.setPerformative("refuse")
								reply.setContent("( "+msg.getContent() +"(unsuported-function "+ content.keys()[0] +"))")
								self.myAgent.send(reply)

								return -1



						else: error = "(unsupported-language "+msg.getLanguage()+")"
					else: error = "(unsupported-ontology "+msg.getOntology()+")"


				elif msg.getPerformative().lower() not in ['failure','refuse']:
						error = "(unsupported-act " + msg.getPerformative() + ")"
				if error:
					reply = msg.createReply()
					reply.setSender(self.myAgent.getAID())
					reply.setPerformative("not-understood")
					reply.setContent("( "+msg.getContent() + error+")")
					self.myAgent.send(reply)
					return -1

				#TODO: delete old services


	class RegisterBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content
			#print "Constructor"

		def _process(self):

			#The DF agrees and then informs dummy of the successful execution of the action
			error = False
			print "###DFRegister"

			try:
				if "register" in self.content.action:
					dad = DfAgentDescription(self.content.action.register['df-agent-description'])
				else:
					dad = DfAgentDescription(self.content.action.deregister['df-agent-description'])
			except KeyError: #Exception,err:
				error = "(missing-argument df-agent-description)"


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
				if not self.myAgent.servicedb.has_key(dad.getAID().getName()):

					try:
						self.myAgent.servicedb[dad.getAID().getName()] = dad
						#print "###########"
						#print "DF REGISTERED SERVICE"
						#print dad
						#print "###########"
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

				if self.myAgent.servicedb.has_key(dad.getAID().getName()):
					try:
						del self.myAgent.servicedb[dad.getAID().getName()]
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
			#reply.setConversationId(self.msg.getConversationId())
			self.myAgent.send(reply)

			max = 50
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

			if "df-agent-description" in self.content.action.search:
				dad = DfAgentDescription(self.content.action.search["df-agent-description"])
			for i in self.myAgent.servicedb.values():
				if max >= 0:
					if dad.match(i):
						result.append(i)
						max -= 1
				else: break



			content = "((result " #+ self.msg.getContent()
			if len(result)>0:
				content += " (set "
				for i in result:
					content += str(i) + " "
				content += ")"
			else:
				content+= "None"
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
			dad = None
			#print self.content.action.modify[0][1]
			try:
					dad = DF.DfAgentDescription(self.content.action.modify[0][1])
			except Exception,err:
				error = "(missing-argument ams-agent-description)"

			if dad and (dad.getAID().getName() != self.myAgent.getAID().getName()):
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




			if self.myAgent.servicedb.has_key(dad.getAID().getName()):

				try:
					self.myAgent.servicedb[dad.getAID().getName()] = dad
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
		PlatformAgent.__init__(self,node,passw,server,port)


	def _setup(self):
		self.servicedb = dict()

		self.setDefaultBehaviour(self.DefaultBehaviour())


class DfAgentDescription:

	def __init__(self, content = None):

		self.name = AID.aid()
		self.services = []
		self.protocols = []
		self.ontologies = []
		self.languages = []
		self.lease_time = None
		self.scope = []

		if content != None:
			self.loadSL0(content)

	def getAID(self):
		return self.name

	def setAID(self, a):
		self.name = a

	def getServices(self):
		return self.services

	def addService(self, s):
		self.services.append(s)

	def getProtocols(self):
		return self.protocols

	def addProtocol(self, p):
		self.protocols.append(p)

	def getOntologies(self):
		return self.ontologies

	def addOntologies(self, o):
		self.ontologies.append(o)

	def getLanguages(self):
		return self.languages

	def addLanguage(self, l):
		self.languages.append(l)

	def getLeaseTime(self):
		return self.lease_time

	def setLeaseTime(self, lt):
		self.lease_time = lt

	def getScope(self):
		return self.scope

	def addScope(self, s):
		self.scope = s

	#def __eq__(self,y):
	def match(self,y):

		if self.name:
			if self.name != y.getAID():
				return False
		if self.protocols:
			if self.protocols.sort() != y.getProtocols().sort():
				return False
		if self.ontologies:
			if self.ontologies.sort() != y.getOntologies().sort():
				return False
		if self.languages:
			if self.languages.sort() != y.getLanguages().sort():
				return False
		if self.lease_time:
			if self.lease_time != None and y.getLeaseTime() != None:
				return False
		if self.scope:
			if self.scope.sort() != y.getScope().sort():
				return False

		if len(self.services)>0 and len(y.getServices())>0:
			for i in self.services:
				for j in y.getServices():
					#if i == j:
					if i.match(j):
						return True
			return False
		else:
			return True

	def __ne__(self,y):
		return not self == y

	def loadSL0(self,content):
		if content != None:
			if "name" in content:
				self.name.loadSL0(content.name)


			if "services" in content:
				#TODO: el parser solo detecta 1 service-description!!!
				self.services = [] #ServiceDescription()
				#self.services.loadSL0(content.services.set['service-description'])
				for i in content.services.set:
					sd = ServiceDescription(i[1])
					self.services.append(sd)

			if "protocols" in content:
				self.protocols = content.protocols.set.asList()

			if "ontologies" in content:
				self.ontologies = content.ontologies.set.asList()

			if "languages" in content:
				self.languages = content.languages.set.asList()

			if "lease-time" in content:
				self.lease_time = BasicFipaDateTime.BasicFipaDateTime()
				#self.lease_time.fromString(content["lease-time"])
				self.lease_time = content["lease-time"][0]

			if "scope" in content:
				self.scope = content.scope.set.asList()

	def __str__(self):

		sb = ''
		if self.name != None:
			sb = sb + ":name " + str(self.name) + "\n"

		if len(self.services) > 0:
			sb = sb + ":services \n(set\n"
			for i in self.services:
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"

		if len(self.protocols) > 0:
			sb = sb + ":protocols \n(set\n"
			for i in self.protocols:
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"

		if len(self.ontologies) > 0:
			sb = sb + ":ontologies \n(set\n"
			for i in self.ontologies:
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"

		if len(self.languages) > 0:
			sb = sb + ":languages \n(set\n"
			for i in self.languages:
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"

		if self.lease_time != None:
			sb = sb + ":lease-time " + str(self.lease_time)

		if len(self.scope) > 0:
			sb = sb + ":scope \n(set\n"
			for i in self.scope:
				sb = sb + str(i) + '\n'
			sb = sb + ")\n"

		sb = "(df-agent-description \n" + sb + ")\n"
		return sb

class ServiceDescription:

	def __init__(self, content = None):

		self.name = None
		self.type = None
		self.protocols = []
		self.ontologies = []
		self.languages = []
		self.ownership = None
		self.properties = []

		if content != None:
			self.loadSL0(content)

	def getName(self):
		return self.name

	def setName(self, name):
		self.name = name

	def getType(self):
		return self.type

	def setType(self, t):
		self.type = t

	def getProtocols(self):
		return self.protocols

	def addProtocol(self, p):
		self.protocols.append(p)

	def getOntologies(self):
		return self.ontologies

	def addOntologies(self, o):
		self.ontologies.append(o)

	def getLanguages(self):
		return self.languages

	def addLanguage(self, l):
		self.languages.append(l)

	def getOwnership(self):
		return self.ownership

	def setOwnership(self, o):
		self.ownership = o

	def getProperties(self):
		return self.properties

	def getProperty(self, prop):
	    for p in self.properties:
	        if p["name"] == prop:
	            return p["value"]
	    return ""

	def addProperty(self, p):
		self.properties.append(p)

	#def __eq__(self,y):
	def match(self,y):

		if self.name:
			if self.name != y.getName():
				return False
		if self.type:
			if self.type != y.getType():
				return False
		if self.protocols:
			if self.protocols.sort() != y.getProtocols().sort():
				return False
		if self.ontologies:
			if self.ontologies.sort() != y.getOntologies().sort():
				return False
		if self.languages:
			if self.languages.sort() != y.getLanguages().sort():
				return False
		if self.ownership:
			if self.ownership != y.getOwnership():
				return False
		#properties
		return True

	def __ne__(self,y):
		return not self == y

	def loadSL0(self,content):
		if content != None:
			if "name" in content:
				self.name = content.name[0]

			if "type" in content:
				self.type = content.type[0]

			if "protocols" in content:
				self.protocols = content.protocols.set.asList()

			if "ontologies" in content:
				self.ontologies = content.ontologies.set.asList()

			if "languages" in content:
				self.languages = content.languages.set.asList()

			if "ownership" in content:
				self.ownership = content.ownership

			if "properties" in content:
				#print "##########"
				#print "PROPERTIES"
				#print str(content.properties.set)
				#print "##########"
				for p in content.properties.set.asDict().values():
					#print p
					self.properties.append({'name':str(p['name']).strip("[']"),'value':str(p['value']).strip("[']")})

	def __str__(self):

		sb = ""
		if self.name != None:
			sb += ":name " + str(self.name) + "\n"
		if self.type:
			sb += ":type " + str(self.type) + "\n"

		if len(self.protocols) > 0:
			sb += ":protocols \n(set\n"
			for i in self.protocols:
				sb += str(i) + " "
			sb = sb + ")\n"

		if len(self.ontologies) > 0:
			sb = sb + ":ontologies \n(set\n"
			for i in self.ontologies:
				sb += str(i) + " "
			sb = sb + ")\n"

		if len(self.languages) > 0:
			sb = sb + ":languages \n(set\n"
			for i in self.languages:
				sb += str(i) + " "
			sb += ")"

		if self.ownership:
			sb += ":ownership" + str(self.ownership) + "\n"

		if len(self.properties) > 0:
			sb += ":properties \n (set\n"
			for i in self.properties:
				sb += " (property :name " + i['name'] + " :value " + i['value'] +")\n"
			sb += ")\n"


		if sb != "":
			sb = "(service-description\n" + sb + ")\n"
		return sb


