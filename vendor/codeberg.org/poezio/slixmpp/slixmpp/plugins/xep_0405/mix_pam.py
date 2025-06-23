# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    List,
    Optional,
    Set,
    Tuple,
)

from slixmpp import JID, Iq
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins import BasePlugin
from slixmpp.stanza.roster import RosterItem
from slixmpp.plugins.xep_0405 import stanza
from slixmpp.plugins.xep_0369 import stanza as mix_stanza


BASE_NODES = [
    'urn:xmpp:mix:nodes:messages',
    'urn:xmpp:mix:nodes:participants',
    'urn:xmpp:mix:nodes:info',
]


class XEP_0405(BasePlugin):
    '''XEP-0405: MIX-PAM'''

    name = 'xep_0405'
    description = 'XEP-0405: MIX-PAM'
    dependencies = {'xep_0369'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()

    async def check_server_capability(self) -> bool:
        """Check if the server is MIX-PAM capable"""
        result = await self.xmpp.plugin['xep_0030'].get_info(jid=self.xmpp.boundjid.bare)
        features = result['disco_info']['features']
        return stanza.NS in features

    async def join_channel(self, room: JID, nick: str, subscribe: Optional[Set[str]] = None, *,
                           ito: Optional[JID] = None,
                           ifrom: Optional[JID] = None,
                           **iqkwargs) -> Set[str]:
        """
        Join a MIX channel.

        :param JID room: JID of the MIX channel
        :param str nick: Desired nickname on that channel
        :param Set[str] subscribe: Set of nodes to subscribe to when joining.
            If empty, all nodes will be subscribed by default.

        :rtype: Set[str]
        :return: The nodes that failed to subscribe, if any
        """
        if subscribe is None:
            subscribe = set(BASE_NODES)
        if ito is None:
            ito = self.xmpp.boundjid.bare
        iq = self.xmpp.make_iq_set(ito=ito, ifrom=ifrom)
        iq['client_join']['channel'] = room
        iq['client_join']['mix_join']['nick'] = nick
        for node in subscribe:
            sub = mix_stanza.Subscribe()
            sub['node'] = node
            iq['client_join']['mix_join'].append(sub)
        result = await iq.send(**iqkwargs)
        result_nodes = {sub['node'] for sub in result['client_join']['mix_join']}
        return subscribe.difference(result_nodes)

    async def leave_channel(self, room: JID, *,
                            ito: Optional[JID] = None,
                            ifrom: Optional[JID] = None,
                            **iqkwargs) -> Iq:
        """"
        Leave a MIX channel
        :param JID room: JID of the channel to leave
        """
        if ito is None:
            ito = self.xmpp.boundjid.bare
        iq = self.xmpp.make_iq_set(ito=ito, ifrom=ifrom)
        iq['client_leave']['channel'] = room
        iq['client_leave'].enable('mix_leave')
        return await iq.send(**iqkwargs)

    async def get_mix_roster(self, *,
                            ito: Optional[JID] = None,
                            ifrom: Optional[JID] = None,
                            **iqkwargs) -> Tuple[List[RosterItem], List[RosterItem]]:
        """
        Get the annotated roster, with MIX channels.

        :return: A tuple of (contacts, mix channels) as RosterItem elements
        """
        iq = self.xmpp.make_iq_get(ito=ito, ifrom=ifrom)
        iq['roster'].enable('annotate')
        result = await iq.send(**iqkwargs)
        self.xmpp.event("roster_update", result)
        contacts = []
        mix = []
        for item in result['roster']:
            channel = item.get_plugin('channel', check=True)
            if channel:
                mix.append(item)
            else:
                contacts.append(item)
        return (contacts, mix)
