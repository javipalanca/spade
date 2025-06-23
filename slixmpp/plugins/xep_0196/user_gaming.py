# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging

from asyncio import Future
from slixmpp import JID
from typing import Optional, Callable
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0196 import stanza, UserGaming
from slixmpp.plugins.xep_0004.stanza import Form


log = logging.getLogger(__name__)


class XEP_0196(BasePlugin):

    """
    XEP-0196: User Gaming
    """

    name = 'xep_0196'
    description = 'XEP-0196: User Gaming'
    dependencies = {'xep_0163'}
    stanza = stanza

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=UserGaming.namespace)
        self.xmpp['xep_0163'].remove_interest(UserGaming.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('user_gaming', UserGaming)

    def publish_gaming(self, name: Optional[str] = None,
                       level: Optional[str] = None,
                       server_name: Optional[str] = None,
                       uri: Optional[str] = None,
                       character_name: Optional[str] = None,
                       character_profile: Optional[str] = None,
                       server_address: Optional[str] = None,
                       **pubsubkwargs) -> Future:
        """
        Publish the user's current gaming status.

        :param name: The name of the game.
        :param level: The user's level in the game.
        :param uri: A URI for the game or relevant gaming service
        :param server_name: The name of the server where the user is playing.
        :param server_address: The hostname or IP address of the server where the
                               user is playing.
        :param character_name: The name of the user's character in the game.
        :param character_profile: A URI for a profile of the user's character.
        :param options: Optional form of publish options.
        """
        gaming = UserGaming()
        gaming['name'] = name
        gaming['level'] = level
        gaming['uri'] = uri
        gaming['character_name'] = character_name
        gaming['character_profile'] = character_profile
        gaming['server_name'] = server_name
        gaming['server_address'] = server_address
        return self.xmpp['xep_0163'].publish(
            gaming,
            node=UserGaming.namespace,
            **pubsubkwargs
        )

    def stop(self, **pubsubkwargs) -> Future:
        """
        Clear existing user gaming information to stop notifications.
        """
        gaming = UserGaming()
        return self.xmpp['xep_0163'].publish(
            gaming,
            node=UserGaming.namespace,
            **pubsubkwargs
        )
