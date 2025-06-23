
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0049.stanza import PrivateXML
from slixmpp.plugins.xep_0049.private_storage import XEP_0049


register_plugin(XEP_0049)
