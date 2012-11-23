#!/usr/bin/python
# -*- coding: utf-8 -*-
from xmpp import *
import time
import sha
import xmlrpclib


def routerHandler(self, session, stanza):

    clients = {}

    cl = Client('127.0.0.1', 5223, None)

    if not cl.connect(server=('127.0.0.1', 5223)):
        raise IOError('Can not connect to server.')

    if not cl.auth('_internal_rerouter', 'test', our_resource):
        raise IOError('Can not auth with server.')

    cl.RegisterNamespaceHandler(NS_CLIENT, self.routerHandler)

    cl.RegisterNamespaceHandler(NS_SERVER, self.routerHandler)

    cl.sendInitPresence()

    cl.Process(1)

    if not cl.isConnected():
        cl.reconnectAndReauth()
