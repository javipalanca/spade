
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
from typing import (
    List,
    Optional,
    Union,
)
from asyncio import Future

from slixmpp import JID
from slixmpp.stanza import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin, ElementBase
from slixmpp.plugins.xep_0049 import stanza, PrivateXML


log = logging.getLogger(__name__)


class XEP_0049(BasePlugin):

    name = 'xep_0049'
    description = 'XEP-0049: Private XML Storage'
    dependencies = {}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Iq, PrivateXML)

    def register(self, stanza):
        register_stanza_plugin(PrivateXML, stanza, iterable=True)

    def store(self, data: Union[List[ElementBase], ElementBase], ifrom: Optional[JID] = None, **iqkwargs) -> Future:
        """Store data in Private XML Storage.

        :param data: An XML element or list of xml element to store.
        """
        iq = self.xmpp.make_iq_set(ifrom=ifrom)

        if not isinstance(data, list):
            data = [data]
        for elem in data:
            iq['private'].append(elem)

        return iq.send(**iqkwargs)

    def retrieve(self, name: str, ifrom: Optional[JID] = None, **iqkwargs) -> Future:
        """Get previously stored data from Private XML Storage.

        :param name: Name of the payload to retrieve (slixmpp plugin attribute)
        """
        iq = self.xmpp.make_iq_get(ifrom=ifrom)
        iq['private'].enable(name)
        return iq.send(**iqkwargs)
