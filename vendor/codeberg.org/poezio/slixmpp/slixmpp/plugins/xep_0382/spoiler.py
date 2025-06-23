# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp import JID
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0382 import stanza
from slixmpp.stanza import Message


class XEP_0382(BasePlugin):
    '''XEP-0382: Spoiler Messages'''

    name = 'xep_0382'
    description = 'Spoiler Messages'
    dependencies = {'xep_0030'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        Message.sub_interfaces.add('spoiler')

    def session_bind(self, jid: JID):
        self.xmpp['xep_0030'].add_feature(stanza.NS)

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)
        Message.sub_interfaces.remove('spoiler')
