
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins import BasePlugin, register_plugin


class XEP_0242(BasePlugin):

    name = 'xep_0242'
    description = 'XEP-0242: XMPP Client Compliance 2009'
    dependencies = {'xep_0030', 'xep_0115', 'xep_0054',
                    'xep_0045', 'xep_0085', 'xep_0016',
                    'xep_0191'}


register_plugin(XEP_0242)
