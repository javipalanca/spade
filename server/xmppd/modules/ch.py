
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
	        #server.Dispatcher.RegisterHandler('acc',self.do)
		#print "jabber:component:accept  REGISTERED !!!!"

	def componentHandler(self, session, stanza):
		print "Component Handler called"
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
			elif port == 9001:  # AMS
				component_name = 'ams.' + primary_name
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
			elif port == 9002:  # DF
				component_name = 'df.' + primary_name
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
		else:
			if session._session_state >= SESSION_AUTHED:
				print "COMPONENT SENDS:"
				print str(stanza)
		print self.server.routes
		raise NodeProcessed
		

