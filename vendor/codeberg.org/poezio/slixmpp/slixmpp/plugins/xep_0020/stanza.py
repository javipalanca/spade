
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


class FeatureNegotiation(ElementBase):

    name = 'feature'
    namespace = 'http://jabber.org/protocol/feature-neg'
    plugin_attrib = 'feature_neg'
    interfaces = set()
