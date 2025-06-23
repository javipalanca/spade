# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
import logging
from typing import Optional

from slixmpp.stanza import Message
from slixmpp.jid import JID
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0308 import stanza, Replace


log = logging.getLogger(__name__)


class XEP_0308(BasePlugin):

    """
    XEP-0308 Last Message Correction
    """

    name = 'xep_0308'
    description = 'XEP-0308: Last Message Correction'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_handler(
            Callback('Message Correction',
                     StanzaPath('message/replace'),
                     self._handle_correction))

        register_stanza_plugin(Message, Replace)

        self.xmpp.use_message_ids = True

    def plugin_end(self):
        self.xmpp.remove_handler('Message Correction')
        self.xmpp.plugin['xep_0030'].del_feature(feature=Replace.namespace)

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(Replace.namespace)

    def is_correction(self, msg: Message):
        return msg.xml.find('{%s}replace' % Replace.namespace) is not None

    def _handle_correction(self, msg: Message):
        self.xmpp.event('message_correction', msg)

    def build_correction(self, id_to_replace: str, mto: JID,
                         mfrom: Optional[JID] = None, mtype: str = 'chat',
                         mbody: str = '') -> Message:
        """
        Build a corrected message.

        :param id_to_replace: The id of the original message.
        :param mto: Recipient of the message, must be the same as the original
                    message.
        :param mfrom: Sender of the message, must be the same as the original
                      message.
        :param mtype: Type of the message, must be the send as the original
                      message.
        :param mbody: The corrected message body.
        """
        msg = self.xmpp.make_message(
            mto=mto,
            mfrom=mfrom,
            mbody=mbody,
            mtype=mtype
        )
        msg['replace']['id'] = id_to_replace
        return msg

    def correct_message(self, msg: Message, body: str) -> Message:
        """
        Send a correction to an existing message.

        :param msg: The message that must be replaced.
        :param body: The body to set in the correcting message.
        :returns: The message that was sent.
        """
        to_replace = msg['id']
        mto = msg['to']
        mfrom = msg['from']
        mtype = msg['type']
        if not to_replace:
            raise ValueError('No available ID for replacing the message')
        if not mto:
            raise ValueError('No available recipient JID')

        new = self.build_correction(
            id_to_replace=to_replace,
            mto=mto,
            mfrom=mfrom,
            mtype=mtype,
            mbody=body,
        )
        new.send()
        return new
