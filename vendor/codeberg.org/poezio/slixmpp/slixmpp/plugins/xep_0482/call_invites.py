# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 Mathieu Pasquet
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
from slixmpp.plugins.xep_0482 import stanza


log = logging.getLogger(__name__)


class XEP_0482(BasePlugin):

    """
    XEP-0482: Call Invites

    This plugin defines the stanza elements for Call Invites, as well as new
    events:

    - `call-invite`
    - `call-reject`
    - `call-retract`
    - `call-leave`
    - `call-left`
    """

    name = 'xep_0482'
    description = 'XEP-0482: Call Invites'
    dependencies = set()
    stanza = stanza

    def plugin_init(self):
        stanza.register_plugins()

        for event in ('invite', 'reject', 'retract', 'leave', 'left'):
            self.xmpp.register_handler(
                Callback(f'Call {event}',
                         StanzaPath(f'message/call_{event}'),
                         self._handle_event))
    def _handle_event(self, message):
        for event in ('invite', 'reject', 'retract', 'leave', 'left'):
            if message.get_plugin(f'call_{event}', check=True):
                self.xmpp.event(f'call_{event}')

    def plugin_end(self):
        for event in ('invite', 'reject', 'retract', 'leave', 'left'):
            self.xmpp.remove_handler(f'Call {event}')
