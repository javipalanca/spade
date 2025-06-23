# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Optional,
    Set,
)

from slixmpp import JID, Iq
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0403 import stanza
from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.xmlstream.handler import Callback


NODES = [
    'urn:xmpp:mix:nodes:presence'
]


class XEP_0403(BasePlugin):
    '''XEP-0403: MIX-Presence'''

    name = 'xep_0403'
    description = 'XEP-0403: MIX-Presence'
    dependencies = {'xep_0369'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()

        self.xmpp.register_handler(
            Callback(
                'MIX Presence received',
                MatchXPath('{%s}presence/{%s}mix' % (self.xmpp.default_ns, stanza.NS)),
                self._handle_mix_presence,
            )
        )

    def _handle_mix_presence(self, presence):
        self.xmpp.event('mix_presence', presence)
