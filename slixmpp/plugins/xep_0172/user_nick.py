# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

from asyncio import Future
from typing import Optional, Callable
from slixmpp import JID
from slixmpp.stanza.message import Message
from slixmpp.stanza.presence import Presence
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0172 import stanza, UserNick
from slixmpp.plugins.xep_0004.stanza import Form


log = logging.getLogger(__name__)


class XEP_0172(BasePlugin):

    """
    XEP-0172: User Nickname
    """

    name = 'xep_0172'
    description = 'XEP-0172: User Nickname'
    dependencies = {'xep_0163'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, UserNick)
        register_stanza_plugin(Presence, UserNick)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=UserNick.namespace)
        self.xmpp['xep_0163'].remove_interest(UserNick.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('user_nick', UserNick)

    def publish_nick(self, nick: Optional[str] = None, **pubsubkwargs) -> Future:
        """
        Publish the user's current nick.

        :param nick: The user nickname to publish.
        """
        nickname = UserNick()
        nickname['nick'] = nick
        return self.xmpp['xep_0163'].publish(
            nickname,
            node=UserNick.namespace,
            **pubsubkwargs
        )

    def stop(self, **pubsubkwargs) -> Future:
        """
        Clear existing user nick information to stop notifications.
        """
        nick = UserNick()
        return self.xmpp['xep_0163'].publish(
            nick,
            node=UserNick.namespace,
            **pubsubkwargs
        )
