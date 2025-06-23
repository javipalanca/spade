
# slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0333.stanza import Markable, Received, Displayed, Acknowledged
from slixmpp.plugins.xep_0333.markers import XEP_0333

register_plugin(XEP_0333)
