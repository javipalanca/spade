from slixmpp.plugins import BasePlugin
from . import stanza


class XEP_0469(BasePlugin):

    """
    XEP-0469: Bookmark Pinning
    """

    name = "xep_0469"
    description = "XEP-0469: Bookmark Pinning"
    dependencies = {"xep_0402"}
    stanza = stanza

    def plugin_init(self):
        stanza.register_plugin()
