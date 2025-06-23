
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0033 import stanza
from slixmpp.plugins.xep_0033.stanza import Addresses, Address
from slixmpp.plugins.xep_0033.addresses import XEP_0033


register_plugin(XEP_0033)
