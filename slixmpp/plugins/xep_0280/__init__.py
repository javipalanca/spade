
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0280.stanza import ReceivedCarbon, SentCarbon
from slixmpp.plugins.xep_0280.stanza import PrivateCarbon
from slixmpp.plugins.xep_0280.stanza import CarbonEnable, CarbonDisable
from slixmpp.plugins.xep_0280.carbons import XEP_0280


register_plugin(XEP_0280)
