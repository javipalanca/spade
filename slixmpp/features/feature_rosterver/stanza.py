# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase
from typing import Set, ClassVar


class RosterVer(ElementBase):

    name = 'ver'
    namespace = 'urn:xmpp:features:rosterver'
    interfaces: ClassVar[Set[str]] = set()
    plugin_attrib = 'rosterver'
