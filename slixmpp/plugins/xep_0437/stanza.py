
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Iterable
from slixmpp import JID, Presence
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)

NS = 'urn:xmpp:rai:0'

class RAI(ElementBase):
    name = 'rai'
    plugin_attrib = 'rai'
    namespace = NS
    interfaces = {'activities'}

    def get_activities(self) -> Iterable[JID]:
        return [JID(el.xml.text) for el in self if isinstance(el, Activity)]

    def del_activities(self):
        for el in self.xml.findall('{%s}activity' % NS):
            self.xml.remove(el)

    def set_activities(self, activities: Iterable[JID]):
        self.del_activities()
        for jid in activities:
            act = Activity()
            act.xml.text = str(jid)
            self.append(act)


class Activity(ElementBase):
    name = 'activity'
    plugin_attrib = 'activity'
    namespace = NS


def register_plugins():
    register_stanza_plugin(RAI, Activity, iterable=True)
    register_stanza_plugin(Presence, RAI)
