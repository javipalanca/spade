
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.stanza import Message
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)


NS = 'urn:xmpp:sid:0'


class StanzaID(ElementBase):
    namespace = NS
    name = 'stanza-id'
    plugin_attrib = 'stanza_id'
    interfaces = {'id', 'by'}


class OriginID(ElementBase):
    namespace = NS
    name = 'origin-id'
    plugin_attrib = 'origin_id'
    interfaces = {'id'}


def register_plugins():
    register_stanza_plugin(Message, StanzaID)
    register_stanza_plugin(Message, OriginID)
