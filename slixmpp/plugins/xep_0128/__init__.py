
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0128.static import StaticExtendedDisco
from slixmpp.plugins.xep_0128.extended_disco import XEP_0128


register_plugin(XEP_0128)
