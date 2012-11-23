#!/usr/bin/python
# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# In-band-registration for xmppd.py

# $Id: jep0077.py,v 1.2 2004/09/19 20:20:05 snakeru Exp $

from xmpp import *


class IBR(PlugIn):
    NS = NS_REGISTER

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.getRegInfoHandler, 'get', NS_REGISTER)
        server.Dispatcher.RegisterHandler('iq', self.setRegInfoHandler, 'set', NS_REGISTER)

    def getRegInfoHandler(self, sess, stanza):
        name = stanza['to']
        if name and name not in self._owner.servernames:
            sess.send(Error(stanza, ERR_ITEM_NOT_FOUND))
        else:
            iq = stanza.buildReply('result')
            iq.T.query.NT.username
            iq.T.query.NT.password
            iq.T.query.NT.name
            iq.T.query.NT.instructions = 'Please specify name and password to register with'
            sess.send(iq)
        raise NodeProcessed

    def setRegInfoHandler(self, sess, stanza):
        domain_name = stanza['to']
        if domain_name and domain_name not in self._owner.servernames:
            sess.send(Error(stanza, ERR_ITEM_NOT_FOUND))
        else:
            #username=stanza.T.query.T.username
            #password=stanza.T.query.T.password
            try:
                name = stanza.T.query.T.name.getData()
            except:
                name = ""  # Turbo-Hack!!!
            try:
                servername = domain_name.getDomain()
            except:
                servername = self._owner.servernames[0]
            try:
                username = stanza.T.query.T.username.getData().lower()
                password = stanza.T.query.T.password.getData()
            except:
                # TODO: Implement de-registration from server
                sess.send(Error(stanza, ERR_NOT_ACCEPTABLE))
                raise NodeProcessed

            if not(self._owner.AUTH.isuser(username, servername)):
                if self._owner.DB.register_user(servername, username, password, name):
                    iq = stanza.buildReply('result')
                    sess.send(iq)
                    #self.DEBUG(str(self._owner.DB.printdb()),'info')
                else:
                    sess.send(Error(stanza, ERR_CONFLICT))
            else:
                sess.send(Error(stanza, ERR_CONFLICT))
        raise NodeProcessed
