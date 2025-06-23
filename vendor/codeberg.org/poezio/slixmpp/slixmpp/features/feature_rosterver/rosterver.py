# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp.stanza import StreamFeatures
from slixmpp.features.feature_rosterver import stanza
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.base import BasePlugin
from typing import ClassVar, Set


log = logging.getLogger(__name__)


class FeatureRosterVer(BasePlugin):

    name = 'feature_rosterver'
    description = 'RFC 6121: Stream Feature: Roster Versioning'
    dependences: ClassVar[Set[str]] = set()
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_feature('rosterver',
                self._handle_rosterver,
                restart=False,
                order=9000)

        register_stanza_plugin(StreamFeatures, stanza.RosterVer)

    def _handle_rosterver(self, features):
        """Enable using roster versioning.

        Arguments:
            features -- The stream features stanza.
        """
        log.debug("Enabling roster versioning.")
        self.xmpp.features.add('rosterver')
