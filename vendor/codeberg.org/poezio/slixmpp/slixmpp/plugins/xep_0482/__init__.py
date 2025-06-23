# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0482 import stanza
from slixmpp.plugins.xep_0482.call_invites import XEP_0482


register_plugin(XEP_0482)
