
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Set, Iterable
from slixmpp.xmlstream import ElementBase
try:
    from emoji import is_emoji
except ImportError:
    def is_emoji(*args, **kwargs) -> bool:
        return True


NS = 'urn:xmpp:reactions:0'

class Reactions(ElementBase):
    name = 'reactions'
    plugin_attrib = 'reactions'
    namespace = NS
    interfaces = {'id', 'values'}

    def get_values(self, *, all_chars=False) -> Set[str]:
        """"Get all reactions as str"""
        reactions = set()
        for reaction in self:
            value = reaction['value']
            if all_chars:
                reactions.add(reaction['value'])
            elif is_emoji(value):
                reactions.add(reaction['value'])
        return reactions

    def set_values(self, values: Iterable[str], *, all_chars=False):
        """"Set all reactions as str"""
        for element in self.xml.findall('reaction'):
            self.xml.remove(element)
        for reaction_txt in values:
            reaction = Reaction()
            reaction.set_value(reaction_txt, all_chars=all_chars)
            self.append(reaction)


class Reaction(ElementBase):
    name = 'reaction'
    namespace = NS
    interfaces = {'value'}

    def get_value(self) -> str:
        return self.xml.text

    def set_value(self, value: str, *, all_chars=False):
        if not all_chars and not is_emoji(value):
            raise ValueError("%s is not a valid emoji" % value)
        self.xml.text = value

