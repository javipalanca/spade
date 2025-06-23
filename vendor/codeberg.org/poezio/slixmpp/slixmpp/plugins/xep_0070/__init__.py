
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2015 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0070.stanza import Confirm
from slixmpp.plugins.xep_0070.confirm import XEP_0070


register_plugin(XEP_0070)
