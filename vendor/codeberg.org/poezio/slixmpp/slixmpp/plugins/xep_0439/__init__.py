
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin
from slixmpp.plugins.xep_0439.stanza import *
from slixmpp.plugins.xep_0439.quickresponse import XEP_0439

register_plugin(XEP_0439)
