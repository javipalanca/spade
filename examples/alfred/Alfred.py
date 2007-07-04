from spade import *
from spade.SL0Parser import *

import ConfigParser
import xmpp

from GooglePlugin import *


class AlfredAgent(Agent.Agent):

	def __init__(self,jid,passw):
		Agent.Agent.__init__(self,jid,passw)

	def setup(self):

		configfile = ConfigParser.ConfigParser()

		cffile = open('profile.ini','r')
		configfile.readfp(cffile)
		cffile.close()

		agentjid = configfile.get("agent","jid")
		password = configfile.get("agent","password")

		owner = configfile.get("user","jid")
		self.owner = xmpp.protocol.JID(owner)

		db = self.DefaultBehaviour()
		self.setDefaultBehaviour(db)

	class DefaultBehaviour(Behaviour.Behaviour):

		def process(self):
			msg = self.blockingReceive()
			#print "ESTO QUE ES?:\n"
			#print str(msg)


	def other_messageCB(self, conn, mess):
		if (mess.getError() == None):
			msg = mess.getBody()
			if msg[:7]=="#google":
				self.google_search(msg[8:])
			else:
				m = "Lo siento Señor. No le entiendo."
				self.send_owner_msg(m)

	def send_owner_msg(self, payload):
		jabber_msg = xmpp.protocol.Message(self.owner,payload, xmlns="")
		jabber_msg["from"]=self.getAID().getName()
	        self.jabber.send(jabber_msg)


	def google_search(self, string, max = None):
		ACLtemplate = Behaviour.ACLTemplate()
		msg = ACLMessage.ACLMessage()
		#ACLtemplate.setFrom(AID.aid("google@localhost", ["xmpp://spade.localhost"]))
		ACLtemplate.setConversationId(msg.getConversationId())
		template = (Behaviour.MessageTemplate(ACLtemplate))
		self.addBehaviour(GoogleBehaviour(msg, string,max),template)

		

if __name__ == "__main__":
	alfred = AlfredAgent("alfred@localhost","secret")
	alfred.start_and_wait()

