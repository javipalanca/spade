import xmppd
from  modules import *

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
    jep0077.IBR,
    jep0078.NSA,

# Mine
    #ch.CH,
    #dummy.dummyClass,
    ]

# Transport-level flags
SOCKET_UNCONNECTED  =0
SOCKET_ALIVE        =1
SOCKET_DEAD         =2
# XML-level flags
STREAM__NOT_OPENED =1
STREAM__OPENED     =2
STREAM__CLOSING    =3
STREAM__CLOSED     =4
# XMPP-session flags
SESSION_NOT_AUTHED =1
SESSION_AUTHED     =2
SESSION_BOUND      =3
SESSION_OPENED     =4

