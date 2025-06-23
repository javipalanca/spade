
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


class Hash(ElementBase):
    name = 'hash'
    namespace = 'urn:xmpp:hashes:2'
    plugin_attrib = 'hash'
    interfaces = {'algo', 'value'}

    allowed_algos = ['sha-1', 'sha-256', 'sha-512', 'sha3-256', 'sha3-512', 'BLAKE2b256', 'BLAKE2b512']

    def set_algo(self, value):
        if value in self.allowed_algos:
            self._set_attr('algo', value)
        elif value in [None, '']:
            self._del_attr('algo')
        else:
            raise ValueError('Invalid algo: %s' % value)

    def get_value(self):
        return self.xml.text

    def set_value(self, value):
        self.xml.text = value

    def del_value(self):
        self.xml.text = ''
