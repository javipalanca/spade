from slixmpp.plugins.base import register_plugin

from . import stanza
from .jingle_file_transfer import XEP_0234

register_plugin(XEP_0234)
