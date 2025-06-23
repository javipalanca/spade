
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0084 import stanza
from slixmpp.plugins.xep_0084.stanza import Data, MetaData
from slixmpp.plugins.xep_0084.avatar import XEP_0084


register_plugin(XEP_0084)
