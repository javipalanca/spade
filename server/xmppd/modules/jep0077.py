#!/usr/bin/python
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# In-band-registration for xmppd.py

# $Id: jep0077.py,v 1.2 2004/09/19 20:20:05 snakeru Exp $

from xmpp import *

class IBR(PlugIn):
    def plugin(self,server):
        server.Dispatcher.RegisterHandler('iq',self.getRegInfoHandler,'get',NS_REGISTER)
        server.Dispatcher.RegisterHandler('iq',self.setRegInfoHandler,'set',NS_REGISTER)

    def getRegInfoHandler(self,sess,stanza):
        name=stanza['to']
        if name not in self._owner.servernames:
            sess.send(Error(stanza,ERR_ITEM_NOT_FOUND))
        else:
            iq=stanza.buildReply('result')
            iq.T.query.T.username
            iq.T.query.T.password
            iq.T.query.T.instructions='Please specify name and password to register with'
            sess.send(iq)
        raise NodeProcessed

    def setRegInfoHandler(self,sess,stanza):
        name=stanza['to']
        if name not in self._owner.servernames:
            sess.send(Error(stanza,ERR_ITEM_NOT_FOUND))
        else:
            sess.send(Error(stanza,ERR_CONFLICT))       # dummy code for now
            """iq=stanza.buildReply('result')
            iq.T.query.T.username
            iq.T.query.T.password
            iq.T.query.T.instructions='Please specify name and password to register with'
            sess.send(iq)"""
        raise NodeProcessed
