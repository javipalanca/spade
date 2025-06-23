
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0377.stanza import Report, Text
from slixmpp.plugins.xep_0377.spam_reporting import XEP_0377


register_plugin(XEP_0377)
