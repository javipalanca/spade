
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.stanza import Message
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)


NS = 'urn:xmpp:message-retract:1'


class Retract(ElementBase):
    namespace = NS
    name = 'retract'
    plugin_attrib = 'retract'
    interfaces = {'reason', 'id'}
    sub_interfaces = {'reason'}


class Retracted(ElementBase):
    namespace = NS
    name = 'retracted'
    plugin_attrib = 'retracted'
    interfaces = {'stamp', 'id', 'reason'}
    sub_interfaces = {'reason'}


def register_plugins():
    register_stanza_plugin(Message, Retract)
    register_stanza_plugin(Message, Retracted)
