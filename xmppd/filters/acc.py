from xmppd import filter
from xmpp import *
from spade import *
from spade.ACLMessage import *

class ACC(filter.Filter):

	def test(self,stanza):
		simple_to = str(stanza['to'])
		if not('@' in simple_to):  # Component name
			# SPADE CASE: message directed to the ACC component
			if simple_to[0:4] == "acc.":
				self._router.DEBUG("Message for the ACC",'ok')
				return True
		self._router.DEBUG("Message NOT for the ACC",'error')
		return False


	def filter(self,session,stanza):

		receivers = self.getRealTo(stanza)
		to = str(receivers[0])  # FIX THIS TO ALLOW MULTIPLE RECEIVERS
		# We do NOT raise the NodeProcessed exception, the message follows its normal course from here
		#self._router.DEBUG("ya tengo receiver: "+ to,"info")
		#stanza['to'] = to
		stanza.setTo(to)
		self._router.DEBUG("retorno stanza","info")
		return stanza

	def getRealTo(self, mess):
		"""
		return the real JID of the receiver of a "jabber:x:fipa" message
		"""
		#self._router.DEBUG("ACC PLUGIN: received " + str(dir(mess)), "info")
		#self.DEBUG("ACC PLUGIN: received " + str(mess), "info")
		envxml=None
		receiver_names = []
		'''
		payload = None
		try:
	            	payload=mess.getBody()
		except:
			self.DEBUG("ACC PLUGIN: getBody FAILED. Trying alternate method")
		try:
			if payload == None:
				payload=mess.getTagData['body']
		except:
			self.DEBUG("ACC PLUGIN: getTagData FAILED.")
		'''
			
		#self._router.DEBUG("ACC PLUGIN: mess Body got", "info")
            	children = mess.getChildren()
		#self._router.DEBUG("ACC PLUGIN: analyzing message structure", "info")
            	for child in children:
                	if (child.getNamespace() == "jabber:x:fipa") or (child.getNamespace() == u"jabber:x:fipa"):
                    		envxml = child.getData()
            	if (envxml != None):
			#self._router.DEBUG("ACC PLUGIN: found envelope", "info")
                	xc = XMLCodec.XMLCodec()
                	envelope = xc.parse(str(envxml))
			#self._router.DEBUG("ACC PLUGIN: envelope decoded: " + str(envelope), "info")
			#self._router.DEBUG("ACC PLUGIN: envelope decoded: " + str(dir(envelope)), "info")
			for aid in envelope.getTo():
				receiver_names.append(str(aid.getName()))

                	'''
			if   str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.string.std":
                        	ac = ACLParser.ACLParser()
                	elif str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.xml.std":
                        	ac = ACLParser.ACLxmlParser()
                	else:
                        	self.DEBUG("ACC PLUGIN: NO PARSER!", "info")
			'''

		#ACLmsg = ac.parse(str(payload))	
		#self.DEBUG("ACC PLUGIN: getRealTo = " + str(ACLmsg.getReceivers()), "info")
		#for item in ACLmsg.getReceivers():
		#	receiver_names.append(str(item.getName()))
		return receiver_names

