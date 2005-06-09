import xmlstream
import jabber
import xmlcolor

class Payload:
	def __init__(self, original_msg = None, attributes = None):

		#possible FIPA communicative acts
		self.commacts = ['accept-proposal', 'agree', 'cancel', \
				'cfp', 'confirm', 'disconfirm', \
				'failure', 'inform', 'not-understood', \
				'propose', 'query-if', 'query-ref', \
				'refuse', 'reject-proposal', 'request', \
				'request-when', 'request-whenever', 'subscribe', \
				'inform-if', 'proxy', 'propagate']
		
		if original_msg != None:
			self.__message = original_msg
		else:
			self.__message = xmlstream.Node('fipa-message')


		if attributes != None:
			if attributes.has_key("performative"):
		      		if attributes.get("performative") in self.commacts:
					self.__message.putAttr('act',attributes.get("performative"))
			if attributes.has_key("sender"):
			   	nodo = xmlstream.Node('sender')
				agentnode = xmlstream.Node('agent-identifier')
				namenode = xmlstream.Node('name')
				namenode.insertData(attributes.get("sender"))
				agentnode.insertNode(namenode)
				nodo.insertNode(agentnode)
				self.__message.insertNode(nodo)
			if attributes.has_key("receiver"):
	   			nodo = xmlstream.Node('receiver')
				for i in attributes.get("receiver"):
					agentnode = xmlstream.Node('agent-identifier')
					namenode = xmlstream.Node('name')
					namenode.insertData(i.get("name"))
					agentnode.insertNode(namenode)
					nodo.insertNode(agentnode)
				self.__message.insertNode(nodo)

			if attributes.has_key("reply-to"):   	
			   	nodo = xmlstream.Node('reply-to')
				nodo.insertData(attributes.get("reply-to"))
				self.__message.insertNode(nodo)
			if attributes.has_key("content"):
			   	nodo = xmlstream.Node('content')
				nodo.insertData(attributes.get("content"))
				self.__message.insertNode(nodo)
			if attributes.has_key("language"):
			   	nodo = xmlstream.Node('language')
				nodo.insertData(attributes.get("language"))
				self.__message.insertNode(nodo)
			if attributes.has_key("encoding"):
			   	nodo = xmlstream.Node('encoding')
				nodo.insertData(attributes.get("encoding"))
				self.__message.insertNode(nodo)
			if attributes.has_key("ontology"):
			   	nodo = xmlstream.Node('ontology')
				nodo.insertData(attributes.get("ontology"))
				self.__message.insertNode(nodo)
			if attributes.has_key("protocol"):
			   	nodo = xmlstream.Node('protocol')
				nodo.insertData(attributes.get("protocol"))
				self.__message.insertNode(nodo)
			if attributes.has_key("conversation-id"):
			   	nodo = xmlstream.Node('conversation-id')
				nodo.insertData(attributes.get("conversation-id"))
				self.__message.insertNode(nodo)
			if attributes.has_key("reply-with"):
			   	nodo = xmlstream.Node('reply-with')
				nodo.insertData(attributes.get("reply-with"))
				self.__message.insertNode(nodo)
			if attributes.has_key("in-reply-to"):
			   	nodo = xmlstream.Node('in-reply-to')
				nodo.insertData(attributes.get("in-reply-to"))
				self.__message.insertNode(nodo)
			if attributes.has_key("reply-by"):
			   	nodo = xmlstream.Node('reply-by')
				nodo.insertData(attributes.get("reply-by"))
				self.__message.insertNode(nodo)
		return
		

	
	def getSender(self):
		for child in self.__message.getChildren():
			if child.getName() == 'sender':
				for child_ in child.getChildren():
					if child_.getName() == 'agent-identifier':
						for child__ in child_.getChildren():
							if child__.getName() == 'name':
								return child__.getData()
								
	def getReceiver(self):
		l = list()
		for child in self.__message.getChildren():
			if child.getName() == 'receiver':
				for child_ in child.getChildren():
					if child_.getName() == 'agent-identifier':
						for child__ in child_.getChildren():
							if child__.getName() == 'name':
								l.append(child__.getData())
		return l

	def getPerformative(self):
		return self.__message.getAttr('act')

	def getContent(self):
		for child in self.__message.getChildren():
			if child.getName() == 'content':
				return child.getData()
	   	
	     
	def setPerformative(self,performative):
		if performative in self.commacts:
			self.__message.putAttr('act',performative)
		else:
		   print "performative: it's not a valid FIPA communication act"
	def setSender(self,sender):
		nodo = xmlstream.Node('sender')
		agentnode = xmlstream.Node('agent-identifier')
		namenode = xmlstream.Node('name')
		namenode.insertData(sender)
		agentnode.insertNode(namenode)
		nodo.insertNode(agentnode)
		self.__message.insertNode(nodo)
	def setReceiver(self,receiver):	
		nodo = xmlstream.Node('receiver')
		for i in receiver:
			agentnode = xmlstream.Node('agent-identifier')
			namenode = xmlstream.Node('name')
			namenode.insertData(i)
			agentnode.insertNode(namenode)
			nodo.insertNode(agentnode)
		self.__message.insertNode(nodo)

	   	self.__receiver = receiver
	
	def setReplyTo(self,replyto):
	   	nodo = xmlstream.Node('reply-to')
		nodo.insertData(reply-to)
		self.__message.insertNode(nodo)
	def setContent(self,content):
	   	nodo = xmlstream.Node('content')
		nodo.insertData(content)
		self.__message.insertNode(nodo)
	def setLanguage(self,language):
	   	nodo = xmlstream.Node('language')
		nodo.insertData(language)
		self.__message.insertNode(nodo)
	def setEncoding(self,encoding):
	   	nodo = xmlstream.Node('encoding')
		nodo.insertData(encoding)
		self.__message.insertNode(nodo)
	def setOntology(self,ontology):
	   	nodo = xmlstream.Node('ontology')
		nodo.insertData(ontology)
		self.__message.insertNode(nodo)
	def setProtocol(self,protocol):
	   	nodo = xmlstream.Node('protocol')
		nodo.insertData(protocol)
		self.__message.insertNode(nodo)
	def setConversationId(self,conv_id):
	   	nodo = xmlstream.Node('conversation-id')
		nodo.insertData(conv_id)
		self.__message.insertNode(nodo)
	def setReplyWith(self,replywith):
	   	nodo = xmlstream.Node('reply-with')
		nodo.insertData(replywith)
		self.__message.insertNode(nodo)
	def setInReplyTo(self,inreplyto):
	   	nodo = xmlstream.Node('in-reply-to')
		nodo.insertData(inreplyto)
		self.__message.insertNode(nodo)
	def setReplyBy(self,replyby):
	   	nodo = xmlstream.Node('reply-by')
		nodo.insertData(replyby)
		self.__message.insertNode(nodo)

	def getXML(self):
	   	return self.__message

	def rawXML(self):
	   return self.__message._xmlnode2str()




class Envelope:
	def __init__(self, id = None, to = None, sender = None):
	   	self.__envelope = xmlstream.Node('envelope')
		params = xmlstream.Node('params')
		self.__envelope.insertNode(params)

		if id!=None and to!=None and sender!=None:
			self.Stamp(id,to,sender)


	def Stamp(self,id,to,sender):
		
		self.to = to
		
		param = xmlstream.Node('param')
	
		'''id'''
		param.putAttr('id',id)
		
		'''sender'''
		sendernode = xmlstream.Node('from')
		agentnode = xmlstream.Node('agent-identifier')
		namenode = xmlstream.Node('name')
		namenode.insertData(sender)
		agentnode.insertNode(namenode)
		'''
		if sender.has_key('addresses'):
			addsnode = xmlstream.Node('addresses')
			for addr in sender['addresses']:
				urlnode = xmlstream.Node(url)
				urlnode.insertData(addrr)
				addsnode.insertNode(urlnode)
			agentnode.insertNode(addsnode)
		'''
		sendernode.insertNode(agentnode)
		param.insertNode(sendernode)

		'''receiver'''
		recvnode = xmlstream.Node('to')
		for recv in to:
			agentnode = xmlstream.Node('agent-identifier')
			namenode = xmlstream.Node('name')
			namenode.insertData(recv)
			agentnode.insertNode(namenode)
			'''
			if recv.has_key('addresses'):
				addsnode = xmlstream.Node('addresses')
				for addr in recv['addresses']:
					urlnode = xmlstream.Node(url)
					urlnode.insertData(addrr)
					addsnode.insertNode(urlnode)
				agentnode.insertNode(addsnode)
			'''
			recvnode.insertNode(agentnode)
		param.insertNode(recvnode)

		'''insertamos params'''
		for subnode in self.__envelope.getChildren():
			if subnode.getName() == 'params':
				subnode.insertNode(param)

	
	def rawXML(self):
	   	return self.__envelope._xmlnode2str()
	def getXML(self):
	   	return self.__envelope

class ACLMessage:
   
	#~ def __init__(self,con,sender,to,performative,content=None):
	def __init__(self,con,payload,envelope):
		'''
	   	self.sender = sender
		self.to = to
		self.performative = performative
		self.content = content
	   	self.__con = con
		
		self.payload = Payload()
		self.payload.setPerformative(performative)
		self.payload.setSender(sender)
		self.payload.setReceiver(to)
		if content != None:
			self.payload.setContent(content)

		self.envelope = Envelope()
		self.envelope.Stamp('1',to,sender)
		'''
		self.__con = con
		self.payload = payload
		self.envelope = envelope
		self.to = self.envelope.to

	def rawXML(self):

	   	rawxml = ""
		rawxml = rawxml + str(self.envelope.rawXML())
		rawxml = rawxml + str(self.payload.rawXML())
		return rawxml

	def getMsg(self):
		return self.payload.getXML()
	def getEnvelope(self):
		return self.envelope.getXML()
	     
	def send(self):
		for to in self.to:
			msg = jabber.Message(to,self.rawXML())
			self.__con.send(msg)
