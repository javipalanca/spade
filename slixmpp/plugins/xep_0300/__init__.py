
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0300 import stanza
from slixmpp.plugins.xep_0300.stanza import Hash
from slixmpp.plugins.xep_0300.hash import XEP_0300


register_plugin(XEP_0300)
