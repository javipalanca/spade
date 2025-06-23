# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

from datetime import datetime
from slixmpp import JID, Iq
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0369 import stanza
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import MatchXPath

try:
    from typing import TypedDict
    InfoType = TypedDict(
        'InfoType',
        {
            'Name': str,
            'Description': str,
            'Contact': Optional[List[JID]],
            'modified': datetime
        },
        total=False,
    )
except ImportError:
    # Placeholder until we drop python < 3.8
    InfoType = Dict[str, Any]


BASE_NODES = [
    'urn:xmpp:mix:nodes:messages',
    'urn:xmpp:mix:nodes:participants',
    'urn:xmpp:mix:nodes:info',
]


class XEP_0369(BasePlugin):
    '''XEP-0369: MIX-CORE'''

    name = 'xep_0369'
    description = 'XEP-0369: MIX-CORE'
    dependencies = {'xep_0030', 'xep_0060', 'xep_0082', 'xep_0004'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        self.xmpp.register_handler(
            Callback(
                "MIX message received",
                MatchXPath('{%s}message[@type="groupchat"]/{%s}mix' % (
                    self.xmpp.default_ns, self.namespace
                )),
                self._handle_mix_message,
            )
        )

    def _handle_mix_message(self, message):
        self.xmpp.event('mix_message', message)

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(stanza.NS)
        self.xmpp.plugin['xep_0060'].map_node_event(
            'urn:xmpp:mix:nodes:participants',
            'mix_participant_info',
        )
        self.xmpp.plugin['xep_0060'].map_node_event(
            'urn:xmpp:mix:nodes:info',
            'mix_channel_info',
        )

    def plugin_end(self):
        self.xmpp.plugin['xep_0030'].del_feature(feature=stanza.NS)
        node_map = self.xmpp.plugin['xep_0060'].node_event_map
        if 'urn:xmpp:mix:nodes:info' in node_map:
            del node_map['urn:xmpp:mix:nodes:info']
        if 'urn:xmpp:mix:nodes:participants' in node_map:
            del node_map['urn:xmpp:mix:nodes:participants']

    async def get_channel_info(self, channel: JID) -> InfoType:
        """"
        Get the contents of the channel info node.

        :param channel: The MIX channel
        :returns: a dict containing the last modified time and form contents
                  (Name, Description, Contact per the spec, YMMV)
        """
        info = await self.xmpp['xep_0060'].get_items(channel, 'urn:xmpp:mix:nodes:info')
        for item in info['pubsub']['items']:
            time = item['id']
            fields = item['form'].get_values()
            del fields['FORM_TYPE']
            fields['modified'] = self.xmpp['xep_0082'].parse(time)
            contact = fields.get('Contact')
            if contact:
                if isinstance(contact, str):
                    contact = [contact]
                elif isinstance(contact, list):
                    contact = [JID(cont) for cont in contact]
                fields['Contact'] = contact
            return fields

    async def join_channel(self, channel: JID, nick: str, subscribe: Optional[Set[str]] = None, *,
                           ifrom: Optional[JID] = None, **iqkwargs) -> Set[str]:
        """
        Join a MIX channel.

        :param JID channel: JID of the MIX channel
        :param str nick: Desired nickname on that channel
        :param Set[str] subscribe: Set of notes to subscribe to when joining.
            If empty, all nodes will be subscribed by default.

        :rtype: Set[str]
        :return: The nodes that failed to subscribe, if any
        """
        if not subscribe:
            subscribe = set(BASE_NODES)
        iq = self.xmpp.make_iq_set(ito=channel, ifrom=ifrom)
        iq['mix_join']['nick'] = nick
        for node in subscribe:
            sub = stanza.Subscribe()
            sub['node'] = node
            iq['mix_join']['subscribe'].append(sub)
        result = await iq.send(**iqkwargs)
        result_nodes = {sub['node'] for sub in result['mix_join']}
        return result_nodes.difference(subscribe)

    async def update_subscription(self, channel: JID,
                                  subscribe: Optional[Set[str]] = None,
                                  unsubscribe: Optional[Set[str]] = None, *,
                                  ifrom: Optional[JID] = None, **iqkwargs) -> Tuple[Set[str], Set[str]]:
        """
        Update a MIX channel subscription.

        :param JID channel: JID of the MIX channel
        :param Set[str] subscribe: Set of notes to subscribe to additionally.
        :param Set[str] unsubscribe: Set of notes to unsubscribe from.
        :rtype: Tuple[Set[str], Set[str]]
        :return: A tuple containing the set of nodes that failed to subscribe
            and the set of nodes that failed to unsubscribe.
        """
        if not subscribe and not unsubscribe:
            raise ValueError("No nodes were provided.")
        unsubscribe = unsubscribe or set()
        subscribe = subscribe or set()
        iq = self.xmpp.make_iq_set(ito=channel, ifrom=ifrom)
        iq.enable('mix_updatesub')
        for node in subscribe:
            sub = stanza.Subscribe()
            sub['node'] = node
            iq['mix_updatesub'].append(sub)
        for node in unsubscribe:
            unsub = stanza.Unsubscribe()
            unsub['node'] = node
            iq['mix_updatesub'].append(unsub)
        result = await iq.send(**iqkwargs)
        for item in result['mix_updatesub']:
            if isinstance(item, stanza.Subscribe):
                subscribe.discard(item['node'])
            elif isinstance(item, stanza.Unsubscribe):
                unsubscribe.discard(item['node'])
        return (subscribe, unsubscribe)

    async def leave_channel(self, channel: JID, *,
                            ifrom: Optional[JID] = None, **iqkwargs) -> None:
        """"
        Leave a MIX channel
        :param JID channel: JID of the channel to leave
        """
        iq = self.xmpp.make_iq_set(ito=channel, ifrom=ifrom)
        iq.enable('mix_leave')
        await iq.send(**iqkwargs)

    async def set_nick(self, channel: JID, nick: str, *,
                       ifrom: Optional[JID] = None, **iqkwargs) -> str:
        """
        Set your nick on a channel. The returned nick MAY be different
        from the one provided, depending on service configuration.
        :param JID channel: MIX channel JID
        :param str nick: desired nick
        :rtype: str
        :return: The nick saved on the MIX channel
        """

        iq = self.xmpp.make_iq_set(ito=channel, ifrom=ifrom)
        iq['mix_setnick']['nick'] = nick
        result = await iq.send(**iqkwargs)
        result_nick = result['mix_setnick']['nick']
        return result_nick

    async def can_create_channel(self, service: JID) -> bool:
        """
        Check if the current user can create a channel on the MIX service

        :param JID service: MIX service jid
        :rtype: bool
        """
        results_stanza = await self.xmpp['xep_0030'].get_info(service.server)
        features = results_stanza['disco_info']['features']
        return 'urn:xmpp:mix:core:1#create-channel' in features

    async def create_channel(self, service: JID, channel: Optional[str] = None, *,
                             ifrom: Optional[JID] = None, **iqkwargs) -> str:
        """
        Create a MIX channel.

        :param JID service: MIX service JID
        :param Optional[str] channel: Channel name (or leave empty to let
            the service generate it)
        :returns: The channel name, as created by the service
        """
        if '#' in channel:
            raise ValueError("A channel name cannot contain hashes")
        iq = self.xmpp.make_iq_set(ito=service.server, ifrom=ifrom)
        iq.enable('mix_create')
        if channel is not None:
            iq['mix_create']['channel'] = channel
        result = await iq.send(**iqkwargs)
        return result['mix_create']['channel']

    async def destroy_channel(self, channel: JID, *,
                              ifrom: Optional[JID] = None, **iqkwargs):
        """
        Destroy a MIX channel.
        :param JID channel: MIX channelJID
        """
        iq = self.xmpp.make_iq_set(ito=channel.server, ifrom=ifrom)
        iq['mix_destroy'] = channel.user
        await iq.send(**iqkwargs)

    async def list_mix_nodes(self, channel: JID,
                             ifrom: Optional[JID] = None, **discokwargs) -> Set[str]:
        """
        List mix nodes for a channel.

        :param JID channel: The MIX channel
        :returns: List of nodes available
        """
        result = await self.xmpp['xep_0030'].get_items(
            channel,
            node='mix',
            ifrom=ifrom,
            **discokwargs,
        )
        nodes = set()
        for item in result['disco_items']:
            nodes.add(item['node'])
        return nodes

    async def list_participants(self, channel: JID, *,
                                ifrom: Optional[JID] = None, **pubsubkwargs) -> List[Tuple[str, str, Optional[JID]]]:
        """
        List the participants of a MIX channel
        :param JID channel: The MIX channel

        :returns: A list of tuples containing the participant id, nick, and jid (if available)
        """
        info = await self.xmpp['xep_0060'].get_items(
            channel,
            'urn:xmpp:mix:nodes:participants',
            ifrom=ifrom,
            **pubsubkwargs
        )
        participants = list()
        for item in info['pubsub']['items']:
            identifier = item['id']
            nick = item['mix_participant']['nick']
            jid = item['mix_participant']['jid'] or None
            participants.append(
                (identifier, nick, jid),
            )
        return participants

    async def list_channels(self, service: JID, *,
                            ifrom: Optional[JID] =None, **discokwargs) -> List[Tuple[JID, str]]:
        """
        List the channels on a MIX service

        :param JID service: MIX service JID
        :returns: A list of channels with their JID and name
        """
        results_stanza = await self.xmpp['xep_0030'].get_items(
            service.server,
            ifrom=ifrom,
            **discokwargs,
        )
        results = []
        for result in results_stanza['disco_items']:
            results.append((result['jid'], result['name']))
        return results
