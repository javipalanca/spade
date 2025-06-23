
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from asyncio import Future
from typing import Optional, Callable, List
from slixmpp import JID
from slixmpp.xmlstream import register_stanza_plugin, ElementBase
from slixmpp.plugins.base import BasePlugin, register_plugin
from slixmpp.plugins.xep_0004.stanza import Form


log = logging.getLogger(__name__)


class XEP_0223(BasePlugin):

    """
    XEP-0223: Persistent Storage of Private Data via PubSub

    If a specific pubsub node requires additional publish options, edit the
    :attr:`.node_profile` attribute of this plugin:

    .. code-block:: python

        self.xmpp.plugin["xep_0223"].node_profiles["urn:some:node"] = {
            "pubsub#max_items" = "max"
        }

    This makes :meth:`.store` add these publish options whenever it is called
    for the ``urn:some:node`` node.
    """

    name = 'xep_0223'
    description = 'XEP-0223: Persistent Storage of Private Data via PubSub'
    dependencies = {'xep_0163', 'xep_0060', 'xep_0004'}

    profile = {'pubsub#persist_items': True,
               'pubsub#access_model': 'whitelist'}
    node_profiles = dict[str, dict[str, str]]()

    def configure(self, node: str, **iqkwargs) -> Future:
        """
        Update a node's configuration to match the private storage profile.

        :param node: Node to set the configuration at.
        """
        config = self.xmpp['xep_0004'].stanza.Form()
        config['type'] = 'submit'
        config.add_field(
            var='FORM_TYPE',
            ftype='hidden',
            value='http://jabber.org/protocol/pubsub#node_config')

        for field, value in self.profile.items():
            config.add_field(var=field, value=value)

        return self.xmpp['xep_0060'].set_node_config(
            jid=None, node=node, config=config, **iqkwargs
        )

    def store(self, stanza: ElementBase, node: Optional[str] = None,
              id: Optional[str] = None, **pubsubkwargs) -> Future:
        """
        Store private data via PEP.

        This is just a (very) thin wrapper around the XEP-0060 publish()
        method to set the defaults expected by PEP.

        :param stanza:  The private content to store.
        :param node: The node to publish the content to. If not specified,
                     the stanza's namespace will be used.
        :param id: Optionally specify the ID of the item.
        :param options: Publish options to use, which will be modified to
                        fit the persistent storage option profile.
        """
        options = pubsubkwargs.pop('options', None)
        if not options:
            options = self.xmpp['xep_0004'].stanza.Form()
            options['type'] = 'submit'
            options.add_field(
                var='FORM_TYPE',
                ftype='hidden',
                value='http://jabber.org/protocol/pubsub#publish-options')

        fields = options['fields']
        profile = self.profile | self.node_profiles.get(node, {})
        for field, value in profile.items():
            if field not in fields:
                options.add_field(var=field)
            options.get_fields()[field]['value'] = value

        pubsubkwargs['options'] = options
        return self.xmpp['xep_0163'].publish(stanza, node, id=id, **pubsubkwargs)

    def retrieve(self, node: str, id: Optional[str] = None,
                 item_ids: Optional[List[str]] = None, **iqkwargs) -> Future:
        """
        Retrieve private data via PEP.

        This is just a (very) thin wrapper around the XEP-0060 publish()
        method to set the defaults expected by PEP.

        :param node: The node to retrieve content from.
        :param id: Optionally specify the ID of the item.
        :param item_ids: Specify a group of IDs. If id is also specified, it
                         will be included in item_ids.
        """
        if item_ids is None:
            item_ids = []
        if id is not None:
            item_ids.append(id)

        return self.xmpp['xep_0060'].get_items(
            jid=None, node=node,
            item_ids=item_ids,
            **iqkwargs
        )


register_plugin(XEP_0223)
