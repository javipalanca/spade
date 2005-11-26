
from xmpp import *


class CH(PlugIn):
	NS=''
	def configureCH(self, server):
		'''Kinda constructor'''
		self.port = 9000
		self.password = 'secret'
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
		print "jabber:component:accept  REGISTERED !!!!"

	def componentHandler(self, session, stanza):
		#print "####################################"
		#print "####################################"
		#print "####################################"
		#print stanza	
		#print "####################################"
		#print "####################################"
		#print "####################################"
		print "Component Handler called"
		print stanza
		name = stanza.getName()
		if name == 'handshake':
			# Reply handshake
			rep = Node('handshake')
			session.send(rep)
		raise NodeProcessed
		

