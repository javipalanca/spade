
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0380.stanza import Encryption
from slixmpp.plugins.xep_0380.eme import XEP_0380


register_plugin(XEP_0380)
