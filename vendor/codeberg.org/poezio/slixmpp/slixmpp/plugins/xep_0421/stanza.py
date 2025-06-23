
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 "Maxime “pep” Buquet <pep@bouah.net>"
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


NS = 'urn:xmpp:occupant-id:0'


class OccupantId(ElementBase):
    '''
    An Occupant-id tag.

    An <occupant-id/> tag is set by the MUC.

    This is useful in semi-anon MUCs (and MUC-PMs) as a stable identifier to
    prevent the usual races with nicknames.

    Without occupant-id, getting the following messages from MUC history would
    prevent a client from asserting senders are the same entity:

    ::

        <message type='groupchat' from='foo@muc/nick1' id='message1'>
            <body>Some message</body>
            <occupant-id xmlns='urn:xmpp:occupant-id:0' id='unique-opaque-id1'/>
        </message>
        <message type='groupchat' from='foo@muc/nick2' id='message2'>
            <body>Some correction</body>
            <occupant-id xmlns='urn:xmpp:occupant-id:0' id='unique-opaque-id1'/>
            <replace xmlns='urn:xmpp:message-correct:0' id='message1'/>
        </message>
    '''

    name = 'occupant-id'
    plugin_attrib = 'occupant-id'
    namespace = NS
    interface = {'id'}
