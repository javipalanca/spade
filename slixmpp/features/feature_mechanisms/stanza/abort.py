# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import StanzaBase
from typing import ClassVar, Set


class Abort(StanzaBase):

    """
    """

    name = 'abort'
    namespace = 'urn:ietf:params:xml:ns:xmpp-sasl'
    interfaces: ClassVar[Set[str]] = set()
    plugin_attrib = name

    def setup(self, xml):
        StanzaBase.setup(self, xml)
        self.xml.tag = self.tag_name()
