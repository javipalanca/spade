# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Optional

from slixmpp import JID, Message
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0425 import stanza


class XEP_0425(BasePlugin):
    '''XEP-0425: Moderated Message Retraction'''

    name = 'xep_0425'
    description = 'XEP-0425: Moderated Message Retraction'
    dependencies = {'xep_0424', 'xep_0421'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        self.xmpp.register_handler(Callback(
            'Moderated Message',
            StanzaPath('message/retract/moderated'),
            self._handle_moderated,
        ))

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(feature=stanza.NS)

    def _handle_moderated(self, message: Message):
        if message['type'] == 'groupchat':
            self.xmpp.event('moderated_message', message)

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)

    async def moderate(self, room: JID, id: str, reason: str = '', *,
                       ifrom: Optional[JID] = None, **iqkwargs):
        iq = self.xmpp.make_iq_set(ito=room.bare, ifrom=ifrom)
        iq['moderate']['id'] = id
        iq['moderate']['reason'] = reason
        iq['moderate'].enable('retract')
        await iq.send(**iqkwargs)
