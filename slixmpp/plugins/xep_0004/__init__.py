
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0004.stanza import Form
from slixmpp.plugins.xep_0004.stanza import FormField, FieldOption
from slixmpp.plugins.xep_0004.dataforms import XEP_0004


register_plugin(XEP_0004)
