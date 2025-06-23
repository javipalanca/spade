# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Iterable

from slixmpp import JID
from slixmpp.plugins import BasePlugin
from slixmpp.stanza import Message
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream.handler import Callback

from slixmpp.plugins.xep_0444 import stanza


class XEP_0444(BasePlugin):
    """
    XEP-0444: Message Reactions.

    If the python-emoji library is present, setting emojis as reactions will
    be checked against known emoji, and trying to set non-emoji characters
    as reactions will raise a ``ValueError``. This behavior can be disabled
    by passing ``all_chars=True`` to the ``Reaction.set_value()`` call.
    """
    name = 'xep_0444'
    description = 'XEP-0444: Message Reactions'
    dependencies = {'xep_0030', 'xep_0334'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self):
        self.xmpp.register_handler(Callback(
            'Reaction received',
            StanzaPath("message/reactions"),
            self._handle_reactions,
        ))
        register_stanza_plugin(Message, stanza.Reactions)
        register_stanza_plugin(stanza.Reactions, stanza.Reaction, iterable=True)

    def session_bind(self, event):
        self.xmpp['xep_0030'].add_feature(stanza.NS)

    def plugin_end(self):
        self.xmpp.remove_handler('Reaction received')
        self.xmpp['xep_0030'].del_feature(feature=stanza.NS)

    def _handle_reactions(self, message: Message):
        self.xmpp.event('reactions', message)

    def send_reactions(self, to: JID, to_id: str, reactions: Iterable[str], *, store=True):
        """Send reactions related to a message"""
        msg = self.xmpp.make_message(mto=to)
        self.set_reactions(msg, to_id, reactions)
        if store:
            msg.enable('store')
        msg.send()

    @staticmethod
    def set_reactions(message: Message, to_id: str, reactions: Iterable[str]):
        """Add reactions to a Message object."""
        message['reactions']['id'] = to_id
        for reaction in reactions:
            reaction_stanza = stanza.Reaction()
            reaction_stanza['value'] = reaction
            message['reactions'].append(reaction_stanza)
