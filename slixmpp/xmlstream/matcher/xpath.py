
# slixmpp.xmlstream.matcher.xpath
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from typing import cast
from slixmpp.xmlstream.stanzabase import ET, fix_ns, StanzaBase
from slixmpp.xmlstream.matcher.base import MatcherBase


class MatchXPath(MatcherBase):

    """
    The XPath matcher selects stanzas whose XML contents matches a given
    XPath expression.

    If the value of :data:`IGNORE_NS` is set to ``True``, then XPath
    expressions will be matched without using namespaces.
    """
    _criteria: str

    def __init__(self, criteria: str):
        self._criteria = cast(str, fix_ns(criteria))

    def match(self, xml: StanzaBase) -> bool:
        """
        Compare a stanza's XML contents to an XPath expression.

        If the value of :data:`IGNORE_NS` is set to ``True``, then XPath
        expressions will be matched without using namespaces.

        :param xml: The :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                    stanza to compare against.
        """
        real_xml = xml.xml
        x = ET.Element('x')
        x.append(real_xml)

        return x.find(self._criteria) is not None
