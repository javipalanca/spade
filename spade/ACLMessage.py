#import time
import AID
import random
import string
#random.seed(time.time())


class ACLMessage:
	"""
	ACLMessage class stores a message using the ACL language
	"""

	cid_base = "".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(5)])
	cid_autocount = 0
	def __init__(self):
		#possible FIPA communicative acts
		self.commacts = ['accept-proposal', 'agree', 'cancel', \
				'cfp', 'confirm', 'disconfirm', \
				'failure', 'inform', 'not-understood', \
				'propose', 'query-if', 'query-ref', \
				'refuse', 'reject-proposal', 'request', \
				'request-when', 'request-whenever', 'subscribe', \
				'inform-if', 'proxy', 'propagate']

		self.performative = 'not-understood'
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
		self.conversation_id = ACLMessage.cid_base + str(ACLMessage.cid_autocount)
		ACLMessage.cid_autocount +=1

		#self.userDefProps = None

	def reset(self):
		"""
		resets the object
		its structures are set to its initial value
		"""
		self.__init__()

	def setSender(self, sender):
		"""
		set the sender (AID class)
		"""
		self.sender = sender

	def getSender(self):
		"""
		returns the sender (AID class)
		"""
		return self.sender

	def addReceiver(self, recv):
		"""
		adds a receiver to the list (AID class)
		"""
		self.receivers.append(recv)

	def removeReceiver(self, recv):
		"""
		removes a receiver from the list (AID class)
		"""
		if recv in self.receivers:
			self.receivers.remove(recv)

	def getReceivers(self):
		"""
		returns the list of reveivers
		"""
		return self.receivers


	def addReplyTo(self, re):
		"""
		adds a 'reply to' to the list (AID class)
		"""
		if isinstance(re,AID.aid):
			self.reply_to.append(re)

	def removeReplyTo(self, re):
		"""
		removes a 'reply to' from the list (AID class)
		"""
		if re in self.reply_to:
			self.reply_to.remove(re)

	def getReplyTo(self):
		"""
		returns a 'reply to' from the list (AID class)
		"""
		return self.reply_to

	def setPerformative(self, p):
		"""
		sets the message performative (string)
		must be in ACLMessage.commacts
		"""
		if p in self.commacts:
			self.performative = p

	def getPerformative(self):
		"""
		returns the message performative (string)
		"""
		return self.performative

	def setContent(self,c):
		"""
		sets the message content (string, bytestream, ...)
		"""
		self.content = c

	def getContent(self):
		"""
		returns the message content
		"""
		return self.content

	def setReplyWith(self,rw):
		self.reply_with = rw

	def getReplyWith(self):
		return self.reply_with
	
	def setInReplyTo(self, reply):
		self.in_reply_to = reply
	
	def getInReplyTo(self):
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

	def createReply(self):
		"""
		Creates a reply for the message
		Duplicates all the message structures
		exchanges the 'from' AID with the 'to' AID
		"""

		m = ACLMessage()

		m.setPerformative(self.performative)
		m.setSender(None)
		m.receivers = []
		m.reply_to = []
		m.setContent(None)
		m.setReplyBy(None)
		m.setEncoding(None)
		m.setLanguage(self.language)
		m.setOntology(self.ontology)
		m.setProtocol(self.protocol)
		m.setConversationId(self.conversation_id)

		for i in self.reply_to:
			m.addReceiver(i)

		if self.reply_to == []:
			m.addReceiver(self.sender)
		
		m.setInReplyTo(self.getReplyWith())

		if self.reply_with != None:
			m.setConversationId(self.reply_with)


		return m;


	def __str__(self):
		"""
		returns a printable version of the message in SL0 language
		"""

		p = '('

		p=p+ str(self.performative) + '\n'
		if self.sender:
			p = p + ":sender " + str(self.sender) + "\n"

		if self.receivers:
			p = p + ":receiver\n (set\n"
			for i in self.receivers:
				p=p+ str(i) + '\n'

			p = p + ")\n"
		if self.content:
			p = p +  ':content "'+ str(self.content) + '"\n'

		if self.reply_with:
			p = p + ":reply-with " + str(self.reply_with) + '\n'

		if self.reply_by:
			p = p+ ":reply-by " + str(self.reply_by) + '\n'

		if self.in_reply_to:
			p = p+ ":in-reply-to " + str(self.in_reply_to) + '\n'

		if self.reply_to:
			p = p+ ":reply-to \n" + '(set\n'
			for i in self.reply_to:
				p=p+ str(i) + '\n'
			p = p + ")\n"

		if self.language:
			p = p+ ":language " + str(self.language) + '\n'

		if self.encoding:
			p = p+ ":encoding " + str(self.encoding) + '\n'

		if self.ontology:
			p = p+ ":ontology " + str(self.ontology) + '\n'

		if self.protocol:
			p = p+ ":protocol " + str(self.protocol) + '\n'

		if self.conversation_id:
			p = p+ ":conversation-id " + str(self.conversation_id) + '\n'


		p = p + ")\n"

		return p



