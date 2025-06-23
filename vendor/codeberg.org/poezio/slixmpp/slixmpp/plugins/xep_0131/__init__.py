
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0131 import stanza
from slixmpp.plugins.xep_0131.stanza import Headers
from slixmpp.plugins.xep_0131.headers import XEP_0131


register_plugin(XEP_0131)
