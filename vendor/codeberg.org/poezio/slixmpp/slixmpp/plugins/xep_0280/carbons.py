
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
import logging

from asyncio import Future
from typing import Optional

from slixmpp import JID
from slixmpp.stanza import Message, Iq
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0280 import stanza


log = logging.getLogger(__name__)


class XEP_0280(BasePlugin):

    """
    XEP-0280 Message Carbons

    Events triggered by this plugin:

    - :term:`carbon_received`
    - :term:`carbon_sent`
    """

    name = 'xep_0280'
    description = 'XEP-0280: Message Carbons'
    dependencies = {'xep_0030', 'xep_0297'}
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_handler(
            Callback('Carbon Received',
                     StanzaPath('message/carbon_received'),
                     self._handle_carbon_received))
        self.xmpp.register_handler(
            Callback('Carbon Sent',
                     StanzaPath('message/carbon_sent'),
                     self._handle_carbon_sent))

        register_stanza_plugin(Message, stanza.ReceivedCarbon)
        register_stanza_plugin(Message, stanza.SentCarbon)
        register_stanza_plugin(Message, stanza.PrivateCarbon)
        register_stanza_plugin(Iq, stanza.CarbonEnable)
        register_stanza_plugin(Iq, stanza.CarbonDisable)

        register_stanza_plugin(stanza.ReceivedCarbon,
                               self.xmpp['xep_0297'].stanza.Forwarded)
        register_stanza_plugin(stanza.SentCarbon,
                               self.xmpp['xep_0297'].stanza.Forwarded)

    def plugin_end(self):
        self.xmpp.remove_handler('Carbon Received')
        self.xmpp.remove_handler('Carbon Sent')
        self.xmpp.plugin['xep_0030'].del_feature(feature='urn:xmpp:carbons:2')

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature('urn:xmpp:carbons:2')

    def _handle_carbon_received(self, msg: Message):
        if msg['from'].bare == self.xmpp.boundjid.bare:
            self.xmpp.event('carbon_received', msg)

    def _handle_carbon_sent(self, msg: Message):
        if msg['from'].bare == self.xmpp.boundjid.bare:
            self.xmpp.event('carbon_sent', msg)

    def enable(self, ifrom: Optional[JID] = None, **iqkwargs) -> Future:
        """Enable carbons."""
        iq = self.xmpp.make_iq_set(ifrom=ifrom)
        iq.enable('carbon_enable')
        return iq.send(**iqkwargs)

    def disable(self, ifrom: Optional[JID] = None, **iqkwargs) -> Future:
        """Disable carbons."""
        iq = self.xmpp.make_iq_set(ifrom=ifrom)
        iq.enable('carbon_disable')
        return iq.send(**iqkwargs)
