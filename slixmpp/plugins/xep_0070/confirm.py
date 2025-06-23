# Slixmpp: The Slick XMPP Library
# Copyright (C) 2015 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import asyncio
import logging
from uuid import uuid4

from slixmpp.plugins import BasePlugin
from slixmpp import Iq, Message
from slixmpp.jid import JID
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.xep_0070 import stanza, Confirm


log = logging.getLogger(__name__)


class XEP_0070(BasePlugin):

    """
    XEP-0070 Verifying HTTP Requests via XMPP
    """

    name = 'xep_0070'
    description = 'XEP-0070: Verifying HTTP Requests via XMPP'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Iq, Confirm)
        register_stanza_plugin(Message, Confirm)

        self.xmpp.register_handler(
            Callback('Confirm',
                 StanzaPath('iq@type=get/confirm'),
                 self._handle_iq_confirm))

        self.xmpp.register_handler(
            Callback('Confirm',
                 StanzaPath('message/confirm'),
                 self._handle_message_confirm))

    def plugin_end(self):
        self.xmpp.remove_handler('Confirm')
        self.xmpp['xep_0030'].del_feature(feature='http://jabber.org/protocol/http-auth')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature('http://jabber.org/protocol/http-auth')

    def ask_confirm(self, jid, id, url, method, *, ifrom=None, message=None):
        jid = JID(jid)
        if jid.resource:
            stanza = self.xmpp.Iq()
            stanza['type'] = 'get'
        else:
            stanza = self.xmpp.Message()
            stanza['thread'] = uuid4().hex
        stanza['from'] = ifrom
        stanza['to'] = jid
        stanza['confirm']['id'] = id
        stanza['confirm']['url'] = url
        stanza['confirm']['method'] = method
        if not jid.resource:
            if message is not None:
                stanza['body'] = message.format(id=id, url=url, method=method)
            stanza.send()
            fut = asyncio.Future()
            fut.set_result(stanza)
            return fut
        else:
            return stanza.send()

    def _handle_iq_confirm(self, iq):
        self.xmpp.event('http_confirm_iq', iq)
        self.xmpp.event('http_confirm', iq)

    def _handle_message_confirm(self, message):
        self.xmpp.event('http_confirm_message', message)
        self.xmpp.event('http_confirm', message)
