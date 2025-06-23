# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.plugins.base import register_plugin
from slixmpp.plugins.xep_0410.self_ping import XEP_0410, PingStatus

register_plugin(XEP_0410)
