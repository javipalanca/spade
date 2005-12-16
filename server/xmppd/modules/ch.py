
from xmpp import *
from xmppd import *

components_db = {}
components_db['localhost'] = {}
components_db['localhost']['acc'] = ['9000', 'secret']

class CH(PlugIn):
	NS=''
	def configureCH(self, server):
		'''Kinda constructor'''
		self.port = 9000
		self.password = 'secret'
		self.server = server
		self.names = []
		# For each servername, create an acc referer name
		for name in server.servernames:
			name = 'acc.' + name
			self.names.append(name)
		
 
	def do(self, session, stanza):
		print "####################################"
		print "####################################"
		print "####################################"
		print "DO THE KUNG FU " + str(session) + " " + str(stanza)
		print "####################################"
		print "####################################"
		print "####################################"

        def plugin(self,server):
        	self._data = {}
		self.configureCH(server)
		server.Dispatcher.RegisterNamespace('jabber:component:accept')
        	server.Dispatcher.RegisterNamespaceHandler('jabber:component:accept',self.componentHandler)

	def componentHandler(self, session, stanza):
		print "Component Handler called"
		print "Server Routes:"
		print self.server.routes
		name = stanza.getName()
		if name == 'handshake':
			# Reply handshake
			rep = Node('handshake')
			session.send(rep)
			# Identify component
			host,port = session._sock.getsockname()
			#print "HOST: " + str(host) + " PORT: " + str(port)
			primary_name = self.server.servernames[0]
			if port == 9000:  # ACC
				component_name = 'acc.' + primary_name
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
				raise NodeProcessed				
			elif port == 9001:  # AMS
				component_name = 'ams.' + primary_name
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
				raise NodeProcessed				
			elif port == 9002:  # DF
				component_name = 'df.' + primary_name
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
				raise NodeProcessed				
		elif name == 'message':
			print "Component sends a MESSAGE"
			to=stanza['to']
			simple_to = str(to)
        		#if not('@' in simple_to):  # Component name
                	s=self._owner.getsession(to)
        		if s:
				print "Found session for to: %s %d" % (str(to), s._session_state)
                		s.enqueue(stanza)
                		print "Stanza going to component enqueue"
				print s.stanza_queue
                	raise NodeProcessed
		else:
			if session._session_state >= SESSION_AUTHED:
				print "COMPONENT SENDS:"
				print str(stanza)

