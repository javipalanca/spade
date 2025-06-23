
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp import JID
from slixmpp.stanza import Iq
from slixmpp.stanza.roster import Roster, RosterItem
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)

from slixmpp.plugins.xep_0369.stanza import (
    Join,
    Leave,
)

NS = 'urn:xmpp:mix:pam:2'
NS_ROSTER = 'urn:xmpp:mix:roster:0'


class ClientJoin(ElementBase):
    namespace = NS
    name = 'client-join'
    plugin_attrib = 'client_join'
    interfaces = {'channel'}


class ClientLeave(ElementBase):
    namespace = NS
    name = 'client-leave'
    plugin_attrib = 'client_leave'
    interfaces = {'channel'}


class Annotate(ElementBase):
    namespace = NS_ROSTER
    name = 'annotate'
    plugin_attrib = 'annotate'


class Channel(ElementBase):
    namespace = NS_ROSTER
    name = 'channel'
    plugin_attrib = 'channel'
    interfaces = {'participant-id'}


def register_plugins():
    register_stanza_plugin(Iq, ClientJoin)
    register_stanza_plugin(ClientJoin, Join)

    register_stanza_plugin(Iq, ClientLeave)
    register_stanza_plugin(ClientLeave, Leave)

    register_stanza_plugin(Roster, Annotate)
    register_stanza_plugin(RosterItem, Channel)
