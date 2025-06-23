
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.stanza import Message
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)


NS = 'urn:xmpp:fasten:0'


class ApplyTo(ElementBase):
    namespace = NS
    name = 'apply-to'
    plugin_attrib = 'apply_to'
    interfaces = {'id', 'shell'}

    def set_shell(self, value: bool):
        if value:
            self.xml.attrib['shell'] = str(value).lower()
        else:
            if 'shell' in self.xml.attrib:
                del self.xml.attrib['shell']


class External(ElementBase):
    namespace = NS
    name = 'external'
    plugin_attrib = 'external'
    interfaces = {'name'}


def register_plugins():
    register_stanza_plugin(Message, ApplyTo)
    register_stanza_plugin(ApplyTo, External)
