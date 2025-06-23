
# slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from typing import Iterable, List, Tuple

from slixmpp.xmlstream import ElementBase, ET

class JingleMessage(ElementBase):
    namespace = 'urn:xmpp:jingle-message:0'
    interfaces = {'id'}

class Propose(JingleMessage):
    name = 'propose'
    plugin_attrib = 'jingle_propose'
    interfaces = {'id', 'descriptions'}

    def get_descriptions(self) -> List[Tuple[str, str]]:
        result = []
        for desc in self.xml:
            namespace = desc.tag.split('}')[0][1:]
            media = desc.attrib['media']
            result.append((namespace, media))
        return result

    def set_descriptions(self, descriptions: Iterable[Tuple[str, str]]):
        self.del_descriptions()
        for namespace, media in descriptions:
            desc = ET.Element('{%s}description' % namespace)
            desc.attrib['media'] = media
            self.xml.append(desc)

    def del_descriptions(self):
        for desc in self.xml.findall('{*}description'):
            self.xml.remove(desc)

class Retract(JingleMessage):
    name = 'retract'
    plugin_attrib = 'jingle_retract'

class Accept(JingleMessage):
    name = 'accept'
    plugin_attrib = 'jingle_accept'

class Proceed(JingleMessage):
    name = 'proceed'
    plugin_attrib = 'jingle_proceed'

class Reject(JingleMessage):
    name = 'reject'
    plugin_attrib = 'jingle_reject'
