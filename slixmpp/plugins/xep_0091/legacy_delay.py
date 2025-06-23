
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.stanza import Message, Presence
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0091 import stanza


class XEP_0091(BasePlugin):

    """
    XEP-0091: Legacy Delayed Delivery
    """

    name = 'xep_0091'
    description = 'XEP-0091: Legacy Delayed Delivery'
    dependencies = set()
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, stanza.LegacyDelay)
        register_stanza_plugin(Presence, stanza.LegacyDelay)
