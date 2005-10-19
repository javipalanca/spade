##   client.py
##
##   Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

# $Id: client.py,v 1.36 2005/05/08 04:51:34 snakeru Exp $

"""
Provides PlugIn class functionality to develop extentions for xmpppy.
Also provides Client and Component classes implementations as the
examples of xmpppy structures usage.
These classes can be used for simple applications "AS IS" though.
"""

import debug
Debug=debug
Debug.DEBUGGING_IS_ON=1
Debug.Debug.colors['socket']=debug.color_dark_gray
Debug.Debug.colors['CONNECTproxy']=debug.color_dark_gray
Debug.Debug.colors['nodebuilder']=debug.color_brown
Debug.Debug.colors['client']=debug.color_cyan
Debug.Debug.colors['component']=debug.color_cyan
Debug.Debug.colors['dispatcher']=debug.color_green
Debug.Debug.colors['auth']=debug.color_yellow
Debug.Debug.colors['roster']=debug.color_magenta
Debug.Debug.colors['ibb']=debug.color_yellow

Debug.Debug.colors['down']=debug.color_brown
Debug.Debug.colors['up']=debug.color_brown
Debug.Debug.colors['data']=debug.color_brown
Debug.Debug.colors['ok']=debug.color_green
Debug.Debug.colors['warn']=debug.color_yellow
Debug.Debug.colors['error']=debug.color_red
Debug.Debug.colors['start']=debug.color_dark_gray
Debug.Debug.colors['stop']=debug.color_dark_gray
Debug.Debug.colors['sent']=debug.color_yellow
Debug.Debug.colors['got']=debug.color_bright_cyan

DBG_CLIENT='client'
DBG_COMPONENT='component'

class PlugIn:
    """ Common xmpppy plugins infrastructure: plugging in/out, debugging. """
    def __init__(self):
        self._exported_methods=[]
        self.DBG_LINE=self.__class__.__name__.lower()

    def PlugIn(self,owner):
        """ Attach to main instance and register ourself and all our staff in it. """
        self._owner=owner
        if self.DBG_LINE not in owner.debug_flags:
            owner.debug_flags.append(self.DBG_LINE)
        self.DEBUG('Plugging %s into %s'%(self,self._owner),'start')
        if owner.__dict__.has_key(self.__class__.__name__):
            return self.DEBUG('Plugging ignored: another instance already plugged.','error')
        self._old_owners_methods=[]
        for method in self._exported_methods:
            if owner.__dict__.has_key(method.__name__):
                self._old_owners_methods.append(owner.__dict__[method.__name__])
            owner.__dict__[method.__name__]=method
        owner.__dict__[self.__class__.__name__]=self
        if self.__class__.__dict__.has_key('plugin'): return self.plugin(owner)
 
    def PlugOut(self):
        """ Unregister all our staff from main instance and detach from it. """
        self.DEBUG('Plugging %s out of %s.'%(self,self._owner),'stop')
        self._owner.debug_flags.remove(self.DBG_LINE)
        for method in self._exported_methods: del self._owner.__dict__[method.__name__]
        for method in self._old_owners_methods: self._owner.__dict__[method.__name__]=method
        del self._owner.__dict__[self.__class__.__name__]
        if self.__class__.__dict__.has_key('plugout'): return self.plugout()

    def DEBUG(self,text,severity='info'):
        """ Feed a provided debug line to main instance's debug facility along with our ID string. """
        self._owner.DEBUG(self.DBG_LINE,text,severity)

import transports,dispatcher,auth,roster
class CommonClient:
    """ Base for Client and Component classes."""
    def __init__(self,server,port=5222,debug=['always', 'nodebuilder']):
        """ Caches server name and (optionally) port to connect to. "debug" parameter specifies
            the debug IDs that will go into debug output. You can either specifiy an "include"
            or "exclude" list. The latter is done via adding "always" pseudo-ID to the list.
            Full list: ['nodebuilder', 'dispatcher', 'gen_auth', 'SASL_auth', 'bind', 'socket', 
             'CONNECTproxy', 'TLS', 'roster', 'browser', 'ibb'] . """
        if self.__class__.__name__=='Client': self.Namespace,self.DBG='jabber:client',DBG_CLIENT
        elif self.__class__.__name__=='Component': self.Namespace,self.DBG=dispatcher.NS_COMPONENT_ACCEPT,DBG_COMPONENT
        self.defaultNamespace=self.Namespace
        self.disconnect_handlers=[]
        self.Server=server
        self.Port=port
        if debug and type(debug)<>list: debug=['always', 'nodebuilder']
        self._DEBUG=Debug.Debug(debug)
        self.DEBUG=self._DEBUG.Show
        self.debug_flags=self._DEBUG.debug_flags
        self.debug_flags.append(self.DBG)
        self._owner=self
        self._registered_name=None
        self.RegisterDisconnectHandler(self.DisconnectHandler)
        self.connected=''

    def RegisterDisconnectHandler(self,handler):
        """ Register handler that will be called on disconnect."""
        self.disconnect_handlers.append(handler)

    def UnregisterDisconnectHandler(self,handler):
        """ Unregister handler that is called on disconnect."""
        self.disconnect_handlers.remove(handler)

    def disconnected(self):
        """ Called on disconnection. Calls disconnect handlers and cleans things up. """
        self.connected=''
        self.DEBUG(self.DBG,'Disconnect detected','stop')
        self.disconnect_handlers.reverse()
        for i in self.disconnect_handlers: i()
        self.disconnect_handlers.reverse()
        if self.__dict__.has_key('TLS'): self.TLS.PlugOut()

    def DisconnectHandler(self):
        """ Default disconnect handler. Just raises an IOError.
            If you choosed to use this class in your production client,
            override this method or at least unregister it. """
        raise IOError('Disconnected from server.')

    def event(self,eventName,args={}):
        """ Default event handler. To be overriden. """
        print "Event: ",(eventName,args)

    def isConnected(self):
        """ Returns connection state. F.e.: None / 'tls' / 'tcp+non_sasl' . """
        return self.connected

    def reconnectAndReauth(self):
        """ Example of reconnection method. In fact, it can be used to batch connection and auth as well. """
        handlerssave=self.Dispatcher.dumpHandlers()
        self.Dispatcher.PlugOut()
        if not self.connect(server=self._Server,proxy=self._Proxy): return
        if not self.auth(self._User,self._Password,self._Resource): return
        self.Dispatcher.restoreHandlers(handlerssave)
        return self.connected

    def connect(self,server=None,proxy=None):
        """ Make a tcp/ip connection, protect it with tls if possible and start XMPP stream. """
        if not server: server=(self.Server,self.Port)
        if proxy: connected=transports.HTTPPROXYsocket(proxy,server).PlugIn(self)
        else: connected=transports.TCPsocket(server).PlugIn(self)
        if not connected: return
        self._Server,self._Proxy=server,proxy
        self.connected='tcp'
        if self.Connection.getPort()==5223:
            transports.TLS().PlugIn(self,now=1)
            self.connected='tls'
        dispatcher.Dispatcher().PlugIn(self)
        while self.Dispatcher.Stream._document_attrs is None: self.Process(1)
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
        return self.connected

class Client(CommonClient):
    """ Example client class, based on CommonClient. """
    def connect(self,server=None,proxy=None,tls=1):
        """ Connect to jabber server. If you want to specify different ip/port to connect to you can
            pass it as tuple as first parameter. If there is HTTP proxy between you and server -
            specify it's address and credentials (if needed) in the second argument.
            Example: connect(('192.168.5.5':5222),{'host':'proxy.my.net','port':8080,'user':'me','password':'secret'})"""
        if not CommonClient.connect(self,server,proxy) or not tls: return self.connected
        transports.TLS().PlugIn(self)
        if not self.Dispatcher.Stream._document_attrs.has_key('version') or not self.Dispatcher.Stream._document_attrs['version']=='1.0': return self.connected
        while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
        if not self.Dispatcher.Stream.features.getTag('starttls'): return self.connected       # TLS not supported by server
        while not self.TLS.starttls and self.Process(): pass
        if self.TLS.starttls<>'success': self.event('tls_failed'); return self.connected
        self.connected='tls'
        return self.connected

    def auth(self,user,password,resource=''):
        """ Authenticate connnection and bind resource. If resource is not provided
            random one or library name used. """
        self._User,self._Password,self._Resource=user,password,resource
        while not self.Dispatcher.Stream._document_attrs and self.Process(): pass
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
        auth.SASL().PlugIn(self)
        if self.SASL.startsasl=='not-supported':
            if not resource: resource='xmpppy'
            if auth.NonSASL(user,password,resource).PlugIn(self):
                self.connected+='+old_auth'
                return 'old_auth'
            return
        self.SASL.auth(user,password)
        while self.SASL.startsasl=='in-process' and self.Process(): pass
        if self.SASL.startsasl=='success':
            auth.Bind().PlugIn(self)
            while self.Bind.bound is None: self.Process()
            if self.Bind.Bind(resource):
                self.connected+='+sasl'
                return 'sasl'

    def getRoster(self):
        """ Return the Roster instance, previously plugging it in and
            requesting roster from server if needed. """
        if not self.__dict__.has_key('Roster'): roster.Roster().PlugIn(self)
        return self.Roster.getRoster()

    def sendInitPresence(self,requestRoster=1):
        """ Send roster request and initial <presence/>.
            You can disable the first by setting requestRoster argument to 0. """
        self.sendPresence(requestRoster=requestRoster)

    def sendPresence(self,jid=None,typ=None,requestRoster=0):
        """ Send some specific presence state.
            Can also request roster from server if according agrument is set."""
        if requestRoster: roster.Roster().PlugIn(self)
        self.send(dispatcher.Presence(to=jid, typ=typ))

class Component(CommonClient):
    """ Component class. The only difference from CommonClient is ability to perform component authentication. """
    def __init__(self,server,port=5347,typ=None,debug=['always', 'nodebuilder']):
        """ Init function for Components.
            As components use a different auth mechanism which includes the namespace of the component.
            Jabberd1.4 and Ejabberd use the default namespace then for all client messages.
            Jabberd2 uses jabber:client."""
        CommonClient.__init__(self,server,port=port,debug=debug)
        self.typ=typ
    
    def connect(self,server=None,proxy=None):
        """ This will connect to the server, and if the features tag is found then set
            the namespace to be jabber:client as that is required for jabberd2"""
        CommonClient.connect(self,server=server,proxy=proxy)
        if self.typ=='jabberd2' or not self.typ and self.Dispatcher.Stream.features != None:
                self.defaultNamespace=auth.NS_CLIENT
                self.Dispatcher.RegisterNamespace(self.defaultNamespace)
                self.Dispatcher.RegisterProtocol('iq',dispatcher.Iq)
                self.Dispatcher.RegisterProtocol('message',dispatcher.Message)
                self.Dispatcher.RegisterProtocol('presence',dispatcher.Presence)
        return self.connected

    def auth(self,name,password,dup=None):
        """ Authenticate component "name" with password "password"."""
        self._User,self._Password,self._Resource=name,password,''
        return auth.NonSASL(name,password,'').PlugIn(self)
