
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2015 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


class Confirm(ElementBase):

    name = 'confirm'
    namespace = 'http://jabber.org/protocol/http-auth'
    plugin_attrib = 'confirm'
    interfaces = {'id', 'url', 'method'}
