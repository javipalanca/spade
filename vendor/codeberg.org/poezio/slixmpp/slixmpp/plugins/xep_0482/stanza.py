# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission

from typing import Tuple, List, Optional
from slixmpp import Message
from slixmpp.jid import JID
from slixmpp.xmlstream import ElementBase, register_stanza_plugin

NS = 'urn:xmpp:call-invites:0'


class Jingle(ElementBase):
    name = 'jingle'
    namespace = NS
    plugin_attrib = 'jingle'
    plugin_multi_attrib = 'jingles'
    interfaces = {'sid', 'jid'}

    def set_jid(self, value: JID) -> None:
        if not isinstance(value, JID):
            try:
                value = JID(value)
            except ValueError:
                raise ValueError(f'"jid" must be a valid JID object')
        self.xml.attrib['jid'] = value.full

    def get_jid(self) -> Optional[JID]:
        try:
            return JID(self.xml.attrib.get('jid', ''))
        except ValueError:
            return None


class External(ElementBase):
    name = 'external'
    namespace = NS
    plugin_attrib = 'external'
    plugin_multi_attrib = 'externals'
    interfaces = {'uri'}


class Invite(ElementBase):
    name = 'invite'
    namespace = NS
    plugin_attrib = 'call-invite'
    interfaces = {'video'}

    def get_methods(self) -> Tuple[List[Jingle], List[External]]:
        return (self['jingles'], self['externals'])

    def set_video(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError(f'Invalid value for the video attribute: {value}')
        self.xml.attrib['video'] = str(value).lower()

    def get_video(self) -> bool:
        vid = self.xml.attrib.get('video', 'false').lower()
        return vid == 'true'


class Retract(ElementBase):
    name = 'retract'
    namespace = NS
    plugin_attrib = 'call-retract'
    interfaces = {'id'}


class Accept(ElementBase):
    name = 'accept'
    namespace = NS
    plugin_attrib = 'call-accept'
    interfaces = {'id'}


class Reject(ElementBase):
    name = 'reject'
    namespace = NS
    plugin_attrib = 'call-reject'
    interfaces = {'id'}


class Left(ElementBase):
    name = 'left'
    namespace = NS
    plugin_attrib = 'call-left'
    interfaces = {'id'}


def register_plugins() -> None:
    register_stanza_plugin(Message, Invite)
    register_stanza_plugin(Message, Retract)
    register_stanza_plugin(Message, Accept)
    register_stanza_plugin(Message, Reject)
    register_stanza_plugin(Message, Left)

    register_stanza_plugin(Invite, Jingle, iterable=True)
    register_stanza_plugin(Invite, External, iterable=True)

    register_stanza_plugin(Accept, Jingle)
    register_stanza_plugin(Accept, External)
