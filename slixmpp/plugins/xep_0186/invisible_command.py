
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0186 import stanza, Visible, Invisible


log = logging.getLogger(__name__)


class XEP_0186(BasePlugin):

    name = 'xep_0186'
    description = 'XEP-0186: Invisible Command'
    dependencies = {'xep_0030'}

    def plugin_init(self):
        register_stanza_plugin(Iq, Visible)
        register_stanza_plugin(Iq, Invisible)

    def set_invisible(self, ifrom=None, callback=None,
                            timeout=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['from'] = ifrom
        iq.enable('invisible')
        return iq.send(callback=callback, timeout=timeout)

    def set_visible(self, ifrom=None, callback=None,
                          timeout=None):
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['from'] = ifrom
        iq.enable('visible')
        return iq.send(callback=callback, timeout=timeout)
