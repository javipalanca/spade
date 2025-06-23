
# slixmpp: The Slick XMPP Library
# Copyright (C) 2016 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase

NS ='urn:xmpp:chat-markers:0'

class Markable(ElementBase):
    name = 'markable'
    plugin_attrib = 'markable'
    namespace = NS


class Received(ElementBase):
    name = 'received'
    plugin_attrib = 'received'
    namespace = NS
    interfaces = {'id'}


class Displayed(ElementBase):
    name = 'displayed'
    plugin_attrib = 'displayed'
    namespace = NS
    interfaces = {'id'}


class Acknowledged(ElementBase):
    name = 'acknowledged'
    plugin_attrib = 'acknowledged'
    namespace = NS
    interfaces = {'id'}
