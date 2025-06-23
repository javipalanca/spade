
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import base64

from slixmpp.util import bytes
from slixmpp.xmlstream import StanzaBase

class Success(StanzaBase):

    """
    """

    name = 'success'
    namespace = 'urn:ietf:params:xml:ns:xmpp-sasl'
    interfaces = {'value'}
    plugin_attrib = name

    def setup(self, xml):
        StanzaBase.setup(self, xml)
        self.xml.tag = self.tag_name()

    def get_value(self):
        return base64.b64decode(bytes(self.xml.text))

    def set_value(self, values):
        if values:
            self.xml.text = bytes(base64.b64encode(values)).decode('utf-8')
        else:
            self.xml.text = '='

    def del_value(self):
        self.xml.text = ''
