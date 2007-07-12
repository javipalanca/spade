#import time
import AID
import random
import string
#random.seed(time.time())


class ACLMessage:
	"""
	ACLMessage class stores a message using the ACL language
	"""
	ACCEPT_PROPOSAL  = 'accept-proposal'
	AGREE            = 'agree'
	CANCEL           = 'cancel'
	CFP              = 'cfp'
	CONFIRM          = 'confirm'
	DISCONFIRM       = 'disconfirm'
	FAILURE	         = 'failure'
	INFORM           = 'inform'
	NOT_UNDERSTOOD   = 'not-understood'
	PROPOSE          = 'propose'
	QUERY_IF         = 'query-if'
	QUERY_REF        = 'query-ref'
	REFUSE           = 'refuse'
	REJECT_PROPOSAL  = 'reject-proposal'
	REQUEST          = 'request'
	REQUEST_WHEN     = 'request-when'
	REQUEST_WHENEVER = 'request-whenever'
	SUBSCRIBE	 = 'subscribe'
	INFORM_IF        = 'inform-if'
	PROXY            = 'proxy'
	PROPAGATE        = 'propagate'

	cid_base = str("".join([string.ascii_letters[int(random.randint(0,len(string.ascii_letters)-1))] for a in range(4)]))
	cid_autocount = 0

	def __init__(self, performative=None):
		self._attrs = {}
		#possible FIPA communicative acts
		self.commacts = ['accept-proposal', 'agree', 'cancel', \
				'cfp', 'confirm', 'disconfirm', \
				'failure', 'inform', 'not-understood', \
				'propose', 'query-if', 'query-ref', \
				'refuse', 'reject-proposal', 'request', \
				'request-when', 'request-whenever', 'subscribe', \
				'inform-if', 'proxy', 'propagate']

		"""
		if performative and (performative.lower() in self.commacts):
			self.performative = performative.lower()
		else: self.performative = None
		"""
		if performative and (performative.lower() in self.commacts):
			self._attrs["performative"] = performative.lower()

		self.sender = None
		self.receivers = []
		self.content = None

		"""
		self.reply_to = []
		self.reply_with = None
		self.reply_by = None
		self.in_reply_to = None
		self.encoding = None
		self.language = None
		self.ontology = None
		self.protocol = None
		self.conversation_id = str(self.cid_base + str(self.cid_autocount))
		self.cid_autocount +=1
		"""

		self._attrs['id'] = str(ACLMessage.cid_base + str(ACLMessage.cid_autocount))
		ACLMessage.cid_autocount += 1

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
			#self.reply_to.append(re)
			if self._attrs.has_key('reply_to'):
				self._attrs['reply_to'].append(re)
			else:
				self._attrs['reply_to'] = [re]

	def removeReplyTo(self, re):
		"""
		removes a 'reply to' from the list (AID class)
		"""
		"""
		if re in self.reply_to:
			self.reply_to.remove(re)
		"""
		try:
			self._attrs["reply_to"].remove(re)
		except:
			return False

		return True

	def getReplyTo(self):
		"""
		returns a 'reply to' from the list (AID class)
		"""
		try:
			return str(self._attrs["reply_to"])
		except:
			return []

	def setPerformative(self, p):
		"""
		sets the message performative (string)
		must be in ACLMessage.commacts
		"""
		if p and (p.lower() in self.commacts):
			#self.performative = p.lower()
			self._attrs["performative"] = p.lower()

	def getPerformative(self):
		"""
		returns the message performative (string)
		"""
		try:
			return str(self._attrs["performative"])
		except:
			return None

	def setContent(self,c):
		"""
		sets the message content (string, bytestream, ...)
		"""
		self.content = str(c)

	def getContent(self):
		"""
		returns the message content
		"""
		return str(self.content)

	def setReplyWith(self,rw):
		self._attrs["reply_with"] = str(rw)
		#self.reply_with = rw

	def getReplyWith(self):
		try:
			return str(self._attrs["reply_with"])
		except:
			return None

	def setInReplyTo(self, reply):
		self._attrs["in_reply_to"] = str(reply)

	def getInReplyTo(self):
		try:
			return str(self._attrs["in_reply_to"])
		except:
			return None

	def setEncoding(self,e):
		self._attrs["encoding"] = str(e)

	def getEncoding(self):
		try:
			return str(self._attrs["encoding"])
		except:
			return None

	def setLanguage(self,e):
		self._attrs["language"] = str(e)

	def getLanguage(self):
		try:
			return str(self._attrs["language"])
		except:
			return None

	def setOntology(self,e):
		self._attrs["ontology"] = str(e)

	def getOntology(self):
		try:
			return str(self._attrs["ontology"])
		except:
			return None

	def setReplyBy(self,e):
		self._attrs["reply_by"] = str(e)

	def getReplyBy(self):
		try:
			return str(self._attrs["reply_by"])
		except:
			return None

	def setProtocol(self,e):
		self._attrs["protocol"] = str(e)

	def getProtocol(self):
		try:
			return str(self._attrs["protocol"])
		except:
			return None

	def setConversationId(self,e):
		self._attrs["id"] = str(e)

	def getConversationId(self):
		try:
			return str(self._attrs["id"])
		except:
			return None

	def createReply(self):
		"""
		Creates a reply for the message
		Duplicates all the message structures
		exchanges the 'from' AID with the 'to' AID
		"""

		m = ACLMessage()

		m.setPerformative(self.getPerformative())
		#m.setSender(None)
		#m.receivers = []
		#m.reply_to = []
		#m.setContent(None)
		#m.setReplyBy(None)
		#m.setEncoding(None)
		if self.getLanguage(): m.setLanguage(self.getLanguage())
		if self.getOntology(): m.setOntology(self.getOntology())
		if self.getProtocol(): m.setProtocol(self.getProtocol())
		if self.getConversationId(): m.setConversationId(self.getConversationId())

		for i in self.getReplyTo():
			m.addReceiver(i)

		if not self.getReplyTo():
			m.addReceiver(self.sender)

		if self.getReplyWith():
			m.setInReplyTo(self.getReplyWith())

		if self.getReplyWith() != None:
			m.setConversationId(str(self.getReplyWith()))

		return m


	def __str__(self):
		"""
		returns a printable version of the message in ACL string representation
		"""

		p = '('

		p=p+ str(self.getPerformative()) + '\n'
		if self.sender:
			p = p + ":sender " + str(self.sender) + "\n"

		if self.receivers:
			p = p + ":receiver\n (set\n"
			for i in self.receivers:
				p=p+ str(i) + '\n'

			p = p + ")\n"
		if self.content:
			p = p +  ':content "'+ self.content + '"\n'

		if self.getReplyWith():
			p = p + ":reply-with " + self.getReplyWith() + '\n'

		if self.getReplyBy():
			p = p+ ":reply-by " + self.getReplyBy() + '\n'

		if self.getInReplyTo():
			p = p+ ":in-reply-to " + self.getInReplyTo() + '\n'

		if self.getReplyTo():
			p = p+ ":reply-to \n" + '(set\n'
			for i in self.getReplyTo():
				p=p+ i + '\n'
			p = p + ")\n"

		if self.getLanguage():
			p = p+ ":language " + self.getLanguage() + '\n'

		if self.getEncoding():
			p = p+ ":encoding " + self.getEncoding() + '\n'

		if self.getOntology():
			p = p+ ":ontology " + self.getOntology() + '\n'

		if self.getProtocol():
			p = p+ ":protocol " + self.getProtocol() + '\n'

		if self.getConversationId():
			p = p+ ":conversation-id " + self.getConversationId() + '\n'


		p = p + ")\n"

		return p



