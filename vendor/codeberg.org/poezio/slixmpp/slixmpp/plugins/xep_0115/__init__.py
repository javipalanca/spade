
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0115.stanza import Capabilities
from slixmpp.plugins.xep_0115.static import StaticCaps
from slixmpp.plugins.xep_0115.caps import XEP_0115


register_plugin(XEP_0115)
