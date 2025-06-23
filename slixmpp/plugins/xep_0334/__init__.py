
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0334.stanza import Store, NoStore, NoPermanentStore, NoCopy
from slixmpp.plugins.xep_0334.hints import XEP_0334

register_plugin(XEP_0334)
