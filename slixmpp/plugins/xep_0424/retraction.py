# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Optional

from slixmpp import JID, Message
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0424 import stanza


DEFAULT_FALLBACK = (
    'This person attempted to retract a previous message, but your client '
    'does not support it.'
)


class XEP_0424(BasePlugin):
    '''XEP-0424: Message Retraction'''

    name = 'xep_0424'
    description = 'XEP-0424: Message Retraction'
    dependencies = {'xep_0422', 'xep_0030', 'xep_0359', 'xep_0428', 'xep_0334'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        self.xmpp.register_handler(Callback(
            "Message Retracted",
            StanzaPath("message/retract"),
            self._handle_retract_message,
        ))

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(feature=stanza.NS)

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)

    def _handle_retract_message(self, message: Message):
        self.xmpp.event('message_retract', message)

    def send_retraction(self, mto: JID, id: str, mtype: str = 'chat',
                        include_fallback: bool = True,
                        fallback_text: Optional[str] = None, *,
                        mfrom: Optional[JID] = None):
        """
        Send a message retraction

        :param JID mto: The JID to retract the message from
        :param str id: Message ID to retract
        :param str mtype: Message type
        :param bool include_fallback: Whether to include a fallback body
        :param Optional[str] fallback_text: The content of the fallback
                                            body. None will set the default value.
        """
        if fallback_text is None:
            fallback_text = DEFAULT_FALLBACK
        msg = self.xmpp.make_message(mto=mto, mtype=mtype, mfrom=mfrom)
        if include_fallback:
            msg['body'] = fallback_text
            msg.enable('fallback')
        msg['retract']['id'] = id
        msg.enable('store')
        msg.send()
