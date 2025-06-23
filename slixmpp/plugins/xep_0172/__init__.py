
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0172 import stanza
from slixmpp.plugins.xep_0172.stanza import UserNick
from slixmpp.plugins.xep_0172.user_nick import XEP_0172


register_plugin(XEP_0172)
