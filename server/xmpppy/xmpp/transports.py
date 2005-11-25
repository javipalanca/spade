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

# $Id: transports.py,v 1.14 2004/09/19 12:28:31 snakeru Exp $

import socket,select,base64,dispatcher
from simplexml import ustr
from client import PlugIn
from protocol import *

class error:
    def __init__(self,comment):
        self._comment=comment

    def __str__(self):
        return self._comment

class TCPsocket(PlugIn):
    """Must be plugged into some object to work properly"""
    def __init__(self, server=None):
        PlugIn.__init__(self)
        self.DBG_LINE='socket'
        self._exported_methods=[self.send,self.disconnect]
        self._server = server

    def plugin(self, owner):
        if not self._server: self._server=(self._owner.Server,5222)
        if not self.connect(self._server): return
        self._owner.Connection=self
        self._owner.RegisterDisconnectHandler(self.disconnected)
        return 'ok'

    def getHost(self): return self._server[0]
    def getPort(self): return self._server[1]

    def connect(self,server=None):
        try:
            if not server: server=self._server
            self._sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect(server)
            self._send=self._sock.sendall
            self._recv=self._sock.recv
            self.DEBUG("Successfully connected to remote host %s"%`server`,'start')
            return 'ok'
        except: pass

    def plugout(self):
        self._owner.DeregisterDisconnectHandler(self.disconnected)
        self.shutdown()
        del self._owner.Connection

    def receive(self):
        """Reads all pending incoming data. Calls owner's disconnected() method if appropriate."""
        try: received = self._recv(1024)
        except: received = ''

        while select.select([self._sock],[],[],0)[0]:
            try: add = self._recv(1024)
            except: add=''
            received +=add
            if not add: break

        if len(received): # length of 0 means disconnect
            self.DEBUG(received,'got')
        else:
            self.DEBUG('Socket error while receiving data','error')
            self._owner.disconnected()
        return received

    def send(self,raw_data):
        """Writes raw outgoing data. Blocks until done.
           If supplied data is unicode string, treating it as utf-8 encoded."""
        if type(raw_data)==type(u''): raw_data = raw_data.encode('utf-8')
        elif type(raw_data)<>type(''): raw_data = ustr(raw_data).encode('utf-8')
        try:
            self._send(raw_data)
            self.DEBUG(raw_data,'sent')
        except:
            self.DEBUG("Socket error while sending data",'error')
            self._owner.disconnected()

    def pending_data(self,timeout=0):
        return select.select([self._sock],[],[],timeout)[0]

    def disconnect(self):
        """Close the socket"""
        self.DEBUG("Closing socket",'stop')
        self._sock.close()

    def disconnected(self):
        """Called when a Network Error or disconnection occurs.
        Designed to be overidden"""
        self.DEBUG("Socket operation failed",'error')

DBG_CONNECT_PROXY='CONNECTproxy'
class HTTPPROXYsocket(TCPsocket):
    def __init__(self,proxy,server=None):
        TCPsocket.__init__(self,server)
        self._proxy=proxy

    def plugin(self, owner):
        owner.debug_flags.append(DBG_CONNECT_PROXY)
        return TCPsocket.plugin(self,owner)

    def connect(self,dupe=None):
        if not TCPsocket.connect(self,(self._proxy['host'],self._proxy['port'])): return
        self.DEBUG("Proxy server contacted, performing authentification",'start')
        connector = ['CONNECT %s:%s HTTP/1.0'%self._server,
            'Proxy-Connection: Keep-Alive',
            'Pragma: no-cache',
            'Host: %s:%s'%self._server,
            'User-Agent: HTTPPROXYsocket/v0.1']
        if self._proxy.has_key('user') and self._proxy.has_key('password'):
            credentials = '%s:%s'%(self._proxy['user'],self._proxy['password'])
            credentials = base64.encodestring(credentials).strip()
            connector.append('Proxy-Authorization: Basic '+credentials)
        connector.append('\r\n')
        self.send('\r\n'.join(connector))
        reply = self.receive().replace('\r','')
        try: proto,code,desc=reply.split('\n')[0].split(' ',2)
        except: raise error('Invalid proxy reply')
        if code<>'200':
            self.DEBUG('Invalid proxy reply: %s %s %s'%(proto,code,desc),'error')
            self._owner.disconnected()
            return
        while reply.find('\n\n') == -1: reply += self.receive().replace('\r','')
        self.DEBUG("Authentification successfull. Jabber server contacted.",'ok')
        return 'ok'

    def DEBUG(self,text,severity):
        return self._owner.DEBUG(DBG_CONNECT_PROXY,text,severity)

class TLS(PlugIn):
    def PlugIn(self,owner,now=0):
        if owner.__dict__.has_key('TLS'): return  # Already enabled.
        PlugIn.PlugIn(self,owner)
        DBG_LINE='TLS'
        if now: return self._startSSL()
        if self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else: self._owner.RegisterHandlerOnce('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        self.starttls=None

    def plugout(self,owner,now=0):
        self._owner.UnregisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        self._owner.UnregisterHandlerOnce('proceed',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.UnregisterHandlerOnce('failure',self.StartTLSHandler,xmlns=NS_TLS)

    def FeaturesHandler(self, conn, feats):
        if not feats.getTag('starttls',namespace=NS_TLS):
            self.DEBUG("TLS unsupported by remote server.",'warn')
            return
        self.DEBUG("TLS supported by remote server. Requesting TLS start.",'ok')
        self._owner.RegisterHandlerOnce('proceed',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.RegisterHandlerOnce('failure',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.Connection.send('<starttls xmlns="%s"/>'%NS_TLS)
        raise NodeProcessed

    def _startSSL(self):
        tcpsock=self._owner.Connection
        tcpsock._sslObj    = socket.ssl(tcpsock._sock, None, None)
        tcpsock._sslIssuer = tcpsock._sslObj.issuer()
        tcpsock._sslServer = tcpsock._sslObj.server()
        tcpsock._recv = tcpsock._sslObj.read
        tcpsock._send = tcpsock._sslObj.write
        self.starttls='success'

    def StartTLSHandler(self, conn, starttls):
        if starttls.getNamespace()<>NS_TLS: return
        self.starttls=starttls.getName()
        if self.starttls=='failure':
            self.DEBUG("Got starttls responce: "+self.starttls,'error')
            return
        self.DEBUG("Got starttls proceed responce. Switching to SSL...",'ok')
        self._startSSL()
        self._owner.Dispatcher.PlugOut()
        dispatcher.Dispatcher().PlugIn(self._owner)
