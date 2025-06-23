# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from __future__ import annotations

import logging

from typing import (
    Optional,
    Any,
    Dict,
    Tuple,
    TYPE_CHECKING,
    Union,
    Collection,
)

from slixmpp import BaseXMPP, JID
from slixmpp.stanza import Iq
from slixmpp.types import TypedDict, OptJidStr, OptJid
from slixmpp.exceptions import XMPPError, IqError, IqTimeout
from slixmpp.plugins.xep_0030 import DiscoInfo, DiscoItems


log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from slixmpp.plugins.xep_0030 import XEP_0030


class NodeType(TypedDict):
    info: DiscoInfo
    items: DiscoItems


NodesType = Dict[
    Tuple[str, str, str],
    NodeType
]


class StaticDisco:

    """
    While components will likely require fully dynamic handling
    of service discovery information, most clients and simple bots
    only need to manage a few disco nodes that will remain mostly
    static.

    StaticDisco provides a set of node handlers that will store
    static sets of disco info and items in memory.

    :var nodes: A dictionary mapping (JID, node) tuples to a dict
                containing a disco#info and a disco#items stanza.
    :var xmpp: The main Slixmpp object.
    :var disco: The instance of the XEP-0030 plugin.
    """

    def __init__(self, xmpp: 'BaseXMPP', disco: 'XEP_0030'):
        """
        Create a static disco interface. Sets of disco#info and
        disco#items are maintained for every given JID and node
        combination. These stanzas are used to store disco
        information in memory without any additional processing.

        :param xmpp: The main Slixmpp object.
        :param disco: The XEP-0030 plugin.
        """
        self.nodes: NodesType = {}
        self.xmpp: BaseXMPP = xmpp
        self.disco: 'XEP_0030' = disco

    def add_node(self, jid: OptJidStr = None, node: Optional[str] = None,
                 ifrom: OptJidStr = None) -> NodeType:
        if jid is None:
            node_jid = self.xmpp.boundjid.full
        elif isinstance(jid, JID):
            node_jid = jid.full
        else:
            node_jid = jid
        if ifrom is None:
            node_ifrom = ''
        elif isinstance(ifrom, JID):
            node_ifrom = ifrom.full
        else:
            node_ifrom = ifrom
        if node is None:
            node = ''
        if (node_jid, node, node_ifrom) not in self.nodes:
            node_dict: NodeType = {
                'info': DiscoInfo(),
                'items': DiscoItems(),
            }
            node_dict['info']['node'] = node
            node_dict['items']['node'] = node
            self.nodes[(node_jid, node, node_ifrom)] = node_dict
        return self.nodes[(node_jid, node, node_ifrom)]

    def get_node(self, jid: OptJidStr = None, node: Optional[str] = None,
                 ifrom: OptJidStr = None) -> NodeType:
        if jid is None:
            node_jid = self.xmpp.boundjid.full
        elif isinstance(jid, JID):
            node_jid = jid.full
        else:
            node_jid = jid
        if node is None:
            node = ''
        if ifrom is None:
            node_ifrom = ''
        elif isinstance(ifrom, JID):
            node_ifrom = ifrom.full
        else:
            node_ifrom = ifrom
        if (node_jid, node, node_ifrom) not in self.nodes:
            self.add_node(node_jid, node, node_ifrom)
        return self.nodes[(node_jid, node, node_ifrom)]

    def node_exists(self, jid: OptJidStr = None, node: Optional[str] = None,
                    ifrom: OptJidStr = None) -> bool:
        if jid is None:
            node_jid = self.xmpp.boundjid.full
        elif isinstance(jid, JID):
            node_jid = jid.full
        else:
            node_jid = jid
        if node is None:
            node = ''
        if ifrom is None:
            node_ifrom = ''
        elif isinstance(ifrom, JID):
            node_ifrom = ifrom.full
        else:
            node_ifrom = ifrom
        return (node_jid, node, node_ifrom) in self.nodes

    # =================================================================
    # Node Handlers
    #
    # Each handler accepts four arguments: jid, node, ifrom, and data.
    # The jid and node parameters together determine the set of info
    # and items stanzas that will be retrieved or added. Additionally,
    # the ifrom value allows for cached results when results vary based
    # on the requester's JID. The data parameter is a dictionary with
    # additional parameters that will be passed to other calls.
    #
    # This implementation does not allow different responses based on
    # the requester's JID, except for cached results. To do that,
    # register a custom node handler.

    async def supports(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                       data: Any) -> Optional[bool]:
        """
        Check if a JID supports a given feature.

        The data parameter may provide:

        :param feature: The feature to check for support.
        :param local:   If true, then the query is for a JID/node
                        combination handled by this Slixmpp instance and
                        no stanzas need to be sent.
                        Otherwise, a disco stanza must be sent to the
                        remove JID to retrieve the info.
        :param cached:  If true, then look for the disco info data from
                        the local cache system. If no results are found,
                        send the query as usual. The self.use_cache
                        setting must be set to true for this option to
                        be useful. If set to false, then the cache will
                        be skipped, even if a result has already been
                        cached. Defaults to false.
        """
        feature = data.get('feature', None)

        data = {'local': data.get('local', False),
                'cached': data.get('cached', True)}

        if not feature:
            return False

        try:
            info = await self.disco.get_info(jid=jid, node=node,
                                             ifrom=ifrom, **data)
            info = self.disco._wrap(ifrom, jid, info, True)
            features = info['disco_info']['features']
            return feature in features
        except IqError:
            return False
        except IqTimeout:
            return None

    async def has_identity(self, jid: OptJid, node: Optional[str],
                           ifrom: OptJid, data: Dict[str, Any]
                           ) -> Optional[bool]:
        """
        Check if a JID has a given identity.

        The data parameter may provide:

        :param category: The category of the identity to check.
        :param itype:    The type of the identity to check.
        :param lang:     The language of the identity to check.
        :param local:    If true, then the query is for a JID/node
                         combination handled by this Slixmpp instance and
                         no stanzas need to be sent.
                         Otherwise, a disco stanza must be sent to the
                         remove JID to retrieve the info.
        :param cached:   If true, then look for the disco info data from
                         the local cache system. If no results are found,
                         send the query as usual. The self.use_cache
                         setting must be set to true for this option to
                         be useful. If set to false, then the cache will
                         be skipped, even if a result has already been
                         cached. Defaults to false.
        """
        identity = (data.get('category', None),
                    data.get('itype', None),
                    data.get('lang', None))

        data = {'local': data.get('local', False),
                'cached': data.get('cached', True)}

        try:
            info = await self.disco.get_info(jid=jid, node=node,
                                             ifrom=ifrom, **data)
            info = self.disco._wrap(ifrom, jid, info, True)

            def trunc(i):
                return (i[0], i[1], i[2])
            return identity in map(trunc, info['disco_info']['identities'])
        except IqError:
            return False
        except IqTimeout:
            return None

    def get_info(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                 data: Any) -> Optional[DiscoInfo]:
        """
        Return the stored info data for the requested JID/node combination.

        The data parameter is not used.
        """
        if not self.node_exists(jid, node):
            if not node:
                return DiscoInfo()
            else:
                raise XMPPError(condition='item-not-found')
        else:
            return self.get_node(jid, node)['info']

    def set_info(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                 data: DiscoInfo):
        """
        Set the entire info stanza for a JID/node at once.

        The data parameter is a disco#info substanza.
        """
        new_node = self.add_node(jid, node)
        new_node['info'] = data

    def del_info(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                 data: Any):
        """
        Reset the info stanza for a given JID/node combination.

        The data parameter is not used.
        """
        if self.node_exists(jid, node):
            self.get_node(jid, node)['info'] = DiscoInfo()

    def get_items(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                  data: Any) -> Optional[DiscoItems]:
        """
        Return the stored items data for the requested JID/node combination.

        The data parameter is not used.
        """
        if not self.node_exists(jid, node):
            if not node:
                return DiscoItems()
            else:
                raise XMPPError(condition='item-not-found')
        else:
            return self.get_node(jid, node)['items']

    def set_items(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                  data: Dict[str, Collection[Tuple]]):
        """
        Replace the stored items data for a JID/node combination.

        The data parameter may provide:
            items -- A set of items in tuple format.
        """
        items = data.get('items', set())
        new_node = self.add_node(jid, node)
        new_node['items']['items'] = items

    def del_items(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                  data: Any):
        """
        Reset the items stanza for a given JID/node combination.

        The data parameter is not used.
        """
        if self.node_exists(jid, node):
            self.get_node(jid, node)['items'] = DiscoItems()

    def add_identity(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                     data: Dict[str, Optional[str]]):
        """
        Add a new identity to the JID/node combination.

        The data parameter may provide:

        :param category: The general category to which the agent belongs.
        :param itype: A more specific designation with the category.
        :param name: Optional human readable name for this identity.
        :param lang: Optional standard xml:lang value.
        """
        new_node = self.add_node(jid, node)
        new_node['info'].add_identity(
                data.get('category', ''),
                data.get('itype', ''),
                data.get('name', None),
                data.get('lang', None))

    def set_identities(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                       data: Dict[str, Collection[str]]):
        """
        Add or replace all identities for a JID/node combination.

        The data parameter should include:

        :param identities: A list of identities in tuple form:
                           (category, type, name, lang)
        """
        identities = data.get('identities', set())
        new_node = self.add_node(jid, node)
        new_node['info']['identities'] = identities

    def del_identity(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                     data: Dict[str, Optional[str]]):
        """
        Remove an identity from a JID/node combination.

        The data parameter may provide:

        :param category: The general category to which the agent belonged.
        :param itype: A more specific designation with the category.
        :param name: Optional human readable name for this identity.
        :param lang: Optional, standard xml:lang value.
        """
        if self.node_exists(jid, node):
            self.get_node(jid, node)['info'].del_identity(
                    data.get('category', ''),
                    data.get('itype', ''),
                    data.get('name', None),
                    data.get('lang', None))

    def del_identities(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                       data: Any):
        """
        Remove all identities from a JID/node combination.

        The data parameter is not used.
        """
        if self.node_exists(jid, node):
            del self.get_node(jid, node)['info']['identities']

    def add_feature(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                    data: Dict[str, str]):
        """
        Add a feature to a JID/node combination.

        The data parameter should include:

        :param feature: The namespace of the supported feature.
        """
        new_node = self.add_node(jid, node)
        new_node['info'].add_feature(
                data.get('feature', ''))

    def set_features(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                     data: Dict[str, Collection[str]]):
        """
        Add or replace all features for a JID/node combination.

        The data parameter should include:

        :param features: The new set of supported features.
        """
        features = data.get('features', set())
        new_node = self.add_node(jid, node)
        new_node['info']['features'] = features

    def del_feature(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                    data: Dict[str, str]):
        """
        Remove a feature from a JID/node combination.

        The data parameter should include:

        :param feature: The namespace of the removed feature.
        """
        if self.node_exists(jid, node):
            self.get_node(jid, node)['info'].del_feature(
                    data.get('feature', ''))

    def del_features(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                     data: Any):
        """
        Remove all features from a JID/node combination.

        The data parameter is not used.
        """
        if not self.node_exists(jid, node):
            return
        del self.get_node(jid, node)['info']['features']

    def add_item(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                 data: Dict[str, str]):
        """
        Add an item to a JID/node combination.

        The data parameter may include:

        :param ijid: The JID for the item.
        :param inode: Optional additional information to reference
                      non-addressable items.
        :param name: Optional human readable name for the item.
        """
        new_node = self.add_node(jid, node)
        new_node['items'].add_item(
                data.get('ijid', ''),
                node=data.get('inode', ''),
                name=data.get('name', ''))

    def del_item(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                 data: Dict[str, str]):
        """
        Remove an item from a JID/node combination.

        The data parameter may include:

        :param ijid: JID of the item to remove.
        :param inode: Optional extra identifying information.
        """
        if self.node_exists(jid, node):
            self.get_node(jid, node)['items'].del_item(
                    data.get('ijid', ''),
                    node=data.get('inode', None))

    def cache_info(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                   data: Union[Iq, DiscoInfo]):
        """
        Cache disco information for an external JID.

        The data parameter is the Iq result stanza
        containing the disco info to cache, or
        the disco#info substanza itself.
        """
        if isinstance(data, Iq):
            info = data['disco_info']
        else:
            info = data

        new_node = self.add_node(jid, node, ifrom)
        new_node['info'] = info

    def get_cached_info(self, jid: OptJid, node: Optional[str], ifrom: OptJid,
                        data: Any) -> Optional[DiscoInfo]:
        """
        Retrieve cached disco info data.

        The data parameter is not used.
        """
        if not self.node_exists(jid, node, ifrom):
            return None
        return self.get_node(jid, node, ifrom)['info']
