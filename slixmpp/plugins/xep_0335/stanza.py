
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Maxime “pep” Buquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import json
from slixmpp.xmlstream import ElementBase


class JSON_Container(ElementBase):
    name = 'json'
    plugin_attrib = 'json'
    namespace = 'urn:xmpp:json:0'
    interfaces = {'value'}

    def get_value(self):
        return json.loads(self.xml.text)

    def set_value(self, value):
        if not isinstance(value, str):
            value = json.dumps(value)
        self.xml.text = value

    def del_value(self):
        self.xml.text = ''
