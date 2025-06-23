
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Erik Reuterborg Larsson, Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0184.stanza import Request, Received
from slixmpp.plugins.xep_0184.receipt import XEP_0184


register_plugin(XEP_0184)
