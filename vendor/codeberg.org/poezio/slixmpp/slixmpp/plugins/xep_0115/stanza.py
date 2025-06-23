
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from __future__ import unicode_literals

from slixmpp.xmlstream import ElementBase


class Capabilities(ElementBase):

    namespace = 'http://jabber.org/protocol/caps'
    name = 'c'
    plugin_attrib = 'caps'
    interfaces = {'hash', 'node', 'ver', 'ext'}
