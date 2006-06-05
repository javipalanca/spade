from xmpp import *
from spade import *
from spade.ACLMessage import *
import types


class rosterPlugIn(PlugIn):
        #NS='jabber:x:fipa'
        NS=''
	def plugin(self, server):
		self.server = server
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=NS_ROSTER)
		server.Dispatcher.RegisterHandler('iq', self.rosterHandler, ns=u'jabber:iq:roster')

		# Initialize the roster management system
		self.rosters = {}
		#dummy = {'friend@localhost': {'name':'Friend', 'subscription':'none'} }
		dummy = dict()
		dummy['friend@localhost'] = dict()
		dummy['friend@localhost']['name'] = 'Friend'
		dummy['friend@localhost']['subscription'] = 'none'
		dummy['amiga@localhost'] = dict()
		dummy['amiga@localhost']['name'] = 'Amiga One'
		dummy['amiga@localhost']['subscription'] = 'none'
		dummy['amiga@localhost']['ask'] = 'none'
		self.rosters['receptor0@localhost'] = dummy
		self.rosters['test@localhost'] = dummy
		
		self.DEBUG("Roster manager loaded", "warn")

	
	def getRoster(self, jid):
		#print "### getRoster: ", jid
		if type(jid) == types.InstanceType:
			# Transform jid to string representation (faster?)
			#print "### Got instance:", str(jid)
			jid = jid.getStripped()
			#print "### Turned in:", jid
		elif type(jid) == types.StringType:
			# Remove resource
			jid = jid.split('/')[0]
			#print "### Resource Removed: ", jid

		'''if jid not in self.rosters.keys():
			# Particular rosters are dicts
			# Create one
			print "### Create roster for: ", jid
			self.rosters[jid] = dict()'''
			
		#print "### getRoster returning: ", str(self.rosters[jid])
		#return self.rosters[jid]
		ros = self.server.DB.getRoster(jid)
		#print "### Got roster from DB: ", str(ros)
		return ros


	"""
	MyRoster:
	{ friend@localhost: { name:'Friend', subscription: 'none' }
	  another@localhost: { }
	  . . . 
	}
	"""

	def sendRoster(self, frm, session, type='result'):
		ros = self.getRoster(frm)
		iq = Iq(type, NS_ROSTER, to=frm)
		query=iq.getTag('query')
		#print "### Got roster: ", str(ros)
		for key, value in ros.items():
			#print key, value
			attrs={'jid':key}
			if 'name' in value.keys():
				attrs['name'] = value['name']
			if 'subscription' in value.keys():
				attrs['subscription'] = value['subscription']
			if 'ask' in value.keys():
				attrs['ask'] = value['ask']
			item=query.setTag('item',attrs)
		session.enqueue(iq)	

	def initialPresence(self, frm):
		ros = self.getRoster(frm)
		probe = Presence(typ='probe', frm=frm)
		pres = Presence(frm=frm)
		for contact in ros.keys():
			try:
				# Send a presence probe to all contacts with the 'to' or 'both' subscription
				if ros[contact]['subscription']	== 'to' or ros[contact]['subscription'] == 'both':
					s = self.server.getsession(contact)
					s.enqueue(probe)
                		# Send a presence to all contacts with the 'from' or 'both' subscription
				if ros[contact]['subscription']	== 'from' or ros[contact]['subscription'] == 'both':
					s = self.server.getsession(contact)
					s.enqueue(pres)
			except:
				pass
				

	def sendUnavailable(self, frm, to, status):
		# Generate a Presence node
		if status:
			p = Presence(to, 'unavailable', frm = frm, status = status)
		else:
			p = Presence(to, 'unavailable', frm = frm)
		# Find the receiver's session and send the presence information through it
		s = self.server.getsession(to)
		if s:
			s.enqueue(p)

	def broadcastUnavailable(self, barejid, status=None):
		'''
		Broadcasts an 'unavailable' presence to all contacts
		'''
		ros = self.getRoster(barejid)
		if ros:
			for contact in ros.keys():
				# If a contact is subscribed to our presence
				try:
					if ros[contact]['subscription'] == 'from' or ros[contact]['subscription'] == 'both':
						self.sendUnavailable(barejid, contact, status)
				except:
					# Contact does not have subscription
					print "### Contact does not have subscription item"
	def cancelSubscription(self, frm, to, session):
		#print "### cancelSubscription called: ", str(frm), str(to)
		# Cancel the subscription of the client 'to' 
		ros = self.getRoster(frm)
		to=str(to.split('/')[0])  # In case there was a resource
		try:
			contact = ros[to]
		except:
			# There was no contact, so there was no subscription. We're done
			return
		if contact:
			# Check what type of subscription there was and change it
			if contact['subscription'] == 'from':
				contact['subscription'] = 'none'
			elif contact['subscription'] == 'both':
				contact['subscription'] = 'to'
			self.sendRoster(frm, session, type='set')


	def makeUnsubscription(self, frm, to, session):
		#print "### makeUnsubscription called: ", str(frm), str(to)
		# Unsubscribe the contact 'to' from the roster of client 'frm'
		ros = self.getRoster(frm)
		to=str(to.split('/')[0])  # In case there was a resource
		try:
			contact = ros[to]
		except:
			# There was no contact, so there was no subscription. We're done
			return
		if contact:
			# Check what type of subscription there was and change it
			if contact['subscription'] == 'to':
				contact['subscription'] = 'none'
			elif contact['subscription'] == 'both':
				contact['subscription'] = 'from'
			self.sendRoster(frm, session, type='set')

	def makeSubscription(self, frm, to, session, subs='none'):
		#print "### makeSubscription called: ", str(frm), str(to)
		# Subscribe the contact 'to' to the roster of client 'frm'
		ros = self.getRoster(frm)
		to=str(to.split('/')[0])  # In case there was a resource
		try:
			contact = ros[to]
		except:
			contact = False
		if contact:
			# Check wether there is already a subscription
			if contact['subscription'] == 'from' and subs == 'to':
				contact['subscription'] = 'both'
			elif contact['subscription'] == 'to' and subs == 'from':
				contact['subscription'] = 'both'
			elif contact['subscription'] == 'none' and subs == 'from':
				contact['subscription'] = 'from'
			elif contact['subscription'] == 'none' and subs == 'to':
				contact['subscription'] = 'to'
			# For the rest of cases, contact['subscription'] equals 'both'
			# so, it should not be touched

			# Specific actions for each type of subscription
			if subs == 'none':
				# Add the subscription state
				contact['ask'] = 'subscribe'
				self.sendRoster(frm, session, type='set')
			elif subs == 'to':
				try:
					del contact['ask']
				except:
					pass
				self.sendRoster(frm, session, type='set')
		else:
			# There was no such contact in the roster. Let's create its entry
			values = dict()
			values['subscription'] = subs
			if subs == 'none':
				values['ask'] = 'subscribe'
				self.sendRoster(frm, session, type='set')
			elif subs == 'to':
				# No 'ask' entry
				self.sendRoster(frm, session, type='set')
			ros[to] = values
			# Make the changes persistent in the DB
			#self.server.DB.savedb()



        def rosterHandler(self, session, stanza):
		# Client is asking for the roster
		if stanza.getAttr('type') == 'get':
			query = stanza.getTag('query', namespace=NS_ROSTER)
			if query != None:
				# The whole roster was requested
                		#print "####################################"
				#print "THE ROSTER WAS REQUESTED"
		                #print "####################################"
				#iq = Iq('result', NS_ROSTER)
				#query=iq.getTag('query')
				# Fill the roster
				#print "FILL THE ROSTER"
		                #print "####################################"
				frm = stanza.getAttr('from')
				self.sendRoster(frm, session)
				#print frm
				#ros = self.getRoster(frm)
				#print "### Got roster: ", str(ros)
				#for key, value in ros.items():
				#	print key, value
				#	attrs={'jid':key}
				#	if 'name' in value.keys():
				#		attrs['name'] = value['name']
				#	if 'subscription' in value.keys():
				#		attrs['subscription'] = value['subscription']
				#	if 'ask' in value.keys():
				#		attrs['ask'] = value['ask']
				#	item=query.setTag('item',attrs)
				#session.enqueue(iq)	
				#print " ### THE ROSTER WAS SENT TO: " + str(frm)
				#print str(iq)
		# Client is modifying the roster
		elif stanza.getAttr('type') == 'set':
			query = stanza.getTag('query', namespace=NS_ROSTER)
			if query != None:
				frm = stanza.getAttr('from')
				ros = self.getRoster(frm)
				for item in stanza.getTag('query').getTags('item'):
					jid=str(item.getAttr('jid'))
					jid=str(jid.split('/')[0])
					name=item.getAttr('name')
					subscription=item.getAttr('subscription')
					ask=item.getAttr('ask')
					if subscription == 'remove':
						try:
							del ros[jid]
						except:	
							print "Could not delete item from roster"
					else:
						values = dict()
						if name:
							values['name'] = str(name)
						if subscription:
							values['subscription'] = str(subscription)
						if ask:
							values['ask'] = str(ask)
						ros[jid] = values
				# Send the roster back
				self.sendRoster(frm, session, type='set')
				# TODO: Send the roster to every resource
				# Send a confirmation 'result'-type iq
				iq = Iq('result', NS_ROSTER, to=frm)
				session.enqueue(iq)
				# Make the changes persistent in the DB
				self.server.DB.savedb()

		raise NodeProcessed

