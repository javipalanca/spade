
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0091 import stanza
from slixmpp.plugins.xep_0091.stanza import LegacyDelay
from slixmpp.plugins.xep_0091.legacy_delay import XEP_0091


register_plugin(XEP_0091)
