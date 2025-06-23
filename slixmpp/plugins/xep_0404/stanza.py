
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)
from slixmpp import Iq

from slixmpp.plugins.xep_0004.stanza import Form
from slixmpp.plugins.xep_0060.stanza import (
    EventItem,
    Item,
)

NS = 'urn:xmpp:mix:anon:0'


class Participant(ElementBase):
    namespace = NS
    name = 'participant'
    plugin_attrib = 'anon_participant'
    interfaces = {'jid'}
    sub_interfaces = {'jid'}


class UserPreference(ElementBase):
    namespace = NS
    name = 'user-preference'
    plugin_attrib = 'user_preference'


def register_plugins():
    register_stanza_plugin(EventItem, Participant)
    register_stanza_plugin(Item, Participant)

    register_stanza_plugin(Iq, UserPreference)
    register_stanza_plugin(UserPreference, Form)
