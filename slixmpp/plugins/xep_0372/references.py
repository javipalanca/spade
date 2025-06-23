import logging

from slixmpp import Message, register_stanza_plugin
from slixmpp.plugins import BasePlugin

from . import stanza

log = logging.getLogger(__name__)


class XEP_0372(BasePlugin):
    """
    XEP-0372: References

    Minimum needed for xep 0385 (Stateless inline media sharing)
    """

    name = "xep_0372"
    description = "XEP-0372: References"
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, stanza.Reference)
