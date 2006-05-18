from xmpp import *
import types

class Participant:
	"""
	A client that participates in a MUC room
	"""
	def __init__(self, fulljid, barejid=None, nick=None, role=None, affiliation=None):
		# Get data from constructor
		self.fulljid = fulljid
		# If there was no barejid, build it
		if not barejid:
			 self.barejid = str(fulljid).split('/')[0]
		else:
			self.barejid = barejid
		# If there was no nick, take the barejid instead
		if not nick:
			self.nick = self.barejid
		else:
			self.nick = nick
		# If there was no role, take the 'none' role
		if not role:
			self.role = 'none'
		else:
			self.role = role
		# Same as role
		if not affiliation:
			self.affiliation = 'none'
		else:
			self.affiliation = affiliation

	def __str__(self):
		return '<' + str(self.fulljid) + ' barejid="' + self.barejid + '" nick="' + self.nick + '" role="' + self.role + '" affiliation="' + self.affiliation + '">'

	def getFullJID(self):
		"""
		Get the participant's full JID
		"""
		return self.fulljid

	def getBareJID(self):
		"""
		Get the participant's bare JID
		"""
		return self.barejid

	def getNick(self):
		"""
		Get the participant's nickname
		"""
		return self.nick

	def getRole(self):
		"""
		Get the participant's role
		"""
		return self.role

	def getAffiliation(self):
		"""
		Get the participant's affiliation
		"""
		return self.affiliation

	def setFullJID(self, fulljid):
		"""
		Set the participant's full JID
		"""
		self.fulljid = fulljid

	def setBareJID(self, barejid):
		"""
		Set the participant's bare JID
		"""
		self.barejid = barejid

	def setNick(self, nick):
		"""
		Set the participant's nickname
		"""
		self.nick = nick

	def setRole(self, role):
		"""
		Set the participant's role
		"""
		self.role = role

	def setAffiliation(self, affiliation):
		"""
		Set the participant's affiliation
		"""
		self.affiliation = affiliation


class Room:
	"""
	A MUC room
	"""
	def __init__(self, name, subject=None, template=None, creator=None, whitelist=[], blacklist=[], password=None):
		# Initialize default room specific values
		self.hidden = False
		self.open = True
		self.moderated = False
		self.semi_anonymous = False
		self.unsecured = True
		self.password = password
		self.persistent = False

		# Initialize default role privileges
		# Every privilege is expressed in a hierarchical form.
		# If a given privilege is granted to a client with the role of 'visitor',
		# all superior roles, will have that privilege too (i.e. 'participant' and 'moderator')
		self.role_privileges = {}
		self.role_privileges['change_nick'] = 'visitor'
		self.role_privileges['send_private'] = 'visitor'
		self.role_privileges['invite'] = 'visitor'
		self.role_privileges['send'] = 'participant'
		self.role_privileges['subject'] = 'participant'

		# Get data from constructor
		self.name = name
		# If there was no subject, take the first part of the jid instead
		if not subject:
			self.subject = name
		else:
			self.subject = subject
		# If there was a template, change values by default
		if template:
			print "TODO: Implement room templates"
		# Initialize participants dict. It will be indexed by the participants full JIDs
		self.participants = {}
		# If there was a creator, add it to the participants dict
		if creator:
			self.creator = creator
			creator.setRole('moderator')
			self.participants[creator.getFullJID()] = creator

		# Initialize white and blacklists
		self.whitelist = whitelist
		self.blacklist = blacklist

	def __str__(self):
		s = str(self.name) + ": " + self.subject
		s = s + " Hidden = " + str(self.hidden) + " Open = " + str(self.open) + " Moderated = " + str(self.moderated) + " Semi-Anonymous = " + str(self.semi_anonymous) + " Unsecured = " + str(self.unsecured) + " Persistent = " + str(self.persistent)
		s = s + " Role Privileges = " + str(self.role_privileges)
		s = s + " Participants = " + str(self.participants.keys())
		s = s + " Creator = " + str(self.creator.getFullJID())
		s = s + " Whitelist = " + str(self.whitelist)
		s = s + " Blacklist = " + str(self.blacklist)
		return s

	def addParticipant(self, fulljid=None, barejid=None, nick=None, role=None, affiliation=None, participant=None, password=None):
		"""
		Add a participant to a room
		"""
		# fulljid must be a string
		if isinstance(fulljid, JID):
			fulljid = str(fulljid)

		# If a participant object has been passed here, copy all its attributes into the new participant
		if participant:
			# Copy another object
			p = Participant(participant.getFullJID(), participant.getBareJID(), participant.getNick(), participant.getRole(), participant.getAffiliation())
		elif fulljid not in self.participants.keys():
			# Instantiate a new participant
			p = Participant(fulljid)
			# Now, override the new participant's attributes
			p.setNick(nick)
			p.setRole(role)
			p.setAffiliation(affiliation)
		else:
			# Modify an existing participant
			p = self.participants[fulljid]

		# See wether the participant can be added to the room depending on the room's type
		# Case 0: The participant is blacklisted
		if p.getBareJID() in self.blacklist:
			# "I told you not to come back! Get the f**k out of here!"
			return False
		# Case 1: Open and without password. Free way
		if self.open and self.unsecured:
			# Set the participants role based on the room's moderation and the 'role' parameter provided
			if self.moderated and not role:
				p.setRole('visitor')
			elif not self.moderated and not role:
				p.setRole('participant')
			self.participants[p.getFullJID()] = p
			return True
		# Case 2: Open but with password. "Say say say say the password"
		elif self.open and not self.unsecured:
			if password == self.password:
				# Free way
				# Set the participants role based on the room's moderation and the 'role' parameter provided
				if self.moderated and not role:
					p.setRole('visitor')
				elif not self.moderated and not role:
					p.setRole('participant')
				self.participants[p.getFullJID()] = p
				return True
			else:
				# Wrong password
				return False
		# Case 3: Members-only but without password
		elif not self.open and self.unsecured:
			if p.getBareJid() in self.whitelist:
				# "Welcome back, sir"
				# Set the participants role based on the room's moderation and the 'role' parameter provided
				if self.moderated and not role:
					p.setRole('visitor')
				elif not self.moderated and not role:
					p.setRole('participant')
				self.participants[p.getFullJID()] = p
				return True
			else:
				# "You're not on my list. Get lost"
				return False
		# Case 4: Members-only and with password
		elif not self.open and not self.unsecured:
			if p.getBareJid() in self.whitelist:
				if password == self.password:
					# Free way
					# Set the participants role based on the room's moderation and the 'role' parameter provided
					if self.moderated and not role:
						p.setRole('visitor')
					elif not self.moderated and not role:
						p.setRole('participant')
					self.participants[p.getFullJID()] = p
					return True
				else:
					# Bad password
					return False
			else:
				# Not a member. Get lost
				return False

	def setAffiliation(self, participant, affiliation):
		"""
		Set the affiliation of a participant
		"""
		# If 'participant' is a string
		if type(participant) == types.StringType:
			jid = participant
		# If its an instance of JID or Participant
		elif type(participant) == types.InstanceType:
			if isinstance(participant, JID):
				jid = str(participant)
			elif isinstance(participant, Participant): 
				jid = participant.getFullJID()

		# Change affiliation in the participants dict
		try:
			self.participants[jid].setAffiliation(affiliation)
		except:
			print "No such participant " + str(jid)


class MUC(PlugIn):
	"""
	The conference component. Composed of multiple rooms
	"""
	NS = ''
	#def __init__(self, jid, name):
	def plugin(self, server):
		self.server = server
		self.jid = server.mucjid
		self.name = server.mucname
		self.rooms = dict()

		general = Room('general', 'General Discussion')
		self.addRoom(general)

		self.DEBUG("Created MUC Conference " + str(self.jid), "warn")

	def printMUC(self):
		return str(self.jid) + ": " + str(self.rooms)

	def addRoom(self, room = None, jid = None):
		if room:
			# Add the given room
			self.rooms[str(room.name)] = room
			return True
		elif name:
			# Create a new (empty) default room with given jid
			self.rooms[str(name)] = Room(name)
		else:
			# Error: no room and no jid. Don't know what to do
			return False

	def dispatch(self, session, stanza):
		"""
		Mini-dispatcher for the jabber stanzas that arrive to the Conference
		"""
		self.DEBUG("MUC dispatcher called", "warn")
		try:
			to = stanza['to']
			room = to.getNode()
			domain = to.getDomain()
		except:
			# There was no 'to'
			pass

		# No room name. Stanza directed to the Conference
		if room == '' and domain == str(self.jid):
			if stanza.getName() == 'iq':
				self.IQ_cb(stanza, session)
			# TODO: Implement the rest of protocols


	def IQ_cb(self, iq, session):
		"""
		Manages IQ stanzas directed to the Conference itself
		"""
		self.DEBUG("MUC Iq callback called", "warn")
		# Look for the query xml namespace
		query = iq.getTag('query')
		print "### query = " + str(query)
		if query:
			try:
				ns = str(iq.getQueryNS())
				print "ns = " + ns
				# Discovery Info
				if ns == NS_DISCO_INFO:
					# Build reply
					reply = Iq('result', NS_DISCO_INFO, to=iq.getFrom(), frm=str(self.jid))
					id = iq.getAttr('id')
					if id:
						reply.setAttr('id', id)
					identity = Node('identity', { 'category': 'conference', 'type': 'text', 'name':self.name })
					feature = Node('feature', { 'var': 'http://jabber.org/protocol/muc' })
					reply.getQuerynode().addChild(node = identity)
					reply.getQuerynode().addChild(node = feature)
					session.enqueue(reply)
				# Discovery Items, i.e., the rooms
				elif ns == NS_DISCO_ITEMS:
					self.DEBUG("NS_DISCO_ITEMS requested", "warn")
					# Build reply
					reply = Iq('result', NS_DISCO_ITEMS, to=iq.getFrom(), frm=str(self.jid))
					id = iq.getAttr('id')
                                        if id:
                                        	reply.setAttr('id', id)
					# For each room in the conference, generate an 'item' element with info about the room
					for room in self.rooms.keys():
						print "### room = " + str(room)
						item = Node('item', { 'jid': str(room+'@'+self.jid), 'name': str(self.rooms[room].subject) })
						print "### item done = " + str(item)
						print "### reply = " + str(reply)
						reply.getQuerynode().addChild(node = item)
						print "### reply = " + str(reply)
					session.enqueue(reply)
					self.DEBUG("NS_DISCO_ITEMS sent", "warn")
					
			except:
				print " ### No xmlns, don't know what to do"
				pass
			
		


# Debug main code
if __name__ == "__main__":
	conf = Conference("muc.localhost")
	p1 = Participant('p1@localhost/res', nick="PlayerOne")
	p2 = Participant('p2@localhost/Gaim', nick="PlayerTwo")
	r1 = Room('house@muc.localhost', "My House", creator=p1)
	r2 = Room('auction@muc.localhost', "Auction House", creator=p2)
	r1.addParticipant(participant=p2)

	conf.addRoom(r1)
	conf.addRoom(r2)
	
	print p1
	print p2
	print r1
	print conf
