
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Dalek
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0249.stanza import Invite
from slixmpp.plugins.xep_0249.invite import XEP_0249


register_plugin(XEP_0249)
