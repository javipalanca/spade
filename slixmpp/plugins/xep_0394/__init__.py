
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0394.stanza import Markup, Span, BlockCode, List, Li, BlockQuote
from slixmpp.plugins.xep_0394.markup import XEP_0394


register_plugin(XEP_0394)
