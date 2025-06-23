
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0297 import stanza
from slixmpp.plugins.xep_0297.stanza import Forwarded
from slixmpp.plugins.xep_0297.forwarded import XEP_0297


register_plugin(XEP_0297)
