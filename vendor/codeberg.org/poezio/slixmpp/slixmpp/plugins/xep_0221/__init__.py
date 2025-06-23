
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0221 import stanza
from slixmpp.plugins.xep_0221.stanza import Media, URI
from slixmpp.plugins.xep_0221.media import XEP_0221


register_plugin(XEP_0221)
