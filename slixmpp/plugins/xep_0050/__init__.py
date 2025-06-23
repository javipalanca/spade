
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0050.stanza import Command
from slixmpp.plugins.xep_0050.adhoc import XEP_0050


register_plugin(XEP_0050)
