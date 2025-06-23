
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

import slixmpp
from slixmpp.stanza import Message
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin, ElementBase, ET
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0380 import stanza, Encryption


log = logging.getLogger(__name__)


class XEP_0380(BasePlugin):

    """
    XEP-0380: Explicit Message Encryption
    """

    name = 'xep_0380'
    description = 'XEP-0380: Explicit Message Encryption'
    dependencies = {'xep_0030'}
    default_config = {
        'template': 'This message is encrypted with {name} ({namespace})',
    }

    mechanisms = {
        'jabber:x:encrypted': 'Legacy OpenPGP',
        'urn:xmpp:ox:0': 'OpenPGP for XMPP',
        'urn:xmpp:otr:0': 'OTR',
        'eu.siacs.conversations.axolotl': 'Legacy OMEMO',
        'urn:xmpp:omemo:0': 'OMEMO',
    }

    def plugin_init(self):
        self.xmpp.register_handler(
            Callback('Explicit Message Encryption',
                     StanzaPath('message/eme'),
                     self._handle_eme))

        register_stanza_plugin(Message, Encryption)

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(Encryption.namespace)

    def has_eme(self, msg):
        return msg.xml.find('{%s}encryption' % Encryption.namespace) is not None

    def add_eme(self, msg: Message, namespace: str) -> Message:
        msg['eme']['name'] = self.mechanisms[namespace]
        msg['eme']['namespace'] = namespace
        return msg

    def replace_body_with_eme(self, msg):
        eme = msg['eme']
        namespace = eme['namespace']
        name = self.mechanisms[namespace] if namespace in self.mechanisms else eme['name']
        body = self.config['template'].format(name=name, namespace=namespace)
        msg['body'] = body

    def _handle_eme(self, msg):
        self.xmpp.event('message_encryption', msg)
