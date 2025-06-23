from slixmpp.plugins import BasePlugin
from . import stanza


class XEP_0317(BasePlugin):
    """
    XEP-0317: Hats
    """
    name = 'xep_0317'
    description = 'XEP-0317: Hats'
    dependencies = {'xep_0030', 'xep_0045', 'xep_0050'}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self):
        stanza.register_plugin()
