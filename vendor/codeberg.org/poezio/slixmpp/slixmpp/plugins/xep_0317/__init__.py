# Slixmpp: The Slick XMPP Library
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import register_plugin
from slixmpp.plugins.xep_0317 import stanza
from slixmpp.plugins.xep_0317.hats import XEP_0317
from slixmpp.plugins.xep_0317.stanza import Hat, Hats

register_plugin(XEP_0317)

__all__ = ['stanza', 'XEP_0317', 'Hat', 'Hats', 'stanza']
