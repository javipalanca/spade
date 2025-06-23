
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from asyncio import Future
from typing import Optional

import slixmpp
from slixmpp import Iq, JID
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0004 import Form
from slixmpp.plugins.xep_0030 import DiscoInfo
from slixmpp.plugins.xep_0128 import StaticExtendedDisco


class XEP_0128(BasePlugin):

    """
    XEP-0128: Service Discovery Extensions

    Allow the use of data forms to add additional identity
    information to disco#info results.

    Also see <http://www.xmpp.org/extensions/xep-0128.html>.

    :var disco: A reference to the XEP-0030 plugin.
    :var static: Object containing the default set of static
                 node handlers.
    """

    name = 'xep_0128'
    description = 'XEP-0128: Service Discovery Extensions'
    dependencies = {'xep_0030', 'xep_0004'}

    def plugin_init(self):
        """Start the XEP-0128 plugin."""
        self._disco_ops = ['set_extended_info',
                           'add_extended_info',
                           'del_extended_info']

        register_stanza_plugin(DiscoInfo, Form, iterable=True)

        self.disco = self.xmpp['xep_0030']
        self.static = StaticExtendedDisco(self.disco.static)

        self.disco.set_extended_info = self.set_extended_info
        self.disco.add_extended_info = self.add_extended_info
        self.disco.del_extended_info = self.del_extended_info

        for op in self._disco_ops:
            self.api.register(getattr(self.static, op), op, default=True)

    def set_extended_info(self, jid=None, node=None, **kwargs) -> Future:
        """
        Set additional, extended identity information to a node.

        Replaces any existing extended information.

        .. versionchanged:: 1.8.0
            This function now returns a Future.

        :param jid: The JID to modify.
        :param node: The node to modify.
        :param data: Either a form, or a list of forms to use
                     as extended information, replacing any
                     existing extensions.
        """
        return self.api['set_extended_info'](jid, node, None, kwargs)

    def add_extended_info(self, jid=None, node=None, **kwargs) -> Future:
        """
        Add additional, extended identity information to a node.

        .. versionchanged:: 1.8.0
            This function now returns a Future.

        :param jid: The JID to modify.
        :param node: The node to modify.
        :param data: Either a form, or a list of forms to add
                     as extended information.
        """
        return self.api['add_extended_info'](jid, node, None, kwargs)

    def del_extended_info(self, jid: Optional[JID] = None,
                          node: Optional[str] = None, **kwargs) -> Future:
        """
        Remove all extended identity information to a node.

        .. versionchanged:: 1.8.0
            This function now returns a Future.

        :param jid: The JID to modify.
        :param node: The node to modify.
        """
        return self.api['del_extended_info'](jid, node, None, kwargs)
