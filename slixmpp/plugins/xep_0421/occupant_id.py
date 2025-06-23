
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 "Maxime “pep” Buquet <pep@bouah.net>"
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp import JID, Message, Presence
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0421 import stanza
from slixmpp.plugins.xep_0421.stanza import OccupantId


class XEP_0421(BasePlugin):
    '''XEP-0421: Anonymous unique occupant identifiers for MUCs'''

    name = 'xep_0421'
    description = 'XEP-0421: Anonymous unique occupant identifiers for MUCs'
    dependencies = {'xep_0030', 'xep_0045'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        # XXX: This should be MucMessage. Someday..
        register_stanza_plugin(Message, OccupantId)
        register_stanza_plugin(Presence, OccupantId)

    async def has_feature(self, jid: JID) -> bool:
        info = await self.xmpp['xep_0030'].get_info(jid)
        return self.namespace in info.get_features()
