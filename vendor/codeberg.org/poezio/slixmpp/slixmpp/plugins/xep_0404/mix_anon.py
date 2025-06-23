# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Dict,
    Optional,
    Set,
    Tuple,
)

from slixmpp import JID, Message, Iq
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.plugins.xep_0404 import stanza
from slixmpp.plugins.xep_0004.stanza import Form


NODES = [
    'urn:xmpp:mix:nodes:jidmap',
]


class XEP_0404(BasePlugin):
    '''XEP-0404: MIX JID Hidden Channels'''

    name = 'xep_0404'
    description = 'XEP-0404: MIX-ANON'
    dependencies = {'xep_0369'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()

    async def get_anon_raw(self, channel: JID, *,
                            ifrom: Optional[JID] = None, **pubsubkwargs) -> Iq:
        """
        Get the jid-participant mapping result (raw).
        :param JID channel: MIX channel JID
        """
        return await self.xmpp['xep_0030'].get_items(
            channel.bare,
            ifrom=ifrom,
            **pubsubkwargs
        )

    async def get_anon_by_jid(self, channel: JID, *,
                              ifrom: Optional[JID] = None, **pubsubkwargs) -> Dict[JID, str]:
        """
        Get the jid-participant mapping, by JID

        :param JID channel: MIX channel JID
        """
        raw = await self.get_anon_raw(channel, ifrom=ifrom, **pubsubkwargs)
        mapping = {}
        for item in raw['pubsub']['items']:
            mapping[item['anon_participant']['jid']] = item['id']
        return mapping

    async def get_anon_by_id(self, channel: JID, *,
                             ifrom: Optional[JID] = None, **pubsubkwargs) -> Dict[str, JID]:
        """
        Get the jid-participant mapping, by participant id

        :param JID channel: MIX channel JID
        """
        raw = await self.get_anon_raw(channel, ifrom=ifrom, **pubsubkwargs)
        mapping = {}
        for item in raw['pubsub']['items']:
            mapping[item['id']] = item['anon_participant']['jid']
        return mapping

    async def get_preferences(self, channel: JID, *,
                              ifrom: Optional[JID] = None, **iqkwargs) -> Form:
        """
        Get channel preferences with default values.
        :param JID channel: MIX channel JID
        """
        iq = self.xmpp.make_iq_get(ito=channel.bare, ifrom=ifrom)
        iq.enable('user_preference')
        prefs_stanza = await iq.send(**iqkwargs)
        return prefs_stanza['user_preference']['form']

    async def set_preferences(self, channel: JID, form: Form, *,
                              ifrom: Optional[JID] = None, **iqkwargs) -> Form:
        """
        Set channel preferences
        :param JID channel: MIX channel JID
        :param Form form: A 0004 form with updated preferences
        """
        iq = self.xmpp.make_iq_set(ito=channel.bare, ifrom=ifrom)
        iq['user_preference']['form'] = form
        prefs_result = await iq.send(**iqkwargs)
        return prefs_result['user_preference']['form']
