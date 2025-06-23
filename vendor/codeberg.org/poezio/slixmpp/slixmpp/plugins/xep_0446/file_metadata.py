import logging

from slixmpp.plugins import BasePlugin

from . import stanza

log = logging.getLogger(__name__)


class XEP_0446(BasePlugin):

    """
    XEP-0446: File metadata element

    Minimum needed for xep 0447 (Stateless file sharing)
    """

    name = "xep_0446"
    description = "XEP-0446: File metadata element"
    stanza = stanza
    dependencies = {'xep_0300', 'xep_0264'}

    def plugin_init(self):
        stanza.register_plugins()
