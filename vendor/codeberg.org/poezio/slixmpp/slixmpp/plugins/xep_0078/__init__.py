
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0078 import stanza
from slixmpp.plugins.xep_0078.stanza import IqAuth, AuthFeature
from slixmpp.plugins.xep_0078.legacyauth import XEP_0078


register_plugin(XEP_0078)
