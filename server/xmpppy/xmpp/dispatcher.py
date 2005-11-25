##   transports.py
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

# $Id: dispatcher.py,v 1.24 2004/10/23 07:53:42 snakeru Exp $

import simplexml,time
from protocol import *
from client import PlugIn

DefaultTimeout=25
ID=0

class Dispatcher(PlugIn):
    def __init__(self):
        PlugIn.__init__(self)
        DBG_LINE='dispatcher'
        self.handlers={}
        self._expected={}
        self._defaultHandler=None
        self._eventHandler=None
        self._cycleHandlers=[]
        self._exported_methods=[self.Process,self.RegisterHandler,self.RegisterDefaultHandler,\
        self.RegisterEventHandler,self.UnregisterCycleHandler,self.RegisterCycleHandler,\
        self.RegisterHandlerOnce,self.UnregisterHandler,self.RegisterProtocol,\
        self.WaitForResponse,self.SendAndWaitForResponse,self.send,self.disconnect]

    def dumpHandlers(self): return self.handlers
    def restoreHandlers(self,handlers): self.handlers=handlers

    def _init(self):
        self.RegisterNamespace('unknown')
        self.RegisterNamespace(NS_CLIENT)
        self.RegisterProtocol('iq',Iq)
        self.RegisterProtocol('presence',Presence)
        self.RegisterProtocol('message',Message)
        self.RegisterDefaultHandler(self.returnStanzaHandler)

    def plugin(self, owner):
        self._init()
        for method in self._old_owners_methods:
            if method.__name__=='send': self._owner_send=method; break
        self._owner.lastErrNode=None
        self._owner.lastErr=None
        self._owner.lastErrCode=None
        self.StreamInit()

    def plugout(self):
        self.Stream.dispatch=None
        self.Stream.DEBUG=None
        self.Stream.features=None
        self.Stream.destroy()

    def StreamInit(self):
        self.Stream=simplexml.NodeBuilder()
        self.Stream._dispatch_depth=2
        self.Stream.dispatch=self.dispatch
        self._owner.debug_flags.append(simplexml.DBG_NODEBUILDER)
        self.Stream.DEBUG=self._owner.DEBUG
        self.Stream.features=None
        self._owner.send("<?xml version='1.0'?><stream:stream version='1.0' xmlns:stream='http://etherx.jabber.org/streams' to='%s' xmlns='%s'>"%(self._owner.Server,self._owner.Namespace))

    def Process(self, timeout=0):
        """Returns:
            1) length of processed data if some data were processed;
            2) '0' string if no data were processed but link is alive;
            3) 0 (zero) if underlying connection is closed."""
        for handler in self._cycleHandlers: handler(self)
        if self._owner.Connection.pending_data(timeout):
            data=self._owner.Connection.receive()
            self.Stream.Parse(data)
            return len(data)
        return '0'	# It means that nothing is received but link is alive.
        
    def RegisterNamespace(self,xmlns,order='info'):
        self.DEBUG('Registering namespace "%s"'%xmlns,order)
        self.handlers[xmlns]={}
        self.RegisterProtocol('unknown',Protocol,xmlns=xmlns)
        self.RegisterProtocol('default',Protocol,xmlns=xmlns)

    def RegisterProtocol(self,tag_name,Proto,xmlns=NS_CLIENT,order='info'):
        self.DEBUG('Registering protocol "%s" as %s(%s)'%(tag_name,Proto,xmlns), order)
        self.handlers[xmlns][tag_name]={type:Proto, 'default':[]}

    def RegisterNamespaceHandler(self,xmlns,handler,typ='',ns='', makefirst=0, system=0):
        self.RegisterHandler('default', handler, typ, ns, xmlns, makefirst, system)

    def RegisterHandler(self,name,handler,typ='',ns='',xmlns=NS_CLIENT, makefirst=0, system=0):
        self.DEBUG('Registering handler %s for "%s" type->%s ns->%s(%s)'%(handler,name,typ,ns,xmlns), 'info')
        if not typ and not ns: typ='default'
        if not self.handlers.has_key(xmlns): self.RegisterNamespace(xmlns,'warn')
        if not self.handlers[xmlns].has_key(name): self.RegisterProtocol(name,Protocol,xmlns,'warn')
        if not self.handlers[xmlns][name].has_key(typ+ns): self.handlers[xmlns][name][typ+ns]=[]
        if makefirst: self.handlers[xmlns][name][typ+ns].insert({'func':handler,'system':system})
        else: self.handlers[xmlns][name][typ+ns].append({'func':handler,'system':system})

    def RegisterHandlerOnce(self,name,handler,typ='',ns='',xmlns=NS_CLIENT,makefirst=0, system=0):
        self.RegisterHandler(name, handler, typ, ns, xmlns, makefirst, system)

    def UnregisterHandler(self,name,handler,typ='',ns='',xmlns=NS_CLIENT):
        if not typ and not ns: typ='default'
        for pack in self.handlers[xmlns][name][typ+ns]:
            if handler==pack['func']: break
        else: pack=None
        try: self.handlers[xmlns][name][typ+ns].remove(pack)
        except ValueError: pass

    def RegisterDefaultHandler(self,handler): self._defaultHandler=handler
    def RegisterEventHandler(self,handler): self._eventHandler=handler

    def returnStanzaHandler(self,conn,stanza):
        if stanza.getType() in ['get','set']:
            conn.send(Error(stanza,ERR_FEATURE_NOT_IMPLEMENTED))

    def RegisterCycleHandler(self,handler):
        if handler not in self._cycleHandlers: self._cycleHandlers.append(handler)

    def UnregisterCycleHandler(self,handler):
        if handler in self._cycleHandlers: self._cycleHandlers.remove(handler)

    def Event(self,realm,event,data):
        if self._eventHandler: self._eventHandler(realm,event,data)

    def dispatch(self,stanza,session=None):
        if not session: session=self
        session.Stream._mini_dom=None
        name=stanza.getName()

        if name=='features': session.Stream.features=stanza

        xmlns=stanza.getNamespace()
        if not self.handlers.has_key(xmlns):
            self.DEBUG("Unknown namespace: " + xmlns,'warn')
            xmlns='unknown'
        if not self.handlers[xmlns].has_key(name):
            self.DEBUG("Unknown stanza: " + name,'warn')
            name='unknown'
        else:
            self.DEBUG("Got %s stanza"%name, 'ok')

        if stanza.__class__.__name__=='Node': stanza=self.handlers[xmlns][name][type](node=stanza)

        typ=stanza.getType()
        if not typ: typ=''
        stanza.props=stanza.getProperties()
        ID=stanza.getID()

        session.DEBUG("Dispatching %s stanza with type->%s props->%s id->%s"%(name,typ,stanza.props,ID),'ok')

        list=['default']                                                     # we will use all handlers:
        if self.handlers[xmlns][name].has_key(typ): list.append(typ)                # from very common...
        for prop in stanza.props:
            if self.handlers[xmlns][name].has_key(prop): list.append(prop)
            if typ and self.handlers[xmlns][name].has_key(typ+prop): list.append(typ+prop)  # ...to very particular

        chain=self.handlers[xmlns]['default']['default']
        for key in list:
            if key: chain = chain + self.handlers[xmlns][name][key]

        output=''
        if session._expected.has_key(ID):
            session._expected[ID]=stanza
            user=0
            session.DEBUG("Expected stanza arrived!",'ok')
        else: user=1
        for handler in chain:
            if user or handler['system']:
                try:
                    handler['func'](session,stanza)
                except Exception, typ:
                    if typ.__class__.__name__<>'NodeProcessed': raise
                    user=0
        if user and self._defaultHandler: self._defaultHandler(session,stanza)

    def WaitForResponse(self, ID, timeout=DefaultTimeout):
        self._expected[ID]=None
        has_timed_out=0
        abort_time=time.time() + timeout
        self.DEBUG("Waiting for ID:%s with timeout %s..." % (ID,timeout),'wait')
        while not self._expected[ID]:
            if not self.Process(0.04):
                self._owner.lastErr="Disconnect"
                return None
            if time.time() > abort_time:
                self._owner.lastErr="Timeout"
                return None
        response=self._expected[ID]
        del self._expected[ID]
        if response.getErrorCode():
            self._owner.lastErrNode=response
            self._owner.lastErr=response.getError()
            self._owner.lastErrCode=response.getErrorCode()
        return response

    def SendAndWaitForResponse(self, stanza, timeout=DefaultTimeout):
        return self.WaitForResponse(self.send(stanza),timeout)

    def send(self,stanza):
        if type(stanza) in [type(''), type(u'')]: return self._owner_send(stanza)
        _ID=stanza.getID()
        if not _ID:
            global ID
            ID+=1
            _ID=`ID`
            stanza.setID(_ID)
        if self._owner._registered_name and not stanza.getAttr('from'): stanza.setAttr('from',self._owner._registered_name)
        self._owner_send(stanza)
        return _ID

    def disconnect(self):
        self._owner_send('</stream:stream>')
        while self.Process(1): pass
