#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id: xsend.py,v 1.1 2004/06/20 09:45:09 snakeru Exp $
import sys
import os
import xmpp

if len(sys.argv) < 2:
    print "Syntax: xsend JID text"
    sys.exit(0)

tojid = sys.argv[1]
text = ' '.join(sys.argv[2:])

jidparams = {}
if os.access(os.environ['HOME'] + '/.xsend', os.R_OK):
    for ln in open(os.environ['HOME'] + '/.xsend').readlines():
        key, val = ln.strip().split('=', 1)
        jidparams[key.lower()] = val
for mandatory in ['jid', 'password']:
    if mandatory not in jidparams.keys():
        open(os.environ['HOME'] + '/.xsend', 'w').write('#JID=romeo@montague.net\n#PASSWORD=juliet\n')
        print 'Please point ~/.xsend config file to valid JID for sending messages.'
        sys.exit(0)

jid = xmpp.protocol.JID(jidparams['jid'])
cl = xmpp.Client(jid.getDomain(), debug=[])

cl.connect()
cl.auth(jid.getNode(), jidparams['password'])

#cl.SendInitialPresence()
cl.send(xmpp.protocol.Message(tojid, text))

#cl.disconnect()
