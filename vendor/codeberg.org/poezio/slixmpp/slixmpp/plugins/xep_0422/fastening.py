# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0422 import stanza


class XEP_0422(BasePlugin):
    '''XEP-0422: Message Fastening'''

    name = 'xep_0422'
    description = 'XEP-0422: Message Fastening'
    dependencies = {'xep_0030'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(feature=stanza.NS)

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)
