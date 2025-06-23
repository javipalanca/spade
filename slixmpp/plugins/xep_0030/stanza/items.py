# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Iterable,
    Optional,
    Set,
    Tuple,
)
from slixmpp import JID
from slixmpp.xmlstream import (
    ElementBase,
    ET,
    register_stanza_plugin,
)


class DiscoItem(ElementBase):
    name = 'item'
    namespace = 'http://jabber.org/protocol/disco#items'
    plugin_attrib = name
    interfaces = {'jid', 'node', 'name'}

    def get_node(self) -> Optional[str]:
        """Return the item's node name or ``None``."""
        return self._get_attr('node', None)

    def get_name(self) -> Optional[str]:
        """Return the item's human readable name, or ``None``."""
        return self._get_attr('name', None)


class DiscoItems(ElementBase):

    """
    Example disco#items stanzas:

    .. code-block:: xml

        <iq type="get">
          <query xmlns="http://jabber.org/protocol/disco#items" />
        </iq>

        <iq type="result">
          <query xmlns="http://jabber.org/protocol/disco#items">
            <item jid="chat.example.com"
                  node="xmppdev"
                  name="XMPP Dev" />
            <item jid="chat.example.com"
                  node="slixdev"
                  name="Slixmpp Dev" />
          </query>
        </iq>

    """

    name = 'query'
    namespace = 'http://jabber.org/protocol/disco#items'
    plugin_attrib = 'disco_items'
    #: Stanza Interface:
    #:
    #: - ``node``: The name of the node to either
    #:   query or return info from.
    #: - ``items``: A list of 3-tuples, where each tuple contains
    #:   the JID, node, and name of an item.
    #:
    interfaces = {'node', 'items'}

    # Cache items
    _items: Set[Tuple[JID, Optional[str]]]

    def setup(self, xml: Optional[ET.ElementTree] = None):
        """
        Populate the stanza object using an optional XML object.

        Overrides ElementBase.setup

        Caches item information.

        :param xml: Use an existing XML object for the stanza's values.
        """
        ElementBase.setup(self, xml)
        self._items = {item[0:2] for item in self['items']}

    def add_item(self, jid: JID, node: Optional[str] = None,
                 name: Optional[str] = None):
        """
        Add a new item element. Each item is required to have a
        JID, but may also specify a node value to reference
        non-addressable entitities.

        :param jid: The JID for the item.
        :param node: Optional additional information to reference
                     non-addressable items.
        :param name: Optional human readable name for the item.
        """
        if (jid, node) not in self._items:
            self._items.add((jid, node))
            item = DiscoItem(parent=self)
            item['jid'] = jid
            item['node'] = node
            item['name'] = name
            self.iterables.append(item)
            return True
        return False

    def del_item(self, jid: JID, node: Optional[str] = None) -> bool:
        """
        Remove a single item.

        :param jid: JID of the item to remove.
        :param node: Optional extra identifying information.
        """
        if (jid, node) in self._items:
            for item_xml in self.xml.findall('{%s}item' % self.namespace):
                item = (item_xml.attrib['jid'],
                        item_xml.attrib.get('node', None))
                if item == (jid, node):
                    self.xml.remove(item_xml)
                    return True
        return False

    def get_items(self) -> Set[DiscoItem]:
        """Return all items."""
        items = set()
        for item in self['substanzas']:
            if isinstance(item, DiscoItem):
                items.add((item['jid'], item['node'], item['name']))
        return items

    def set_items(self, items: Iterable[DiscoItem]):
        """
        Set or replace all items. The given items must be in a
        list or set where each item is a tuple of the form:

            (jid, node, name)

        :param items: A series of items in tuple format.
        """
        self.del_items()
        for item in items:
            jid, node, name = item
            self.add_item(jid, node, name)

    def del_items(self):
        """Remove all items."""
        self._items = set()
        items = [i for i in self.iterables if isinstance(i, DiscoItem)]
        for item in items:
            self.xml.remove(item.xml)
            self.iterables.remove(item)


register_stanza_plugin(DiscoItems, DiscoItem, iterable=True)
