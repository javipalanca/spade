
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0279 import stanza
from slixmpp.plugins.xep_0279.stanza import IPCheck
from slixmpp.plugins.xep_0279.ipcheck import XEP_0279


register_plugin(XEP_0279)
