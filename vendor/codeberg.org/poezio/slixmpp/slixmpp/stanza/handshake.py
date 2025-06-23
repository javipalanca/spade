# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.xmlstream import StanzaBase
from typing import Optional


class Handshake(StanzaBase):

    """
    Jabber Component protocol handshake
    """
    namespace = 'jabber:component:accept'
    name = 'handshake'
    interfaces = {'value'}

    def set_value(self, value: str):
        self.xml.text = value

    def get_value(self) -> Optional[str]:
        return self.xml.text

    def del_value(self):
        self.xml.text = ''
