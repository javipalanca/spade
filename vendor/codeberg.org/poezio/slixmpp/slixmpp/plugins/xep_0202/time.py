
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from typing import Optional

from slixmpp import JID
from slixmpp.stanza.iq import Iq
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins import BasePlugin
from slixmpp.plugins import xep_0082
from slixmpp.plugins.xep_0202 import stanza


log = logging.getLogger(__name__)


class XEP_0202(BasePlugin):

    """
    XEP-0202: Entity Time
    """

    name = 'xep_0202'
    description = 'XEP-0202: Entity Time'
    dependencies = {'xep_0030', 'xep_0082'}
    stanza = stanza
    default_config = {
        #: As a default, respond to time requests with the
        #: local time returned by XEP-0082. However, a
        #: custom function can be supplied which accepts
        #: the JID of the entity to query for the time.
        'local_time': None,
        'tz_offset': 0
    }

    def plugin_init(self):
        """Start the XEP-0202 plugin."""

        if not self.local_time:
            def default_local_time(jid):
                return xep_0082.datetime(offset=self.tz_offset)

            self.local_time = default_local_time

        self.xmpp.register_handler(
            Callback('Entity Time',
                 StanzaPath('iq@type=get/entity_time'),
                 self._handle_time_request))
        register_stanza_plugin(Iq, stanza.EntityTime)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature='urn:xmpp:time')
        self.xmpp.remove_handler('Entity Time')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature('urn:xmpp:time')

    def _handle_time_request(self, iq: Iq):
        """
        Respond to a request for the local time.

        The time is taken from self.local_time(), which may be replaced
        during plugin configuration with a function that maps JIDs to
        times.

        :param iq: The Iq time request stanza.
        """
        iq = iq.reply()
        iq['entity_time']['time'] = self.local_time(iq['to'])
        iq.send()

    def get_entity_time(self, to: JID, ifrom: Optional[JID] = None, **iqargs):
        """
        Request the time from another entity.

        :param to: JID of the entity to query.
        """
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['to'] = to
        iq['from'] = ifrom
        iq.enable('entity_time')
        return iq.send(**iqargs)

