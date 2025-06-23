
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0198.stanza import Enable, Enabled
from slixmpp.plugins.xep_0198.stanza import Resume, Resumed
from slixmpp.plugins.xep_0198.stanza import Failed
from slixmpp.plugins.xep_0198.stanza import StreamManagement
from slixmpp.plugins.xep_0198.stanza import Ack, RequestAck

from slixmpp.plugins.xep_0198.stream_management import XEP_0198


register_plugin(XEP_0198)
