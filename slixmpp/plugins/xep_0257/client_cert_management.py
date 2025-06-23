
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0257 import stanza, Certs
from slixmpp.plugins.xep_0257 import AppendCert, DisableCert, RevokeCert


log = logging.getLogger(__name__)


class XEP_0257(BasePlugin):

    name = 'xep_0257'
    description = 'XEP-0257: Client Certificate Management for SASL EXTERNAL'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Iq, Certs)
        register_stanza_plugin(Iq, AppendCert)
        register_stanza_plugin(Iq, DisableCert)
        register_stanza_plugin(Iq, RevokeCert)

    def get_certs(self, ifrom=None, timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['from'] = ifrom
        iq.enable('sasl_certs')
        return iq.send(timeout=timeout, callback=callback)

    def add_cert(self, name, cert, allow_management=True, ifrom=None,
                       timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['from'] = ifrom
        iq['sasl_cert_append']['name'] = name
        iq['sasl_cert_append']['x509cert'] = cert
        iq['sasl_cert_append']['cert_management'] = allow_management
        return iq.send(timeout=timeout, callback=callback)

    def disable_cert(self, name, ifrom=None, timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['from'] = ifrom
        iq['sasl_cert_disable']['name'] = name
        return iq.send(timeout=timeout, callback=callback)

    def revoke_cert(self, name, ifrom=None, timeout=None, callback=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['from'] = ifrom
        iq['sasl_cert_revoke']['name'] = name
        return iq.send(timeout=timeout, callback=callback)
