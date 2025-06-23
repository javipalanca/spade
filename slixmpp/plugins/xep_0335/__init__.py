
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Maxime “pep” Buquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0335 import stanza
from slixmpp.plugins.xep_0335.stanza import JSON_Container
from slixmpp.plugins.xep_0335.json_containers import XEP_0335

register_plugin(XEP_0335)
