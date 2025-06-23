
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 "Maxime “pep” Buquet <pep@bouah.net>"
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin
from slixmpp.plugins.xep_0421.stanza import OccupantId
from slixmpp.plugins.xep_0421.occupant_id import XEP_0421

register_plugin(XEP_0421)
