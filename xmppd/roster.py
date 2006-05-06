from xmpp import *
from spade import *
from spade.ACLMessage import *
import types

class rosterPlugIn(PlugIn):
        #NS='jabber:x:fipa'
        NS=''
	def plugin(self, server):
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=NS_ROSTER)
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=u'jabber:iq:roster')

		# Initialize the roster management system
		self.rosters = {}

		self.DEBUG("Roster manager loaded", "warn")

	"""
	def createRoster(self, jid):
		'''Create a roster for a given jid'''
		if type(jid) == types.InstanceType:
			# Transform jid to string representation (faster?)
			jid = jid.getStripped()	
		if jid not in self.rosters.keys():
			self.rosters[jid] = []
	"""

	
	def getRoster(self, jid):
		if type(jid) == types.InstanceType:
			# Transform jid to string representation (faster?)
			jid = jid.getStripped()
		if not jid in self.rosters.keys()
			# Particular rosters are lists
			self.rosters[jid] = {}
		return self.rosters[jid]


	"""
	MyRoster:
	{ friend@localhost: { name:'Friend', subscription: 'none' }
	  another@localhost: { }
	  . . . 
	}
	"""

        def rosterHandler(self, session, stanza):
                print "####################################"
		print "ROSTER HANDLER CALLED"
                print "####################################"
		print "STANZA: ", str(stanza)
                print "####################################"
		# Client is asking for something
		if stanza.getAttr('type') == 'get':
                	print "####################################"
			print "IT IS A GET"
                	print "####################################"
			query = stanza.getTag('query', namespace=NS_ROSTER)
			if query != None:
				# The whole roster was requested
                		print "####################################"
				print "THE ROSTER WAS REQUESTED"
		                print "####################################"
				iq = Iq('result', NS_ROSTER)
				query=iq.getTag('query')
				# Fill the roster
				ros = self.getRoster(stanza.getAttr('from'))
				for key, value in ros:
					attrs={'jid':key}
					if 'name' in value.keys():
						attrs['name'] = value['name']
					if 'subscription' in value.keys():
						attrs['subscription'] = value['name']						
					item=query.setTag('item',attrs)
				session.enqueue(iq)	
                		print "####################################"
				print "THE ROSTER WAS SENT:"
				print str(iq)
		                print "####################################"
		

		raise NodeProcessed

