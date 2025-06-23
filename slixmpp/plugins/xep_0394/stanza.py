
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase, register_stanza_plugin, ET


class Markup(ElementBase):
    namespace = 'urn:xmpp:markup:0'
    name = 'markup'
    plugin_attrib = 'markup'


class _FirstLevel(ElementBase):
    namespace = 'urn:xmpp:markup:0'
    interfaces = {'start', 'end'}

    def get_start(self):
        return int(self._get_attr('start'))

    def set_start(self, value):
        self._set_attr('start', '%d' % value)

    def get_end(self):
        return int(self._get_attr('end'))

    def set_end(self, value):
        self._set_attr('end', '%d' % value)

class Span(_FirstLevel):
    name = 'span'
    plugin_attrib = 'span'
    plugin_multi_attrib = 'spans'
    interfaces = {'start', 'end', 'types'}

    def get_types(self):
        types = []
        if self.xml.find('{urn:xmpp:markup:0}emphasis') is not None:
            types.append('emphasis')
        if self.xml.find('{urn:xmpp:markup:0}code') is not None:
            types.append('code')
        if self.xml.find('{urn:xmpp:markup:0}deleted') is not None:
            types.append('deleted')
        return types

    def set_types(self, value):
        del self['types']
        for type_ in value:
            if type_ == 'emphasis':
                self.xml.append(ET.Element('{urn:xmpp:markup:0}emphasis'))
            elif type_ == 'code':
                self.xml.append(ET.Element('{urn:xmpp:markup:0}code'))
            elif type_ == 'deleted':
                self.xml.append(ET.Element('{urn:xmpp:markup:0}deleted'))

    def det_types(self):
        for child in self.xml:
            self.xml.remove(child)


class _SpanType(ElementBase):
    namespace = 'urn:xmpp:markup:0'


class EmphasisType(_SpanType):
    name = 'emphasis'
    plugin_attrib = 'emphasis'


class CodeType(_SpanType):
    name = 'code'
    plugin_attrib = 'code'


class DeletedType(_SpanType):
    name = 'deleted'
    plugin_attrib = 'deleted'


class BlockCode(_FirstLevel):
    name = 'bcode'
    plugin_attrib = 'bcode'
    plugin_multi_attrib = 'bcodes'


class List(_FirstLevel):
    name = 'list'
    plugin_attrib = 'list'
    plugin_multi_attrib = 'lists'
    interfaces = {'start', 'end', 'li'}


class Li(ElementBase):
    namespace = 'urn:xmpp:markup:0'
    name = 'li'
    plugin_attrib = 'li'
    plugin_multi_attrib = 'lis'
    interfaces = {'start'}

    def get_start(self):
        return int(self._get_attr('start'))

    def set_start(self, value):
        self._set_attr('start', '%d' % value)


class BlockQuote(_FirstLevel):
    name = 'bquote'
    plugin_attrib = 'bquote'
    plugin_multi_attrib = 'bquotes'

register_stanza_plugin(Markup, Span, iterable=True)
register_stanza_plugin(Markup, BlockCode, iterable=True)
register_stanza_plugin(Markup, List, iterable=True)
register_stanza_plugin(Markup, BlockQuote, iterable=True)
register_stanza_plugin(Span, EmphasisType)
register_stanza_plugin(Span, CodeType)
register_stanza_plugin(Span, DeletedType)
register_stanza_plugin(List, Li, iterable=True)
