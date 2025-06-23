
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 "Maxime “pep” Buquet <pep@bouah.net>"
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import register_plugin
from slixmpp.plugins.xep_0045 import stanza
from slixmpp.plugins.xep_0045.muc import XEP_0045
from slixmpp.plugins.xep_0045.stanza import MUCPresence, MUCMessage

register_plugin(XEP_0045)
