
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0047 import stanza
from slixmpp.plugins.xep_0047.stanza import Open, Close, Data
from slixmpp.plugins.xep_0047.stream import IBBytestream
from slixmpp.plugins.xep_0047.ibb import XEP_0047


register_plugin(XEP_0047)
