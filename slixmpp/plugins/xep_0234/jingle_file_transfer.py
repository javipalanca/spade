import logging

from slixmpp.plugins import BasePlugin

from . import stanza

log = logging.getLogger(__name__)


class XEP_0234(BasePlugin):

    """
    XEP-0234: Jingle File Transfer

    Minimum needed for xep 0385 (Stateless inline media sharing)
    """

    name = "xep_0234"
    description = "XEP-0234: Jingle File Transfer"
    dependencies = {"xep_0082", "xep_0300"}
    stanza = stanza
