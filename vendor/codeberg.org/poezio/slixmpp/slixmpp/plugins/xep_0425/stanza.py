
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.stanza import Message, Iq
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)
from slixmpp.plugins.xep_0421.stanza import OccupantId
from slixmpp.plugins.xep_0424.stanza import Retract, Retracted


NS = 'urn:xmpp:message-moderate:1'


class Moderate(ElementBase):
    namespace = NS
    name = 'moderate'
    plugin_attrib = 'moderate'
    interfaces = {'id', 'reason'}
    sub_interfaces = {'reason'}


class Moderated(ElementBase):
    namespace = NS
    name = 'moderated'
    plugin_attrib = 'moderated'
    interfaces = {'by'}


def register_plugins():
    # for moderation requests
    register_stanza_plugin(Iq, Moderate)
    register_stanza_plugin(Moderate, Retract)

    # for moderation events
    register_stanza_plugin(Retract, Moderated)
    register_stanza_plugin(Moderated, OccupantId)

    # for tombstones
    register_stanza_plugin(Retracted, Moderated)
