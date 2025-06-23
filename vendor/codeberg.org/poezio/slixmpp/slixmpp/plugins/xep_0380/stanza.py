
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


class Encryption(ElementBase):
    name = 'encryption'
    namespace = 'urn:xmpp:eme:0'
    plugin_attrib = 'eme'
    interfaces = {'namespace', 'name'}
