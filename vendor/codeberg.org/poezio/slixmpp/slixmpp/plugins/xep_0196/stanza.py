# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.xmlstream import ElementBase, ET


class UserGaming(ElementBase):

    name = 'game'
    namespace = 'urn:xmpp:gaming:0'
    plugin_attrib = 'gaming'
    interfaces = {'character_name', 'character_profile', 'name',
                  'level', 'server_address', 'server_name', 'uri'}
    sub_interfaces = interfaces
