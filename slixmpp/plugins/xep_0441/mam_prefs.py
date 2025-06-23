# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission
import logging

from asyncio import Future
from typing import (
    List,
    Optional,
    Tuple,
)

from slixmpp import JID
from slixmpp.types import MAMDefault
from slixmpp.stanza import Iq
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0441 import stanza


log = logging.getLogger(__name__)


class XEP_0441(BasePlugin):

    """
    XEP-0441: Message Archive Management Preferences
    """

    name = 'xep_0441'
    description = 'XEP-0441: Message Archive Management Preferences'
    dependencies = {'xep_0313'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Iq, stanza.Preferences)

    async def get_preferences(self, **iqkwargs
                              ) -> Tuple[MAMDefault, List[JID], List[JID]]:
        """Get the current MAM preferences.

        :returns: A tuple of MAM preferences with (default, always, never)
        """
        ifrom = iqkwargs.pop('ifrom', None)
        ito = iqkwargs.pop('ito', None)
        iq = self.xmpp.make_iq_get(ito=ito, ifrom=ifrom)
        iq['type'] = 'get'
        query_id = iq['id']
        iq['mam_prefs']['query_id'] = query_id
        result = await iq.send(**iqkwargs)
        return (
            result['mam_prefs']['default'],
            result['mam_prefs']['always'],
            result['mam_prefs']['never']
        )

    def set_preferences(self, default: Optional[MAMDefault] = 'roster',
                        always: Optional[List[JID]] = None,
                        never: Optional[List[JID]] = None, *,
                        ito: Optional[JID] = None, ifrom: Optional[JID] = None,
                        **iqkwargs) -> Future:
        """Set MAM Preferences.

        The server answer MAY contain different items.

        :param default: Default behavior (one of 'always', 'never', 'roster').
        :param always: List of JIDs whose messages will always be stored.
        :param never: List of JIDs whose messages will never be stored.
        """
        iq = self.xmpp.make_iq_set(ito=ito, ifrom=ifrom)
        iq['mam_prefs']['default'] = default
        iq['mam_prefs']['always'] = always
        iq['mam_prefs']['never'] = never
        return iq.send(**iqkwargs)
