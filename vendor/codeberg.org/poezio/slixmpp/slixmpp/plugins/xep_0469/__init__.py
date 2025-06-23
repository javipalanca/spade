from slixmpp.plugins.base import register_plugin

from . import stanza
from .pinning import XEP_0469

register_plugin(XEP_0469)

__all__ = ['stanza', 'XEP_0469']
