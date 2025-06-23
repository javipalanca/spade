
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0016 import stanza
from slixmpp.plugins.xep_0016.stanza import Privacy
from slixmpp.plugins.xep_0016.privacy import XEP_0016


register_plugin(XEP_0016)
