
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Maxime “pep” Buquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp import Message
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0335 import JSON_Container
from slixmpp.plugins.xep_0335 import stanza


class XEP_0335(BasePlugin):

    name = 'xep_0335'
    description = 'XEP-0335: JSON Containers'
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, JSON_Container)
