# $Id: __init__.py,v 1.4 2004/10/23 08:58:45 snakeru Exp $

import os
#from psyco.classes import *

for m in os.listdir('modules'):
    if m[:2]=='__' or m[-3:]<>'.py': continue
    exec "import "+m[:-3]

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
    router.Router,
#    privacy.Privacy,

# JEPs
#    jep0077.IBR,
    jep0078.NSA,

# Mine
    #ch.CH,
    #dummy.dummyClass,
    ]
