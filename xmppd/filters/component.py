from xmppd import filter
from xmpp  import *
from spade import *

class Component(filter.Filter):

	def __init__(self,router):

		filter.Filter.__init__(self,router)

		#router.server.Dispatcher.RegisterNamespaceHandler(NS_COMPONENT_ACCEPT, router.routerHandler)
	        #router.server.Dispatcher.RegisterHandler('handshake', self.componentHandler, xmlns=NS_COMPONENT_ACCEPT)
        	#router.server.Dispatcher.RegisterHandler('message', router.routerHandler, xmlns=NS_COMPONENT_ACCEPT)


	def test(self,stanza):
		#Counter measure for component originated messages
		the_from = stanza['from']
		simple_from = str(the_from)
		to = str(stanza['to'])

		# Component-originated
		if not('@' in simple_from) and (simple_from not in self._router._owner.servernames):
			if stanza.getNamespace()==NS_COMPONENT_ACCEPT and stanza.getName()=='message':
				self._router.DEBUG("Message for a component",'info')
				return True
		if not ('@' in to) and (to not in self._router._owner.servernames): return True
		self._router.DEBUG("Message NOT for a component",'error')
		return False


	def filter(self,session,stanza):

			s = False
			to = str(stanza['to'])
			ffrom = str(stanza['from'])

			if not('@' in ffrom):
                        	# Fake the namespace. Pose as a client
	                        stanza.setNamespace(NS_CLIENT)
        	                #self._router.DEBUG("NS faked: " + str(stanza.getNamespace()), 'info')

			if not('@' in to):
				s=self._router._owner.getsession(to)
				#self._router.DEBUG("Component getsession("+str(to)+") ->" + str(s), 'info')
				if s:
					s.enqueue(stanza)
					self._router.DEBUG("message for a component delivered", 'info')
					return None


			return stanza



	def componentHandler(self, session, stanza):
                name = stanza.getName()
		print "COMPONENT HANDLER"
                if name == 'handshake':
			#self._router.DEBUG("HANDSHAKE received", 'info')
                        # Reply handshake
                        rep = Node('handshake')
                        session.send(rep)
                        # Identify component
                        host,port = session._sock.getsockname()
                        #print "HOST: " + str(host) + " PORT: " + str(port)
                        primary_name = self._router.server.servernames[0]
                        if port == 9000:  # ACC
                                component_name = 'acc.' + primary_name
                                session.peer = component_name
                                self._router.server.activatesession(session, component_name)
                                session.set_session_state(SESSION_AUTHED)
                                session.set_session_state(SESSION_OPENED)
                                raise NodeProcessed
                        elif port == 9001:  # AMS
                                component_name = 'ams.' + primary_name
                                session.peer = component_name
                                self._router.server.activatesession(session, component_name)
                                session.set_session_state(SESSION_AUTHED)
                                session.set_session_state(SESSION_OPENED)
                                raise NodeProcessed
                        elif port == 9002:  # DF
                                component_name = 'df.' + primary_name
                                session.peer = component_name
                                self._router.server.activatesession(session, component_name)
                                session.set_session_state(SESSION_AUTHED)
                                session.set_session_state(SESSION_OPENED)
                                raise NodeProcessed
                elif name == 'message':
                        #"Component sends a MESSAGE"
                        to=stanza['to']
                        simple_to = str(to)
			s=False
                        s=self._router._owner.getsession(to)
                        if s:
                                self._router.DEBUG( "Found session for to: %s %d" % (str(to), s._session_state),'info')
                                s.enqueue(stanza)
                        raise NodeProcessed
                else:
                        if session._session_state >= SESSION_AUTHED:
                                self._router.DEBUG( str(stanza), 'send')

