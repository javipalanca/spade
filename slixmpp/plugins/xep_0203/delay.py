
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.stanza import Message, Presence
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0203 import stanza


class XEP_0203(BasePlugin):

    """
    XEP-0203: Delayed Delivery

    XMPP stanzas are sometimes withheld for delivery due to the recipient
    being offline, or are resent in order to establish recent history as
    is the case with MUCS. In any case, it is important to know when the
    stanza was originally sent, not just when it was last received.

    Also see <http://www.xmpp.org/extensions/xep-0203.html>.
    """

    name = 'xep_0203'
    description = 'XEP-0203: Delayed Delivery'
    dependencies = set()
    stanza = stanza

    def plugin_init(self):
        """Start the XEP-0203 plugin."""
        register_stanza_plugin(Message, stanza.Delay)
        register_stanza_plugin(Presence, stanza.Delay)
