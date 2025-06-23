from slixmpp.plugins.base import register_plugin

from . import stanza, vcard4
from .vcard4 import XEP_0292

register_plugin(vcard4.XEP_0292)
