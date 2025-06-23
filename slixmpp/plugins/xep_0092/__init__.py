
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0092 import stanza
from slixmpp.plugins.xep_0092.stanza import Version
from slixmpp.plugins.xep_0092.version import XEP_0092


register_plugin(XEP_0092)
