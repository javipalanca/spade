from xmppd import filter
from xmpp import *
from spade import *
from spade.ACLMessage import *

import os

class ACC(filter.Filter):

	def __init__(self,router):

		filter.Filter.__init__(self,router)

		if os.name == "posix":
			configfile = "/etc/spade/spade.xml"
		else:
			configfile = "etc/spade.xml"

		parser = SpadeConfigParser.ConfigParser()
		config = parser.parse(configfile)

		self.mtps = {}
		for name,mtp in config.acc.items():
			#self.mtps[mtp.protocol] = mtp.instance(name)
			self.mtps[mtp['protocol']] = mtp['instance']

	def test(self,stanza):

            	children = stanza.getChildren()
		#self._router.DEBUG("ACC PLUGIN: analyzing message structure", "info")
            	for child in children:
                	if (child.getNamespace() == "jabber:x:fipa") or (child.getNamespace() == u"jabber:x:fipa"):
				self.envelope = child.getData()
				return True

		return False

		"""
		simple_to = str(stanza['to'])
		if not('@' in simple_to):  # Component name
			# SPADE CASE: message directed to the ACC component
			if simple_to[0:4] == "acc.":
				#self._router.DEBUG("Message for the ACC",'ok')
				return True
		#self._router.DEBUG("Message NOT for the ACC",'error')
		return False
		"""


	def filter(self,session,stanza):

		xmpp_processed = False

		if (stanza.getError() == None):
			envxml = self.envelope
			#payload = stanza.getBody()
			payload = stanza.getTag("body")
			xc = XMLCodec.XMLCodec()
			self.envelope = xc.parse(str(envxml))

			for aid in self.envelope.getTo():
				for addr in aid.getAddresses():
					protocol = addr.split("://")[0]

					if protocol == "xmpp":
						#FIXME: only supports 1 xmpp sender
						receivers = self.getRealTo(stanza)
						to = str(receivers[0])  # FIX THIS TO ALLOW MULTIPLE RECEIVERS
						# We do NOT raise the NodeProcessed exception,
						# the message follows its normal course from here
						stanza.setTo(to)
						xmpp_processed = True


					elif protocol in self.mtps.keys():
						print ">>>ACC: Message for external MTP: " + str(protocol)
						mtp = self.mtps[protocol]
						print ">>>ACC: MTP found: " + str(mtp)
						#envelope is in Envelope format
						#payload is in string format (with escaped characters)
						mtp.send(self.envelope,payload)
						print ">>>ACC: External MTP message sent"

					else:
						print ">>>ACC: Could not find suitable MTP for protocol: " + str(protocol)


		if xmpp_processed: return stanza
		else: return None



	def getRealTo(self, mess):
		#return the real JID of the receiver of a "jabber:x:fipa" message
		
		receiver_names = []
		for aid in self.envelope.getTo():
			receiver_names.append(str(aid.getName()))

		return receiver_names

