"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

from __future__ import annotations

import hashlib
import logging

from asyncio import Future
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Union,
    TYPE_CHECKING,
)

from slixmpp.stanza import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin, JID
from slixmpp.plugins.xep_0084.stanza import Data, MetaData, Pointer
from slixmpp.plugins.xep_0084 import stanza

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class AvatarMetadataItem(TypedDict, total=False):
    bytes: int
    id: str
    type: str
    height: int
    width: int
    url: str

MetadataItems = Union[
    AvatarMetadataItem,
    List[AvatarMetadataItem],
    Set[AvatarMetadataItem]
]


log = logging.getLogger(__name__)


class XEP_0084(BasePlugin):

    name = 'xep_0084'
    description = 'XEP-0084: User Avatar'
    dependencies = {'xep_0163', 'xep_0060'}
    stanza = stanza

    def plugin_init(self):
        pubsub_stanza = self.xmpp['xep_0060'].stanza
        register_stanza_plugin(pubsub_stanza.Item, Data)
        register_stanza_plugin(pubsub_stanza.EventItem, Data)

        self.xmpp['xep_0060'].map_node_event(Data.namespace, 'avatar_data')

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=MetaData.namespace)
        self.xmpp['xep_0163'].remove_interest(MetaData.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('avatar_metadata', MetaData)

    def generate_id(self, data) -> str:
        return hashlib.sha1(data).hexdigest()

    def retrieve_avatar(self, jid: JID, id: str, **pubsubkwargs) -> Future:
        """Retrieve an avatar.

        :param jid: JID of the entity to get the avatar from.
        :param id: Identifier of the item containing the avatar.
        """
        return self.xmpp['xep_0060'].get_item(
            jid,
            Data.namespace,
            id,
            **pubsubkwargs
        )

    def publish_avatar(self, data: bytes, **pubsubkwargs) -> Future:
        """Publish an avatar.

        :param data: The avatar, in bytes representation.
        """
        payload = Data()
        payload['value'] = data
        return self.xmpp['xep_0163'].publish(
            payload,
            id=self.generate_id(data),
            **pubsubkwargs
        )

    def publish_avatar_metadata(self, items: Optional[MetadataItems] = None,
                                pointers: Optional[Iterable[Pointer]] = None,
                                **pubsubkwargs) -> Future:
        """Publish avatar metadata.

        :param items: Metadata items to store
        :param pointers: Optional pointers
        """
        metadata = MetaData()
        if items is None:
            items = []
        if not isinstance(items, (list, set)):
            items = [items]
        for info in items:
            metadata.add_info(info['id'], info['type'], info['bytes'],
                    height=info.get('height', ''),
                    width=info.get('width', ''),
                    url=info.get('url', ''))

        if pointers is not None:
            for pointer in pointers:
                metadata.add_pointer(pointer)

        return self.xmpp['xep_0163'].publish(
            metadata,
            id=info['id'],
            **pubsubkwargs
        )

    def stop(self, **pubsubkwargs) -> Future:
        """
        Clear existing avatar metadata information to stop notifications.
        """
        metadata = MetaData()
        return self.xmpp['xep_0163'].publish(
            metadata,
            node=MetaData.namespace,
            **pubsubkwargs
        )
