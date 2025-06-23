
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp import Presence
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0012 import stanza, LastActivity

log = logging.getLogger(__name__)


class XEP_0256(BasePlugin):

    name = 'xep_0256'
    description = 'XEP-0256: Last Activity in Presence'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Presence, LastActivity)
