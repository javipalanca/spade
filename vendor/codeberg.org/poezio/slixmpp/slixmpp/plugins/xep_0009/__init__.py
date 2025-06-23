
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Dann Martens (TOMOTON).
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0009 import stanza
from slixmpp.plugins.xep_0009.rpc import XEP_0009
from slixmpp.plugins.xep_0009.stanza import RPCQuery, MethodCall, MethodResponse


register_plugin(XEP_0009)
