
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase, ET


class Session(ElementBase):

    """
    """

    name = 'session'
    namespace = 'urn:ietf:params:xml:ns:xmpp-session'
    interfaces = {'optional'}
    plugin_attrib = 'session'

    def get_optional(self):
        return self.xml.find('{%s}optional' % self.namespace) is not None

    def set_optional(self, value):
        if value:
            optional = ET.Element('{%s}optional' % self.namespace)
            self.xml.append(optional)
        else:
            self.del_optional()

    def del_optional(self):
        optional = self.xml.find('{%s}optional' % self.namespace)
        self.xml.remove(optional)
