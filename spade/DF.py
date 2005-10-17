import Agent
import AID
import Behaviour
import BasicFipaDateTime
from SL0Parser import *


class DF(Agent.PlatformAgent):

	class DefaultBehaviour(Behaviour.Behaviour):

		def __init__(self):
			Behaviour.Behaviour.__init__(self)
			self.sl0parser = SL0Parser()

		def process(self):
			error = False
			msg = self.blockingReceive()
			if msg != None:
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

		def process(self):

			#The DF agrees and then informs dummy of the successful execution of the action
			error = False
			#print "Register"

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
					reply.setContent("(done "+msg.getContent() + ")")
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

		def process(self):

			error = False

			reply = self.msg.createReply()
			reply.setSender(self.myAgent.getAID())
			reply.setPerformative("agree")
			reply.setContent("(" + str(self.msg.getContent()) + " true)")
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
				reply.setContent("( "+msg.getContent() + error+")")
				self.myAgent.send(reply)
				return -1


			result = []

			if "df-agent-description" in self.content.action.search:
				dad = DfAgentDescription(self.content.action.search["df-agent-description"])
			for i in self.myAgent.servicedb.values():
				if max >= 0:
					if i == dad:
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

		def process(self):

			#The AMS agrees and then informs dummy of the successful execution of the action
			error = False
			dad = None
			#print self.content.action.modify[0][1]
			try:
					dad = DF.DfAgentDescription(self.content.action.modify[0][1])
					print "fuego el 1"
			except Exception,err:
				error = "(missing-argument ams-agent-description)" 
				print "fuego el 1.5"

			if dad and (dad.getAID().getName() != self.myAgent.getAID().getName()):
				error = "(unauthorised)"
				print "fuego el 1.6"

			if error:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("refuse")
				reply.setContent("( "+self.msg.getContent() + error + ")")
				self.myAgent.send(reply)
				print "fuego el 1.7"

				return -1

			else:
	
				print "fuego el 2"
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("agree")
				reply.setContent("(" + str(self.msg.getContent()) + " true)")
				self.myAgent.send(reply)
				print "fuego el 2"




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
		Agent.PlatformAgent.__init__(self,node,passw,server,port)


	def setup(self):
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

	def getServices(self):
		return self.services

	def getProtocols(self):
		return self.protocols

	def getOntologies(self):
		return self.ontologies

	def getLanguages(self):
		return self.languages

	def getLeaseTime(self):
		return self.lease_time

	def getScope(self):
		return self.scope

	def __eq__(self,y):

		if self.name != y.getAID() \
		and self.name != None and y.getAID() != None:
			return False
		if self.protocols.sort() != y.getProtocols().sort() \
		and len(self.protocols)>0 and len(y.getProtocols())>0:
			return False
		if self.ontologies.sort() != y.getOntologies().sort() \
		and len(self.ontologies)>0 and len(y.getOntologies())>0:
			return False
		if self.languages.sort() != y.getLanguages().sort() \
		and len(self.languages)>0 and len(y.getLanguages())>0:
			return False
		if self.lease_time != None and y.getLeaseTime() != None \
		and str(self.lease_time) != str(y.getLeaseTime()):
			return False
		if self.scope.sort() != y.getScope().sort() \
		and len(self.scope)>0 and len(y.getScope())>0:
			return False

		return True

	def __ne__(self,y):
		return not self == y


	def loadSL0(self,content):
		print content.keys()
		if content != None:
			if "name" in content:
				self.name.loadSL0(content.name)

			print "OK 1"

			if "services" in content:
				#TODO: el parser solo detecta 1 service-description!!!
				self.services = [] #ServiceDescription()
				#self.services.loadSL0(content.services.set['service-description'])
				for i in content.services.set:
					sd = ServiceDescription(i[1])
					self.services.append(sd)
			print "OK 2"

			if "protocols" in content:
				self.protocols = content.protocols.set.asList()

			print "OK 3"
			if "ontologies" in content:
				self.ontologies = content.ontologies.set.asList()
			print "OK 4"

			if "languages" in content:
				self.languages = content.languages.set.asList()
			print "OK 5"

			if "lease-time" in content:
				self.lease_time = BasicFipaDateTime.BasicFipaDateTime()
				#self.lease_time.fromString(content["lease-time"])
				self.lease_time = content["lease-time"][0]
			print "OK 6"

			if "scope" in content:
				self.scope = content.scope.set.asList()
			print "OK 7"

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

	def getType(self):
		return self.type

	def getProtocols(self):
		return self.protocols

	def getOntologies(self):
		return self.ontologies

	def getLanguages(self):
		return self.languages

	def getOwnership(self):
		return self.ownership

	def getProperties(self):
		return self.properties


	def __eq__(self,y):

		if self.name != y.getName() \
		and self.name != None and y.getName() != None:
			return False
		if self.type != y.getType() \
		and self.type != None and y.getType() != None:
			return False
		if self.protocols.sort() != y.getProtocols().sort() \
		and len(self.protocols)>0 and len(y.getProtocols())>0:
			return False
		if self.ontologies.sort() != y.getOntologies().sort() \
		and len(self.ontologies)>0 and len(y.getOntologies())>0:
			return False
		if self.languages.sort() != y.getLanguages().sort() \
		and len(self.languages)>0 and len(y.getLanguages())>0:
			return False
		if self.ownership != y.getOwnership() \
		and self.ownership != None and y.getOwnership() != None:
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
				self.type = content.type

			if "protocols" in content:
				self.protocols = content.protocols.set.asList()

			if "ontologies" in content:
				self.ontologies = content.ontologies.set.asList()

			if "languages" in content:
				self.languages = content.languages.set.asList()

			if "ownership" in content:
				self.ownership = content.ownership

			if "properties" in content:
				for p in content.properties.set:
					self.properties.append({'name':p.name,'value':p.value})

	def __str__(self):

		sb = ""
		if self.name != None:
			sb += ":name " + str(self.name) + "\n"
		if self.type:
			sb += ":type" + str(self.type) + "\n"

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
			sb += ":properties\n(set\n"
			for i in self.properties:
				sb += "(property :name " + i['name'] + " :value " + i['value'] +")\n"
			sb += ")\n"


		if sb != "":
			sb = "(service-description\n" + sb + ")\n"
		return sb


