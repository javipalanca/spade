# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from xml.parsers.expat import ExpatError
from xml.etree.ElementTree import Element

from slixmpp.xmlstream.stanzabase import ET, StanzaBase
from slixmpp.xmlstream.matcher.base import MatcherBase


log = logging.getLogger(__name__)


class MatchXMLMask(MatcherBase):

    """
    The XMLMask matcher selects stanzas whose XML matches a given
    XML pattern, or mask. For example, message stanzas with body elements
    could be matched using the mask:

    .. code-block:: xml

        <message xmlns="jabber:client"><body /></message>

    Use of XMLMask is discouraged, and
    :class:`~slixmpp.xmlstream.matcher.xpath.MatchXPath` or
    :class:`~slixmpp.xmlstream.matcher.stanzapath.StanzaPath`
    should be used instead.

    :param criteria: Either an :class:`~xml.etree.ElementTree.Element` XML
                     object or XML string to use as a mask.
    """
    _criteria: Element

    def __init__(self, criteria: str, default_ns: str = 'jabber:client'):
        MatcherBase.__init__(self, criteria)
        if isinstance(criteria, str):
            self._criteria = ET.fromstring(criteria)
        self.default_ns = default_ns

    def setDefaultNS(self, ns: str) -> None:
        """Set the default namespace to use during comparisons.

        :param ns: The new namespace to use as the default.
        """
        self.default_ns = ns

    def match(self, xml: StanzaBase) -> bool:
        """Compare a stanza object or XML object against the stored XML mask.

        Overrides MatcherBase.match.

        :param xml: The stanza object or XML object to compare against.
        """
        real_xml = xml.xml
        return self._mask_cmp(real_xml, self._criteria, True)

    def _mask_cmp(self, source: Element, mask: Element, use_ns: bool = False,
                  default_ns: str = '__no_ns__') -> bool:
        """Compare an XML object against an XML mask.

        :param source: The :class:`~xml.etree.ElementTree.Element` XML object
                       to compare against the mask.
        :param mask: The :class:`~xml.etree.ElementTree.Element` XML object
                     serving as the mask.
        :param use_ns: Indicates if namespaces should be respected during
                       the comparison.
        :default_ns: The default namespace to apply to elements that
                     do not have a specified namespace.
                     Defaults to ``"__no_ns__"``.
        """
        if source is None:
            # If the element was not found. May happen during recursive calls.
            return False

        mask_ns_tag = "{%s}%s" % (self.default_ns, mask.tag)
        if source.tag not in [mask.tag, mask_ns_tag]:
            return False

        # If the mask includes text, compare it.
        if mask.text and source.text and \
           source.text.strip() != mask.text.strip():
            return False

        # Compare attributes. The stanza must include the attributes
        # defined by the mask, but may include others.
        for name, value in mask.attrib.items():
            if source.attrib.get(name, "__None__") != value:
                return False

        # Recursively check subelements.
        matched_elements = {}
        for subelement in mask:
            matched = False
            for other in source.findall(subelement.tag):
                matched_elements[other] = False
                if self._mask_cmp(other, subelement, use_ns):
                    if not matched_elements.get(other, False):
                        matched_elements[other] = True
                        matched = True
            if not matched:
                return False

        # Everything matches.
        return True
