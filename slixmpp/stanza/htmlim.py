
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.stanza import Message
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0071 import XHTML_IM as HTMLIM


register_stanza_plugin(Message, HTMLIM)
