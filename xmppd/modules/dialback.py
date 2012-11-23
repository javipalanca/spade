# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# Dialback module for xmppd.py

# $Id: dialback.py,v 1.2 2004/10/24 04:37:19 snakeru Exp $

from xmpp import *
from xmppd import *
import socket
import thread
import hashlib


class Dialback(PlugIn):
    """ 4. <db:result from= to= /> ->

        8.                db:verify ->
        9.                            <-  db:verify
        10.            <- db:result
        """
    NS = NS_DIALBACK

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('result', self.dialbackHandler, xmlns=NS_DIALBACK)
        server.Dispatcher.RegisterHandler('verify', self.dialbackHandler, xmlns=NS_DIALBACK)
        server.Dispatcher.RegisterHandler('features', self.FeaturesHandler, xmlns=NS_STREAMS)
        self.waitlist = {}

    def dialbackHandler(self, session, stanza):
        frm = stanza['from']
        to = stanza['to']
        name = stanza.getName()
        if to not in self._owner.servernames:
            self.DEBUG('Received dialback key for unknown server.', 'error')
            session.terminate_stream(STREAM_HOST_UNKNOWN)
        elif not frm or frm != frm.getDomain():
            self.DEBUG('Received dialback key from invalid server.', 'error')
            session.terminate_stream(STREAM_INVALID_FROM)
        elif name == 'result' and session.TYP == 'server':
            # (4) Received an dialback key. We should verify it.
            key = stanza.getData()
            self.DEBUG('Received dialback key %s (%s->%s).' % (repr(key), frm, to), 'info')
            # Now we should form a request and send it to authoritative server
            req = Node('db:verify', {'from': session.ourname, 'to': frm, 'id': session.ID}, [key])
            s = self._owner.getsession(frm)
            if not s:
                print "### db:No session for " + str(frm)
                s = self._owner.S2S(session.ourname, frm.getDomain(), slave_session=session)
            s.send(req)
            if frm in self.waitlist:
                self.waitlist[frm][1].terminate_stream(STREAM_CONFLICT)
            self.waitlist[frm] = (key, session)
        elif name == 'verify' and session.TYP == 'server':
            # (8) Received the dialback key for verification
            id = stanza['id']
            key = stanza.getData()
            self.DEBUG('Received dialback key %s for verification against id %s.' % (key, id), 'info')
            if key.strip() == hashlib.sha1(id + self._owner.ID).hexdigest():
                typ = 'valid'
            else:
                typ = 'invalid'
            rep = Node('db:verify', {'from': to, 'to': frm, 'id': id, 'type': typ})
            session.send(rep)
        elif name == 'verify' and session.TYP == 'client':
            # (9) Received the verification reply
            self.DEBUG('Received verified dialback key for id %s (%s->%s). Result is: %s.' % (stanza['id'], frm, to, stanza['type']), 'info')
            if frm in self.waitlist:
                key, s = self.waitlist[frm]
                if s.ID == stanza['id']:
                    rep = Node('db:result', {'from': to, 'to': frm, 'type': stanza['type']})
                    s.send(rep)
                    if stanza['type'] != 'valid':
                        s.terminate_stream(STREAM_NOT_AUTHORIZED)
                    else:
                        s.peer = frm
                        s.set_session_state(SESSION_AUTHED)
                else:
                    session.terminate_stream(STREAM_INVALID_ID)  # it will terminate "initial stream" also
        elif name == 'result' and session.TYP == 'client':
            # (10) Received the result. Either we will be terminated now or authorized.
            if stanza['type'] == 'valid':
                session.set_session_state(SESSION_AUTHED)
                session.push_queue()
        raise NodeProcessed

    def __call__(self, session):
        # Server connected, send request
        key = hashlib.sha1(session.ID + self._owner.ID).hexdigest()
        req = Node('db:result', {'from': session.ourname, 'to': session.peer}, [key])
        session.send(req)

    def FeaturesHandler(self, session, stanza):
        if session._session_state >= SESSION_AUTHED:
            return     # already authed. do nothing
        if session.feature_in_process:
            return                 # another feature underway. Standby
        self(session)
