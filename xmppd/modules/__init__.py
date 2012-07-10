# $Id: __init__.py,v 1.4 2004/10/23 08:58:45 snakeru Exp $

import os
#from psyco.classes import *

#for m in os.listdir('modules'):
#    if m[:2]=='__' or m[-3:]<>'.py': continue
#    exec "import "+m[:-3]

import jep0078,roster,config,message,router,db_fake,muc,stream,dialback,oob,jep0077,pubsub,wq

addons = [
# System stuff
    config.Config,
    db_fake.AUTH,
    db_fake.DB,

# XMPP-Core
    #stream.TLS,
    stream.SASL,
    dialback.Dialback,

# XMPP-IM
    stream.Bind,
    stream.Session,
    stream.Handshake,
    router.Router,
#    privacy.Privacy,

# ROSTER -- BABY!
    roster.ROSTER,
#    roster.PRESENCE,

# MESSAGE
# Handles messages addressed to the server
    message.MessageCatcher,

# JEPs
    jep0077.IBR,
    jep0078.NSA,

    muc.MUC,
    wq.WQ,
    #webadmin.WebAdmin

    pubsub.PubSubServer,
    ]
