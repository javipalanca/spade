
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0095 import stanza
from slixmpp.plugins.xep_0095.stanza import SI
from slixmpp.plugins.xep_0095.stream_initiation import XEP_0095


register_plugin(XEP_0095)
