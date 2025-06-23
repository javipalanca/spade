
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

import slixmpp
from slixmpp import Message
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.xep_0377 import stanza
from slixmpp.plugins.xep_0191 import Block


log = logging.getLogger(__name__)


class XEP_0377(BasePlugin):
    """XEP-0377: Spam reporting"""

    name = 'xep_0377'
    description = 'XEP-0377: Spam Reporting'
    dependencies = {'xep_0030', 'xep_0191'}
    stanza = stanza

    SPAM = 'urn:xmpp:reporting:spam'
    ABUSE = 'urn:xmpp:reporting:abuse'

    def plugin_init(self):
        register_stanza_plugin(Block, stanza.Report)
        register_stanza_plugin(stanza.Report, stanza.Text)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=stanza.Report.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(stanza.Report.namespace)

