
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from asyncio import Future

from slixmpp import JID
from typing import Dict, List, Optional, Callable
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0152 import stanza, Reachability
from slixmpp.plugins.xep_0004 import Form


log = logging.getLogger(__name__)


class XEP_0152(BasePlugin):

    """
    XEP-0152: Reachability Addresses
    """

    name = 'xep_0152'
    description = 'XEP-0152: Reachability Addresses'
    dependencies = {'xep_0163'}
    stanza = stanza

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Reachability.namespace)
        self.xmpp['xep_0163'].remove_interest(Reachability.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('reachability', Reachability)

    def publish_reachability(self, addresses: List[Dict[str, str]],
                             **pubsubkwargs) -> Future:
        """
        Publish alternative addresses where the user can be reached.

        :param addresses: A list of dictionaries containing the URI and
                          optional description for each address.
        """
        if not isinstance(addresses, (list, tuple)):
            addresses = [addresses]
        reach = Reachability()
        for address in addresses:
            if not hasattr(address, 'items'):
                address = {'uri': address}

            addr = stanza.Address()
            for key, val in address.items():
                addr[key] = val
            reach.append(addr)
        return self.xmpp['xep_0163'].publish(
            reach,
            node=Reachability.namespace,
            **pubsubkwargs
        )

    def stop(self, **pubsubkwargs) -> Future:
        """
        Clear existing user activity information to stop notifications.
        """
        reach = Reachability()
        return self.xmpp['xep_0163'].publish(
            reach,
            node=Reachability.namespace,
            **pubsubkwargs
        )
