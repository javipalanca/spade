import logging

from slixmpp.plugins import BasePlugin

from . import stanza

log = logging.getLogger(__name__)


class XEP_0264(BasePlugin):

    """
    XEP-0264: Jingle Content Thumbnails

    Can also be used with 0385 (Stateless inline media sharing)
    """

    name = "xep_0264"
    description = "XEP-0264: Jingle Content Thumbnails"
    dependencies = {"xep_0234"}
    stanza = stanza

    def plugin_init(self):
        stanza.register_plugin()
