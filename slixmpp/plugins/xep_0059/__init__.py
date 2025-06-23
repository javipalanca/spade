
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Erik Reuterborg Larsson
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0059.stanza import Set
from slixmpp.plugins.xep_0059.rsm import ResultIterator, XEP_0059


register_plugin(XEP_0059)
