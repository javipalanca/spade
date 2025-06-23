
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0202 import stanza
from slixmpp.plugins.xep_0202.stanza import EntityTime
from slixmpp.plugins.xep_0202.time import XEP_0202


register_plugin(XEP_0202)
