# slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
import logging
from typing import Optional

from slixmpp import Message, JID
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.xep_0333 import stanza, Markable, Received, Displayed, Acknowledged

log = logging.getLogger(__name__)

class XEP_0333(BasePlugin):

    name = 'xep_0333'
    description = 'XEP-0333: Chat Markers'
    stanza = stanza
    dependencies = {'xep_0030'}

    def plugin_init(self):
        register_stanza_plugin(Message, Markable)
        register_stanza_plugin(Message, Received)
        register_stanza_plugin(Message, Displayed)
        register_stanza_plugin(Message, Acknowledged)

        self.xmpp.register_handler(
            Callback('Received Chat Marker',
                StanzaPath('message/received'),
                self._handle_received))
        self.xmpp.register_handler(
            Callback('Displayed Chat Marker',
                StanzaPath('message/displayed'),
                self._handle_displayed))
        self.xmpp.register_handler(
            Callback('Acknowledged Chat Marker',
                StanzaPath('message/acknowledged'),
                self._handle_acknowledged))

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(stanza.NS)

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)

    def _handle_received(self, message):
        self.xmpp.event('marker_received', message)
        self.xmpp.event('marker', message)

    def _handle_displayed(self, message):
        self.xmpp.event('marker_displayed', message)
        self.xmpp.event('marker', message)

    def _handle_acknowledged(self, message):
        self.xmpp.event('marker_acknowledged', message)
        self.xmpp.event('marker', message)

    def send_marker(self, mto: JID, id: str, marker: str,
                    thread: Optional[str] = None, *,
                    mfrom: Optional[JID] = None):
        """
        Send a chat marker.

        :param JID mto: recipient of the marker
        :param str id: Identifier of the marked message
        :param str marker: Marker to send (one of
            displayed, received, or acknowledged)
        :param str thread: Message thread
        :param str mfrom: Use a specific JID to send the message
        """
        if marker not in ('displayed', 'received', 'acknowledged'):
            raise ValueError('Invalid marker: %s' % marker)
        msg = self.xmpp.make_message(mto=mto, mfrom=mfrom)
        if thread:
            msg['thread'] = thread
        msg[marker]['id'] = id
        msg.send()
