"""
JADE - Java Agent DEvelopment Framework is a framework to develop 
multi-agent systems in compliance with the FIPA specifications.
Copyright (C) 2000 CSELT S.p.A. 

GNU Lesser General Public License

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation, 
version 2.1 of the License. 

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA  02111-1307, USA.
"""

"""
   The class ACLMessage implements an ACL message compliant to the <b>FIPA 2000</b> "FIPA ACL Message Structure Specification" (fipa000061) specifications.
   All parameters are couples <em>keyword: value</em>.
   All keywords are <code>private final String</code>.
   All values can be set by using the methods <em>set</em> and can be read by using
   the methods <em>get</em>. 
   <p> <b>Warning: </b> since JADE 3.1  an exception might be thrown 
   during the serialization of the ACLMessage parameters (with 
   exception of the content of the ACLMessage) because of a limitation
   to 65535 in the total number of bytes needed to represent all the 
   characters of a String (see also java.io.DataOutput#writeUTF(String)).
   <p> The methods <code> setByteSequenceContent() </code> and 
   <code> getByteSequenceContent() </code> allow to send arbitrary
   sequence of bytes
   over the content of an ACLMessage.
   <p> The couple of methods 
   <code> setContentObject() </code> and 
   <code> getContentObject() </code> allow to send
   serialized Java objects over the content of an ACLMessage.
   These method are not strictly 
   FIPA compliant so their usage is not encouraged.
   @author Fabio Bellifemine - CSELT
   @version $Date: 2004/10/21 13:01:37 $ $Revision: 2.39 $
   @see <a href=http://www.fipa.org/specs/fipa00061/XC00061D.html>FIPA Spec</a>
"""
#import time
import AID
import random
import string
#random.seed(time.time())


class ACLMessage:


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
		if p in self.commacts:
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



