
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin
from slixmpp.plugins.xep_0405.stanza import *
from slixmpp.plugins.xep_0405.mix_pam import XEP_0405

register_plugin(XEP_0405)
