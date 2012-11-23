# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# JEP0078 (Non-SASL authenticaion) for xmppd.py

# $Id: jep0078.py,v 1.6 2004/10/23 09:22:44 snakeru Exp $

from xmpp import *
from xmppd import *
#from xmppd import SESSION_OPENED
import hashlib


class NSA(PlugIn):
    NS = NS_AUTH

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.getAuthInfoHandler, 'get', NS_AUTH)
        server.Dispatcher.RegisterHandler('iq', self.setAuthInfoHandler, 'set', NS_AUTH)

    def getAuthInfoHandler(self, session, stanza):
        servername = stanza['to']
        if servername and servername not in self._owner.servernames:
            session.send(Error(stanza, ERR_ITEM_NOT_FOUND))
        else:
            iq = stanza.buildReply('result')
            iq.T.query.NT.username = stanza.T.query.T.username
            iq.T.query.NT.password
            iq.T.query.NT.digest
            iq.T.query.NT.resource
            session.send(iq)
        raise NodeProcessed

    def setAuthInfoHandler(self, session, stanza):
        if not stanza['to']:
            stanza['to'] = session.ourname
        servername = stanza['to'].getDomain()
        username = stanza.T.query.T.username.getData().lower()
        password = self._owner.AUTH.getpassword(username, servername)
        if password is not None:
            digest = hashlib.sha1(session.ID + password).hexdigest()
        try:
            query_password = stanza.T.query.T.password.getData()
        except:
            query_password = None

        if servername not in self._owner.servernames:
            session.send(Error(stanza, ERR_ITEM_NOT_FOUND))
        elif session.ourname == servername \
            and password \
            and (query_password == password
                 or stanza.T.query.T.digest.getData() == digest) \
                and stanza.T.query.T.resource.getData():
            session.send(stanza.buildReply('result'))
            fulljid = "%s@%s/%s" % (username, servername, stanza.T.query.T.resource.getData())
            session.peer = fulljid
            s = self._owner.deactivatesession(fulljid)
            if s:
                s.terminate_stream(STREAM_CONFLICT)
            session.set_session_state(SESSION_OPENED)
        else:
            session.send(stanza.buildReply('error'))
        raise NodeProcessed
