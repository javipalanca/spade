# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0196 import stanza
from slixmpp.plugins.xep_0196.stanza import UserGaming
from slixmpp.plugins.xep_0196.user_gaming import XEP_0196


register_plugin(XEP_0196)
