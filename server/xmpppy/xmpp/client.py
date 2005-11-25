##   client.py
##
##   Copyright (C) 2003-2004 Alexey "Snake" Nezhdanov
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

# $Id: client.py,v 1.28 2004/09/19 20:05:11 snakeru Exp $

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
    def __init__(self):
        self._exported_methods=[]
        self.DBG_LINE=self.__class__.__name__.lower()

    def PlugIn(self,owner):
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
        self.DEBUG('Plugging %s out of %s.'%(self,self._owner),'stop')
        self._owner.debug_flags.remove(self.DBG_LINE)
        for method in self._exported_methods: del self._owner.__dict__[method.__name__]
        for method in self._old_owners_methods: self._owner.__dict__[method.__name__]=method
        del self._owner.__dict__[self.__class__.__name__]
        if self.__class__.__dict__.has_key('plugout'): return self.plugout()

    def DEBUG(self,text,severity='info'):
        self._owner.DEBUG(self.DBG_LINE,text,severity)

import transports,dispatcher,auth,roster
class CommonClient:
    def __init__(self,server,port=5222,debug=['always', 'nodebuilder']):
        if self.__class__.__name__=='Client': self.Namespace,self.DBG='jabber:client',DBG_CLIENT
        elif self.__class__.__name__=='Component': self.Namespace,self.DBG='jabber:component:accept',DBG_COMPONENT
        self.disconnect_handlers=[]
        self.Server=server
        self.Port=port
        self._DEBUG=Debug.Debug(debug)
        self.DEBUG=self._DEBUG.Show
        self.debug_flags=self._DEBUG.debug_flags
        self.debug_flags.append(self.DBG)
        self._owner=self
        self._registered_name=None
        self.RegisterDisconnectHandler(self.DisconnectHandler)
        self.connected=''

    def RegisterDisconnectHandler(self,handler):
        self.disconnect_handlers.append(handler)

    def UnregisterDisconnectHandler(self,handler):
        self.disconnect_handlers.remove(handler)

    def disconnected(self):
        self.connected=''
        self.DEBUG(self.DBG,'Disconnect detected','stop')
        self.disconnect_handlers.reverse()
        for i in self.disconnect_handlers: i()
        self.disconnect_handlers.reverse()
        if self.__dict__.has_key('TLS'): self.TLS.PlugOut()

    def DisconnectHandler(self):        # default stuff. To be overriden or unregistered.
        raise IOError('Disconnected from server.')

    def event(self,eventName,args={}):
        print "Event: ",(eventName,args)

    def isConnected(self): return self.connected

    def reconnectAndReauth(self):
        handlerssave=self.Dispatcher.dumpHandlers()
        self.Dispatcher.PlugOut()
        if not self.connect(server=self._Server,proxy=self._Proxy): return
        if not self.auth(self._User,self._Password,self._Resource): return
        self.Dispatcher.restoreHandlers(handlerssave)
        return self.connected

    def connect(self,server=None,proxy=None):
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
        return self.connected

class Client(CommonClient):
    def connect(self,server=None,proxy=None):
        if not CommonClient.connect(self,server,proxy): return self.connected
        transports.TLS().PlugIn(self)
        if not self.Dispatcher.Stream._document_attrs.has_key('version') or not self.Dispatcher.Stream._document_attrs['version']=='1.0': return self.connected
        while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
        if not self.Dispatcher.Stream.features.getTag('starttls'): return self.connected       # TLS not supported by server
        while not self.TLS.starttls and self.Process(): pass
        if self.TLS.starttls<>'success': self.event('tls_failed'); return self.connected
        self.connected='tls'
        return self.connected

    def auth(self,user,password,resource=''):
        self._User,self._Password,self._Resource=user,password,resource
        auth.SASL().PlugIn(self)
        self.SASL.auth(user,password)
        while not self.Dispatcher.Stream._document_attrs and self.Process(): pass
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
            while self.SASL.startsasl=='in-process' and self.Process(): pass
        else: self.SASL.startsasl='failure'
        if self.SASL.startsasl=='failure':
            if not resource: resource='xmpppy'
            if auth.NonSASL(user,password,resource).PlugIn(self):
                self.connected+='+old_auth'
                return 'old_auth'
        else:
            auth.Bind().PlugIn(self)
            while self.Bind.bound is None: self.Process()
            if self.Bind.Bind(resource):
                self.connected+='+sasl'
                return 'sasl'

    def getRoster(self):
        if not self.__dict__.has_key('Roster'): roster.Roster().PlugIn(self)
        return self.Roster.getRoster()

    def sendInitPresence(self,requestRoster=1):
        self.sendPresence(requestRoster=requestRoster)

    def sendPresence(self,jid=None,typ=None,requestRoster=0):
        if requestRoster: roster.Roster().PlugIn(self)
        self.send(dispatcher.Presence(to=jid, typ=typ))

class Component(CommonClient):
    def auth(self,name,password,dup=None):
        self._User,self._Password,self._Resource=name,password,''
        return auth.NonSASL(name,password,'').PlugIn(self)
