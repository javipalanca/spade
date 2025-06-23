
# slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0353.stanza import Propose, Retract, Accept, Proceed, Reject
from slixmpp.plugins.xep_0353.jingle_message import XEP_0353

register_plugin(XEP_0353)
