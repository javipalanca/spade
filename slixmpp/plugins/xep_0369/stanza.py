
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
import xml.etree.ElementTree as ET
from slixmpp import JID
from slixmpp.stanza import (
    Iq,
    Message,
)
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)

from slixmpp.plugins.xep_0004.stanza import (
    Form,
)
from slixmpp.plugins.xep_0060.stanza import (
    EventItem,
    Item,
)

NS = 'urn:xmpp:mix:core:1'


class MIX(ElementBase):
    name = 'mix'
    namespace = NS
    plugin_attrib = 'mix'
    interfaces = {'nick', 'jid'}
    sub_interfaces = {'nick', 'jid'}


class Setnick(ElementBase):
    name = 'setnick'
    namespace = NS
    plugin_attrib = 'mix_setnick'
    interfaces = {'nick'}
    sub_interfaces = {'nick'}


class Join(ElementBase):
    namespace = NS
    name = 'join'
    plugin_attrib = 'mix_join'
    interfaces = {'nick', 'id'}
    sub_interfaces = {'nick'}


class Leave(ElementBase):
    namespace = NS
    name = 'leave'
    plugin_attrib = 'mix_leave'


class Subscribe(ElementBase):
    namespace = NS
    name = 'subscribe'
    plugin_attrib = 'subscribe'
    interfaces = {'node'}


class Unsubscribe(ElementBase):
    namespace = NS
    name = 'unsubscribe'
    plugin_attrib = 'unsubscribe'
    interfaces = {'node'}

class UpdateSubscription(ElementBase):
    namespace = NS
    name = 'update-subscription'
    plugin_attrib = 'mix_updatesub'
    interfaces = {'jid'}


class Create(ElementBase):
    name = 'create'
    plugin_attrib = 'mix_create'
    namespace = NS
    interfaces = {'channel'}


class Participant(ElementBase):
    namespace = NS
    name = 'participant'
    plugin_attrib = 'mix_participant'
    interfaces = {'nick', 'jid'}
    sub_interfaces = {'nick', 'jid'}


class Destroy(ElementBase):
    name = 'destroy'
    plugin_attrib = 'mix_destroy'
    namespace = NS
    interfaces = {'channel'}


def register_plugins():
    register_stanza_plugin(Item, Form)
    register_stanza_plugin(EventItem, Form)

    register_stanza_plugin(EventItem, Participant)
    register_stanza_plugin(Item, Participant)

    register_stanza_plugin(Join, Subscribe, iterable=True)
    register_stanza_plugin(Iq, Join)

    register_stanza_plugin(UpdateSubscription, Subscribe, iterable=True)
    register_stanza_plugin(UpdateSubscription, Unsubscribe, iterable=True)
    register_stanza_plugin(Iq, UpdateSubscription)

    register_stanza_plugin(Iq, Leave)
    register_stanza_plugin(Iq, Create)
    register_stanza_plugin(Iq, Setnick)

    register_stanza_plugin(Message, MIX)
