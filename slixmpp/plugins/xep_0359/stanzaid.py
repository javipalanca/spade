# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0359 import stanza


class XEP_0359(BasePlugin):
    '''XEP-0359: Unique and Stable Stanza IDs'''

    name = 'xep_0359'
    description = 'XEP-0359: Unique and Stable Stanza IDs'
    dependencies = set()
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
