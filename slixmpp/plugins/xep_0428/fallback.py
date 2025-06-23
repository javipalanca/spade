# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0428 import stanza


class XEP_0428(BasePlugin):
    '''XEP-0428: Fallback Indication'''

    name = 'xep_0428'
    description = 'XEP-0428: Fallback Indication'
    dependencies = set()
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
