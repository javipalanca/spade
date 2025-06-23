# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp.stanza import StreamFeatures
from slixmpp.features.feature_preapproval import stanza
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.base import BasePlugin
from typing import ClassVar, Set


log = logging.getLogger(__name__)


class FeaturePreApproval(BasePlugin):

    name = 'feature_preapproval'
    description = 'RFC 6121: Stream Feature: Subscription Pre-Approval'
    dependencies: ClassVar[Set[str]] = set()
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_feature('preapproval',
                self._handle_preapproval,
                restart=False,
                order=9001)

        register_stanza_plugin(StreamFeatures, stanza.PreApproval)

    def _handle_preapproval(self, features):
        """Save notice that the server support subscription pre-approvals.

        Arguments:
            features -- The stream features stanza.
        """
        log.debug("Server supports subscription pre-approvals.")
        self.xmpp.features.add('preapproval')
