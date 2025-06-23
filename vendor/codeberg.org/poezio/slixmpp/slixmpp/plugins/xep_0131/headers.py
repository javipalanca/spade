
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp import Message, Presence
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0131 import stanza
from slixmpp.plugins.xep_0131.stanza import Headers


class XEP_0131(BasePlugin):

    name = 'xep_0131'
    description = 'XEP-0131: Stanza Headers and Internet Metadata'
    dependencies = {'xep_0030'}
    stanza = stanza
    default_config = {
        'supported_headers': set()
    }

    def plugin_init(self):
        register_stanza_plugin(Message, Headers)
        register_stanza_plugin(Presence, Headers)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Headers.namespace)
        for header in self.supported_headers:
            self.xmpp['xep_0030'].del_feature(
                    feature='%s#%s' % (Headers.namespace, header))

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Headers.namespace)
        for header in self.supported_headers:
            self.xmpp['xep_0030'].add_feature('%s#%s' % (
                Headers.namespace,
                header))
