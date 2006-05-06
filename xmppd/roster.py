from xmpp import *
from spade import *
from spade.ACLMessage import *


class rosterPlugIn(PlugIn):
        #NS='jabber:x:fipa'
        NS=''
	def plugin(self, server):
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=NS_ROSTER)
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=u'jabber:iq:roster')
		self.DEBUG("Roster manager loaded", "warn")

        def rosterHandler(self, session, stanza):
                print "####################################"
		print "ROSTER HANDLER CALLED"
                print "####################################"
		# Client is asking for something
		if stanza[type] == 'get':
			query = stanza.getTag('query', namespace=NS_ROSTER)
			if query <> None:
				# The whole roster was requested
                		print "####################################"
				print "THE ROSTER WAS REQUESTED"
		                print "####################################"
		

		raise NodeProcessed

