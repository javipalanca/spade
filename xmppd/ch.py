
from xmpp import *
from xmppd import *

class CH(PlugIn):
	NS=''
 
        def plugin(self,server):
		server.Dispatcher.RegisterNamespace('jabber:component:accept')
        	server.Dispatcher.RegisterNamespaceHandler('jabber:component:accept',self.componentHandler)

	def componentHandler(self, session, stanza):
		name = stanza.getName()
		if name == 'handshake':
			self.DEBUG("ch.py", "error")
			# Reply handshake
			rep = Node('handshake')
			session.send(rep)
			# Identify component
			host,port = session._sock.getsockname()
			#print "HOST: " + str(host) + " PORT: " + str(port)
			primary_name = self.server.servernames[0]

			if port == 9001:  # AMS
				component_name = 'ams.' + primary_name
				#self.server.componentList.append(component_name)
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
				raise NodeProcessed				
			elif port == 9002:  # DF
				component_name = 'df.' + primary_name
				#self.server.componentList.append(component_name)
				session.peer = component_name
				self.server.activatesession(session, component_name)
				session.set_session_state(SESSION_AUTHED)
				session.set_session_state(SESSION_OPENED)
				raise NodeProcessed

			raise NodeProcessed

		elif name == 'message':
			to=stanza['to']
			simple_to = str(to)
        		#if not('@' in simple_to):  # Component name
                	s=self._owner.getsession(to)
        		if s:
				self.DEBUG("Found session for to: %s %d" % (str(to), s._session_state), 'info')
                		s.enqueue(stanza)
                	raise NodeProcessed
		else:
			if session._session_state >= SESSION_AUTHED:
				self.DEBUG(str(stanza), 'send')

