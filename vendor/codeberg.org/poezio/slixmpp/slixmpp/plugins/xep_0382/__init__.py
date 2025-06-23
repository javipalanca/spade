
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin
from slixmpp.plugins.xep_0382.stanza import *
from slixmpp.plugins.xep_0382.spoiler import XEP_0382

register_plugin(XEP_0382)
