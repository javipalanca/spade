
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0203 import stanza
from slixmpp.plugins.xep_0203.stanza import Delay
from slixmpp.plugins.xep_0203.delay import XEP_0203


register_plugin(XEP_0203)
