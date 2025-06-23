
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0020 import stanza
from slixmpp.plugins.xep_0020.stanza import FeatureNegotiation
from slixmpp.plugins.xep_0020.feature_negotiation import XEP_0020


register_plugin(XEP_0020)
