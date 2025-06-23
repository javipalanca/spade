
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0066 import stanza
from slixmpp.plugins.xep_0066.stanza import OOB, OOBTransfer
from slixmpp.plugins.xep_0066.oob import XEP_0066


register_plugin(XEP_0066)
