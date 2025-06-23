
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0108 import stanza
from slixmpp.plugins.xep_0108.stanza import UserActivity
from slixmpp.plugins.xep_0108.user_activity import XEP_0108


register_plugin(XEP_0108)
