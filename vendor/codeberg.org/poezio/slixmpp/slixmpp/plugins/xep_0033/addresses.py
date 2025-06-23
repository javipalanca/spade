
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp import Message, Presence
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0033 import stanza, Addresses


class XEP_0033(BasePlugin):

    """
    XEP-0033: Extended Stanza Addressing
    """

    name = 'xep_0033'
    description = 'XEP-0033: Extended Stanza Addressing'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, Addresses)
        register_stanza_plugin(Presence, Addresses)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Addresses.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Addresses.namespace)

