# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import asyncio
import logging

from slixmpp.jid import JID
from slixmpp.stanza import Iq, StreamFeatures
from slixmpp.features.feature_bind import stanza
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from typing import ClassVar, Set


log = logging.getLogger(__name__)


class FeatureBind(BasePlugin):

    name = 'feature_bind'
    description = 'RFC 6120: Stream Feature: Resource Binding'
    dependencies: ClassVar[Set[str]] = set()
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_feature('bind',
                self._handle_bind_resource,
                restart=False,
                order=10000)

        register_stanza_plugin(Iq, stanza.Bind)
        register_stanza_plugin(StreamFeatures, stanza.Bind)

    async def _handle_bind_resource(self, features):
        """
        Handle requesting a specific resource.

        Arguments:
            features -- The stream features stanza.
        """
        log.debug("Requesting resource: %s", self.xmpp.requested_jid.resource)
        self.features = features
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq.enable('bind')
        if self.xmpp.requested_jid.resource:
            iq['bind']['resource'] = self.xmpp.requested_jid.resource

        await iq.send(callback=self._on_bind_response)

    def _on_bind_response(self, response):
        self.xmpp.boundjid = JID(response['bind']['jid'])
        self.xmpp.bound = True
        self.xmpp.event('session_bind', self.xmpp.boundjid)
        self.xmpp.session_bind_event.set()

        self.xmpp.features.add('bind')

        log.info("JID set to: %s", self.xmpp.boundjid.full)

        if 'session' not in self.features['features']:
            log.debug("Established Session")
            self.xmpp.sessionstarted = True
            self.xmpp.event('session_start')
