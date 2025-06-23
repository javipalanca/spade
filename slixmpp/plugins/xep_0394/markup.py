
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.stanza import Message
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin, ET, tostring
from slixmpp.plugins.xep_0394 import stanza, Markup, Span, BlockCode, List, Li, BlockQuote
from slixmpp.plugins.xep_0071 import XHTML_IM


class Start:
    def __init__(self, elem):
        self.elem = elem

    def __repr__(self):
        return 'Start(%s)' % self.elem


class End:
    def __init__(self, elem):
        self.elem = elem

    def __repr__(self):
        return 'End(%s)' % self.elem


class XEP_0394(BasePlugin):

    name = 'xep_0394'
    description = 'XEP-0394: Message Markup'
    dependencies = {'xep_0030', 'xep_0071'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Message, Markup)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(feature=Markup.namespace)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Markup.namespace)

    @staticmethod
    def _split_first_level(body, markup_elem):
        split_points = []
        elements = {}
        for markup in markup_elem['substanzas']:
            start = markup['start']
            end = markup['end']
            split_points.append(start)
            split_points.append(end)
            elements.setdefault(start, []).append(Start(markup))
            elements.setdefault(end, []).append(End(markup))
            if isinstance(markup, List):
                lis = markup['lis']
                for i, li in enumerate(lis):
                    start = li['start']
                    split_points.append(start)
                    li_end = lis[i + 1]['start'] if i < len(lis) - 1 else end
                    elements.setdefault(li_end, []).append(End(li))
                    elements.setdefault(start, []).append(Start(li))
        split_points = set(split_points)
        new_body = [[]]
        for i, letter in enumerate(body + '\x00'):
            if i in split_points:
                body_elements = []
                for elem in elements[i]:
                    body_elements.append(elem)
                new_body.append(body_elements)
                new_body.append([])
            new_body[-1].append(letter)
        new_body[-1] = new_body[-1][:-1]
        final = []
        for chunk in new_body:
            if not chunk:
                continue
            final.append(''.join(chunk) if isinstance(chunk[0], str) else chunk)
        return final

    def to_plain_text(self, body, markup_elem):
        chunks = self._split_first_level(body, markup_elem)
        final = []
        for chunk in chunks:
            if isinstance(chunk, str):
                final.append(chunk)
        return ''.join(final)

    def to_xhtml_im(self, body, markup_elem):
        chunks = self._split_first_level(body, markup_elem)
        final = []
        stack = []
        for chunk in chunks:
            if isinstance(chunk, str):
                chunk = (chunk.replace("&", '&amp;')
                              .replace('<', '&lt;')
                              .replace('>', '&gt;')
                              .replace('"', '&quot;')
                              .replace("'", '&apos;')
                              .replace('\n', '<br/>'))
                final.append(chunk)
                continue
            num_end = 0
            for elem in chunk:
                if isinstance(elem, End):
                    num_end += 1

            for i in range(num_end):
                stack_top = stack.pop()
                for elem in chunk:
                    if not isinstance(elem, End):
                        continue
                    elem = elem.elem
                    if elem is stack_top:
                        if isinstance(elem, Span):
                            final.append('</span>')
                        elif isinstance(elem, BlockCode):
                            final.append('</code></pre>')
                        elif isinstance(elem, List):
                            final.append('</ul>')
                        elif isinstance(elem, Li):
                            final.append('</li>')
                        elif isinstance(elem, BlockQuote):
                            final.append('</blockquote>')
                        break
                else:
                    assert False
            for elem in chunk:
                if not isinstance(elem, Start):
                    continue
                elem = elem.elem
                stack.append(elem)
                if isinstance(elem, Span):
                    style = []
                    for type_ in elem['types']:
                        if type_ == 'emphasis':
                            style.append('font-style: italic;')
                        if type_ == 'code':
                            style.append('font-family: monospace;')
                        if type_ == 'deleted':
                            style.append('text-decoration: line-through;')
                    final.append("<span style='%s'>" % ' '.join(style))
                elif isinstance(elem, BlockCode):
                    final.append('<pre><code>')
                elif isinstance(elem, List):
                    final.append('<ul>')
                elif isinstance(elem, Li):
                    final.append('<li>')
                elif isinstance(elem, BlockQuote):
                    final.append('<blockquote>')
        p = "<p xmlns='http://www.w3.org/1999/xhtml'>%s</p>" % ''.join(final)
        p2 = ET.fromstring(p)
        print('coucou', p, tostring(p2))
        xhtml_im = XHTML_IM()
        xhtml_im['body'] = p2
        return xhtml_im
