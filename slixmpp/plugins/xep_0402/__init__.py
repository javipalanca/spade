from slixmpp.plugins.base import register_plugin

from . import stanza
from .bookmarks import XEP_0402

register_plugin(XEP_0402)
