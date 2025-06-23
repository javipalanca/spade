
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0077.stanza import Register, RegisterFeature
from slixmpp.plugins.xep_0077.register import XEP_0077


register_plugin(XEP_0077)
