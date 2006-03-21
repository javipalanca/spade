# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# router, presence tracker and probes responder for xmppd.py

# $Id: router.py,v 1.5 2004/10/24 04:36:28 snakeru Exp $

from xmpp import *
from xmppd import *
from constants import *
from types import *
from filter import *

import os

class Router(PlugIn):
    """ The first entity that gets access to arrived stanza. """
    NS='presence'
    def plugin(self,server):
        self._data = {}
        # For the common folk
	#server.Dispatcher.RegisterNamespace(NS_COMPONENT_ACCEPT)
	
	server.Dispatcher.RegisterNamespaceHandler(NS_CLIENT,self.routerHandler)
        server.Dispatcher.RegisterNamespaceHandler(NS_SERVER,self.routerHandler)
        
	server.Dispatcher.RegisterNamespaceHandler(NS_COMPONENT_ACCEPT,self.routerHandler) # Mine
	server.Dispatcher.RegisterHandler('handshake',self.componentHandler,xmlns=NS_COMPONENT_ACCEPT)  # Mine
	server.Dispatcher.RegisterHandler('message',self.routerHandler,xmlns=NS_COMPONENT_ACCEPT)  # Mine
	self.server = server
        
	server.Dispatcher.RegisterHandler('presence',self.presenceHandler)


	#Init filters
	for name in server.router_filter_names:
		"""
		if name[-3:] == ".py":
			name = name[:-3]
			#name = name + ".py"
		#name = 'xmppd' + '.' + name
		
		try:
			module = __import__(name, fromlist="xmppd")
		except:
			self.DEBUG("Could not import filter module "+str(name),"error")
			break
		for f in vars(module).itervalues():
			if type(f)==ClassType and issubclass(f, Filter):
				try:
					filter = f(self)
					self.DEBUG("Filter "+ str(name) + " loaded","info")
					server.router_filters.append(filter)
				except:
					self.DEBUG("Could not load filter "+str(name),"error")
        	"""
		if issubclass(name,Filter):
			try:
				filter = name(self)
				self.DEBUG("Filter "+ str(name) + " loaded","info")
				server.router_filters.append(filter)
			except:
				self.DEBUG("Could not load filter "+str(name),"error")

    def presenceHandler(self,session,stanza):
#       filter out presences that should not influate our 'roster'
#       This is presences, that's addressed:
#        1) any other server
#        2) any user
        to=stanza['to']
        if  to and (
            to.getDomain() not in self._owner.servernames or
            to.getNode() ):
                return

        typ=stanza.getType()
        jid=session.peer
        try: barejid,resource=jid.split('/')
        except: raise NodeProcessed # Closure of not yet bound session

        if not typ or typ=='available':
            if not self._data.has_key(barejid): self._data[barejid]={}
            if not self._data[barejid].has_key(resource): self._data[barejid][resource]=Presence(frm=jid,typ=typ)
            bp=self._data[barejid][resource]

            try: priority=int(stanza.getTagData('priority'))
            except: priority=0
            bp.T.priority=`priority`
            self._owner.activatesession(session)

            show=stanza.getTag('show')
            if show: bp.T.show=show
            status=stanza.getTag('status')
            if status: bp.T.show=status
            bp.setTimestamp()
            self.update(barejid)
        elif typ=='unavailable' or typ=='error':
            if not self._data.has_key(barejid): raise NodeProcessed
            if self._data[barejid].has_key(resource): del self._data[barejid][resource]
            self.update(barejid)
            if not self._data[barejid]: del self._data[barejid]
            self._owner.deactivatesession(session.peer)
        elif typ=='probe':
            try:
                resources=[stanza.getTo().getResource()]
                if not resources[0]: resources=self._data[barejid].keys()
                flag=1
                for resource in resources:
                    p=Presence(to=stanza.getFrom(),frm=session.peer,node=self._data[barejid][resource])
                    if flag:
                        self._owner.Privacy(session.peer,p)
                        flag=None
                    session.enqueue(p)
            except KeyError: session.enqueue(Presence(to=stanza.getFrom(),frm=jid,typ='unavailable'))
        else: return
        raise NodeProcessed

    def update(self,barejid):
        pri=-1
        s=None
        for resource in self._data[barejid].keys():
            rpri=int(self._data[barejid][resource].getTagData('priority'))
            if rpri>pri: s=self._owner.getsession(barejid+'/'+resource)
        if s: self._owner.activatesession(s,barejid)
        else: self._owner.deactivatesession(barejid)

    def safeguard(self,session,stanza):
        if stanza.getNamespace() not in [NS_CLIENT,NS_SERVER,NS_COMPONENT_ACCEPT]: return # this is not XMPP stanza
        #if stanza.getNamespace() not in [NS_CLIENT,NS_SERVER]: return # this is not XMPP stanza

	# This is ugly and unorthodox, but it works: bypass security for handshakes
	if stanza.getNamespace()==NS_COMPONENT_ACCEPT and stanza.getName()=='handshake':
		self.DEBUG("safeguard: handshake received, calling handler", 'info')
		return

	if session._session_state<SESSION_AUTHED: # NOT AUTHED yet (stream's stuff already done)
            session.terminate_stream(STREAM_NOT_AUTHORIZED)
            raise NodeProcessed
	
        frm=stanza['from']
        to=stanza['to']
        if stanza.getNamespace()==NS_SERVER:
            if not frm or not to \
              or frm.getDomain()<>session.peer \
              or to.getDomain()<>session.ourname:
                session.terminate_stream(STREAM_IMPROPER_ADDRESSING)
                raise NodeProcessed
        else:
            if frm and frm<>session.peer:   # if the from address specified and differs
                if frm.getResource() or not frm.bareMatch(session.peer): # ...it can differ only while comparing inequally
                    session.terminate_stream(STREAM_INVALID_FROM)
                    raise NodeProcessed

            if session._session_state<SESSION_BOUND: # NOT BOUND yet (bind stuff already done)
                if stanza.getType()<>'error': session.send(Error(stanza,ERR_NOT_AUTHORIZED))
                raise NodeProcessed

            if name=='presence' and session._session_state<SESSION_OPENED:
                if stanza.getType()<>'error': session.send(Error(stanza,ERR_NOT_ALLOWED))
                raise NodeProcessed
            stanza.setFrom(session.peer)

    def routerHandler(self,session,stanza):
        """ XMPP-Core 9.1.1 rules """
        name=stanza.getName()
        self.DEBUG('Router handler called','info')
	#print "With stanza:"
	#print stanza


	#Apply filters
	for f in server.router_filters:
		if f.test(stanza):
			stanza = f.filter(session,stanza)
			if stanza == None:
				raise NodeProcessed


        to=stanza['to']
	"""
# 0. It's a component
	# Counter measure for component originated messages
	the_from = stanza['from']
	simple_from = str(the_from)
	if not('@' in simple_from):  # Component-originated
		if stanza.getNamespace()==NS_COMPONENT_ACCEPT and stanza.getName()=='message':
			# Fake the namespace. Pose as a client
			stanza.setNamespace(NS_CLIENT)
			self.DEBUG("NS faked: " + str(stanza.getNamespace()), 'info')

	# Measure for component-destinated stanzas
	simple_to = str(to)
	s = False
	if not('@' in simple_to):  # Component name
		# SPADE CASE: message directed to the ACC component
		if simple_to[0:4] == "acc.":
			self.DEBUG("ACC MESSAGE MUST BE TUNNELED", "info")
			# We must find the real "to" of the message
			try:
				receivers = self._owner.accPlugIn.getRealTo(stanza)
				self.DEBUG("router: getRealTo returned " + str(receivers), "info")
				to = str(receivers[0])  # FIX THIS TO ALLOW MULTIPLE RECEIVERS
				s = False
				self.DEBUG(">> ACC MESSAGE TUNNELED: " + str(to) , "info")
				# We do NOT raise the NodeProcessed exception, the message follows its normal course from here
			except:
				self.DEBUG("ACC FAILED", "info")
		# SPECIAL CASE: message directed to the server itself
		if (simple_to in self._owner.servernames) and (stanza.getName()=='message'):
			# Process message
			self.DEBUG("Message for the server", 'info')
			self.servercommandHandler(session, stanza)
			raise NodeProcessed
	        else:
			s=self._owner.getsession(to)
		self.DEBUG("Component getsession("+str(to)+") ->" + str(s), 'info')
	if s:
		s.enqueue(stanza)
		self.DEBUG("There was a message for a component and it has been delivered", 'info')
		raise NodeProcessed

# Non-components from here
	"""


        if stanza.getNamespace()==NS_CLIENT and \
            (not to or to==session.ourname) and \
            stanza.props in ( [NS_AUTH], [NS_REGISTER], [NS_BIND], [NS_SESSION] ):
              return

        if not session.trusted: self.safeguard(session,stanza)
	
        if not to: return # stanza.setTo(session.ourname)
        domain=to.getDomain()

        getsession=self._owner.getsession
        if domain in self._owner.servernames:
            node=to.getNode()
            if not node: return
            self._owner.Privacy(session.peer,stanza) # it will raise NodeProcessed if needed
            bareto=node+'@'+domain
	    dbg_msg='BARETO: ' + bareto
	    self.DEBUG(dbg_msg, 'info')
            resource=to.getResource()
# 1. If the JID is of the form <user@domain/resource> and an available resource matches the full JID, 
#    the recipient's server MUST deliver the stanza to that resource.
            if resource:
                to=bareto+'/'+resource
                s=getsession(to)
                if s:
                    s.enqueue(stanza)
                    raise NodeProcessed
# 2. Else if the JID is of the form <user@domain> or <user@domain/resource> and the associated user account 
#    does not exist, the recipient's server (a) SHOULD silently ignore the stanza (i.e., neither deliver it 
#    nor return an error) if it is a presence stanza, (b) MUST return a <service-unavailable/> stanza error 
#    to the sender if it is an IQ stanza, and (c) SHOULD return a <service-unavailable/> stanza error to the 
#    sender if it is a message stanza.
            if not self._owner.AUTH.isuser(node,domain):
                if name in ['iq','message']:
                    if stanza.getType()<>'error': session.enqueue(Error(stanza,ERR_SERVICE_UNAVAILABLE))
                raise NodeProcessed
# 3. Else if the JID is of the form <user@domain/resource> and no available resource matches the full JID, 
#    the recipient's server (a) SHOULD silently ignore the stanza (i.e., neither deliver it nor return an 
#    error) if it is a presence stanza, (b) MUST return a <service-unavailable/> stanza error to the sender 
#    if it is an IQ stanza, and (c) SHOULD treat the stanza as if it were addressed to <user@domain> if it 
#    is a message stanza.
            if resource and name<>'message':
                if name=='iq' and stanza.getType()<>'error': session.enqueue(Error(stanza,ERR_SERVICE_UNAVAILABLE))
                raise NodeProcessed
# 4. Else if the JID is of the form <user@domain> and there is at least one available resource available 
#    for the user, the recipient's server MUST follow these rules:
            s=getsession(bareto)
            if s:
#       1. For message stanzas, the server SHOULD deliver the stanza to the highest-priority available 
#          resource (if the resource did not provide a value for the <priority/> element, the server SHOULD 
#          consider it to have provided a value of zero). If two or more available resources have the same 
#          priority, the server MAY use some other rule (e.g., most recent connect time, most recent 
#          activity time, or highest availability as determined by some hierarchy of <show/> values) 
#          to choose between them or MAY deliver the message to all such resources. However, the server 
#          MUST NOT deliver the stanza to an available resource with a negative priority; if the only 
#          available resource has a negative priority, the server SHOULD handle the message as if there 
#          were no available resources (defined below). In addition, the server MUST NOT rewrite the 'to' 
#          attribute (i.e., it MUST leave it as <user@domain> rather than change it to <user@domain/resource>).
                if name=='message':
                    s.enqueue(stanza)
                    raise NodeProcessed
#       2. For presence stanzas other than those of type "probe", the server MUST deliver the stanza to all 
#          available resources; for presence probes, the server SHOULD reply based on the rules defined in 
#          Presence Probes. In addition, the server MUST NOT rewrite the 'to' attribute (i.e., it MUST leave 
#          it as <user@domain> rather than change it to <user@domain/resource>).
                elif name=='presence':
                    # all probes already processed so safely assuming "other" type
                    for resource in self._data[bareto].keys():
                        s=getsession(bareto+'/'+resource)
                        if s: s.enqueue(stanza)
                    raise NodeProcessed
#       3. For IQ stanzas, the server itself MUST reply on behalf of the user with either an IQ result or an 
#          IQ error, and MUST NOT deliver the IQ stanza to any of the available resources. Specifically, if 
#          the semantics of the qualifying namespace define a reply that the server can provide, the server 
#          MUST reply to the stanza on behalf of the user; if not, the server MUST reply with a 
#          <service-unavailable/> stanza error.
                return
# 5. Else if the JID is of the form <user@domain> and there are no available resources associated with 
#    the user, how the stanza is handled depends on the stanza type:
            else:
#       1. For presence stanzas of type "subscribe", "subscribed", "unsubscribe", and "unsubscribed", 
#          the server MUST maintain a record of the stanza and deliver the stanza at least once (i.e., when 
#          the user next creates an available resource); in addition, the server MUST continue to deliver 
#          presence stanzas of type "subscribe" until the user either approves or denies the subscription 
#          request (see also Presence Subscriptions).
                if name=='presence':
                    if stanza.getType() in ["subscribe", "subscribed", "unsubscribe", "unsubscribed"]:
                        self._owner.DB.store(domain,node,stanza,id=stanza.getType().strip('un'))
#       2. For all other presence stanzas, the server SHOULD silently ignore the stanza by not storing it 
#          for later delivery or replying to it on behalf of the user.
                    raise NodeProcessed
#       3. For message stanzas, the server MAY choose to store the stanza on behalf of the user and deliver 
#          it when the user next becomes available, or forward the message to the user via some other means 
#          (e.g., to the user's email account). However, if offline message storage or message forwarding 
#          is not enabled, the server MUST return to the sender a <service-unavailable/> stanza error. (Note: 
#          Offline message storage and message forwarding are not defined in XMPP, since they are strictly a 
#          matter of implementation and service provisioning.)
                elif name=='message':
                    #self._owner.DB.store(domain,node,stanza)
                    if stanza.getType()<>'error': session.enqueue(Error(stanza,ERR_RECIPIENT_UNAVAILABLE))
                    raise NodeProcessed
#       4. For IQ stanzas, the server itself MUST reply on behalf of the user with either an IQ result or 
#          an IQ error. Specifically, if the semantics of the qualifying namespace define a reply that the 
#          server can provide, the server MUST reply to the stanza on behalf of the user; if not, the server 
#          MUST reply with a <service-unavailable/> stanza error.
                return
        else:
            s=getsession(domain)
            if not s:
		self.DEBUG("S2S: Message to another server", 'info')
                s=self._owner.S2S(session.ourname,domain)
            s.enqueue(stanza)
            raise NodeProcessed


    def componentHandler(self, session, stanza):
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
                        #"Component sends a MESSAGE"
                        to=stanza['to']
                        simple_to = str(to)
                        #if not('@' in simple_to):  # Component name
                        s=self._owner.getsession(to)
                        if s:
                                self.DEBUG( "Found session for to: %s %d" % (str(to), s._session_state),'info')
                                s.enqueue(stanza)
                        raise NodeProcessed
                else:
                        if session._session_state >= SESSION_AUTHED:
                                self.DEBUG( str(stanza), 'send')

    def servercommandHandler(self, session, stanza):
		#print ">>>>> stanza = " + str(stanza)
		#simple_from = stanza['from']
		simple_from = ''
		for k, v in self._owner.routes.items():
			if v == session:
				simple_from = k
		if simple_from == '':
			# Bizarre situation when a command has arrived from a non-existent session
			return
		username = simple_from.split('@')[0]
		print ">>>>> Command from " + str(username)
            	if self._owner.AUTH.isadmin(str(username)):
			# An admin has sent a command
			body = stanza.getBody()
			if body == 'SAVEDB':
				try:
					if self._owner.DB.savedb():
						simple_to = str(stanza['to'])
						rep = Message(simple_from,'Database Saved Succesfully', frm=simple_to)
						session.enqueue(rep)
				except:
					pass
			elif body == 'LOADDB':
				try:
					if self._owner.DB.loaddb():
						simple_to = str(stanza['to'])
						rep = Message(simple_from,'Database Loaded Succesfully', frm=simple_to)
						session.enqueue(rep)						
				except:
					pass
			elif body == 'DB':
				try:
					content = str(self._owner.DB.listdb())
					simple_to = str(stanza['to'])
					rep = Message(simple_from,content,frm=simple_to)
					session.enqueue(rep)
				except:
					pass					

