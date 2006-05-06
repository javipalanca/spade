from xmpp import *
from spade import *
from spade.ACLMessage import *


class rosterPlugIn(PlugIn):
        #NS='jabber:x:fipa'
        NS=NS_ROSTER
	def plugin(self, server):
		server.Dispatcher.RegisterNamespaceHandler(NS_ROSTER,self.rosterHandler)

        def rosterHandler(self, session, stanza):
                print "####################################"
		print "ROSTER HANDLER CALLED"
                print "####################################"

