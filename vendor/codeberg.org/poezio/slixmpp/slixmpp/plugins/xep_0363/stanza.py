
# slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase

class Request(ElementBase):
    plugin_attrib = 'http_upload_request'
    name = 'request'
    namespace = 'urn:xmpp:http:upload:0'
    interfaces = {'filename', 'size', 'content-type'}

class Slot(ElementBase):
    plugin_attrib = 'http_upload_slot'
    name = 'slot'
    namespace = 'urn:xmpp:http:upload:0'

class Put(ElementBase):
    plugin_attrib = 'put'
    name = 'put'
    namespace = 'urn:xmpp:http:upload:0'
    interfaces = {'url'}

class Get(ElementBase):
    plugin_attrib = 'get'
    name = 'get'
    namespace = 'urn:xmpp:http:upload:0'
    interfaces = {'url'}

class Header(ElementBase):
    plugin_attrib = 'header'
    name = 'header'
    namespace = 'urn:xmpp:http:upload:0'
    plugin_multi_attrib = 'headers'
    interfaces = {'name', 'value'}

    def get_value(self):
        return self.xml.text

    def set_value(self, value):
        self.xml.text = value

    def del_value(self):
        self.xml.text = ''
