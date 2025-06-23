
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.stanza import Message
from slixmpp.xmlstream import (
    register_stanza_plugin,
    ElementBase,
)


NS = 'urn:xmpp:spoiler:0'


class Spoiler(ElementBase):
    namespace = NS
    name = 'spoiler'
    plugin_attrib = 'spoiler'


def register_plugins():
    register_stanza_plugin(Message, Spoiler)
