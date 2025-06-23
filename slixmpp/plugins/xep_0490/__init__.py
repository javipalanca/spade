from slixmpp.plugins.base import register_plugin

from . import stanza
from .mds import XEP_0490

register_plugin(XEP_0490)

__all__ = ['stanza', 'XEP_0490']
