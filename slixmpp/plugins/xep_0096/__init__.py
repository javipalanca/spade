
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0096 import stanza
from slixmpp.plugins.xep_0096.stanza import File
from slixmpp.plugins.xep_0096.file_transfer import XEP_0096


register_plugin(XEP_0096)
