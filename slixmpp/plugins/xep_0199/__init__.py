
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0199.stanza import Ping
from slixmpp.plugins.xep_0199.ping import XEP_0199


register_plugin(XEP_0199)
