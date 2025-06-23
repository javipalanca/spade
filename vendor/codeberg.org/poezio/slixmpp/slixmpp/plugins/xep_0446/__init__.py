from slixmpp.plugins.base import register_plugin

from . import stanza
from .file_metadata import XEP_0446

register_plugin(XEP_0446)
