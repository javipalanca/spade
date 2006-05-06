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
		#dummy = {'friend@localhost': {'name':'Friend', 'subscription':'none'} }
		dummy = dict()
		dummy['friend@localhost'] = dict()
		dummy['friend@localhost']['name'] = 'Friend'
		dummy['friend@localhost']['subscription'] = 'none'
		self.rosters['receptor0@localhost'] = dummy
		
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
		print "### getRoster: ", jid
		if type(jid) == types.InstanceType:
			# Transform jid to string representation (faster?)
			print "### Got instance:", str(jid)
			jid = jid.getStripped()
			print "### Turned in:", jid
		elif type(jid) == types.StringType:
			# Remove resource
			jid = jid.split('/')[0]
			print "### Resource Removed: ", jid

		if jid not in self.rosters.keys():
			# Particular rosters are dicts
			# Create one
			print "### Create roster for: ", jid
			self.rosters[jid] = {}
		print "### getRoster returning: ", str(self.rosters[jid])
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
				print "FILL THE ROSTER"
		                print "####################################"
				frm = stanza.getAttr('from')
				print frm
				ros = self.getRoster(frm)
				for key, value in ros:
					print key, value
					attrs={'jid':key}
					if 'name' in value.keys():
						attrs['name'] = value['name']
					if 'subscription' in value.keys():
						attrs['subscription'] = value['subscription']
					if 'ask' in value.keys():
						attrs['ask'] = value['ask']
					item=query.setTag('item',attrs)
				session.enqueue(iq)	
                		print "####################################"
				print "THE ROSTER WAS SENT:"
				print str(iq)
		                print "####################################"
		

		raise NodeProcessed

