
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0319 import stanza
from slixmpp.plugins.xep_0319.stanza import Idle
from slixmpp.plugins.xep_0319.idle import XEP_0319


register_plugin(XEP_0319)
