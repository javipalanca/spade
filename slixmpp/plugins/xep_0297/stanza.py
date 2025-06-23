
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.stanza import Message, Presence, Iq
from slixmpp.xmlstream import ElementBase


class Forwarded(ElementBase):
    name = 'forwarded'
    namespace = 'urn:xmpp:forward:0'
    plugin_attrib = 'forwarded'
    interfaces = {'stanza'}

    def get_stanza(self):
        for stanza in self:
            if isinstance(stanza, (Message, Presence, Iq)):
                return stanza
        return ''

    def set_stanza(self, value):
        self.del_stanza()
        self.append(value)

    def del_stanza(self):
        found_stanzas = []
        for stanza in self:
            if isinstance(stanza, (Message, Presence, Iq)):
                found_stanzas.append(stanza)
        for stanza in found_stanzas:
            self.iterables.remove(stanza)
            self.xml.remove(stanza.xml)
