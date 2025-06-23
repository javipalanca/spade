
# slixmpp.xmlstream.matcher.stanzapath
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from typing import cast, List
from slixmpp.xmlstream.matcher.base import MatcherBase
from slixmpp.xmlstream.stanzabase import fix_ns, StanzaBase


class StanzaPath(MatcherBase):

    """
    The StanzaPath matcher selects stanzas that match a given "stanza path",
    which is similar to a normal XPath except that it uses the interfaces and
    plugins of the stanza instead of the actual, underlying XML.

    :param criteria: Object to compare some aspect of a stanza against.
    """
    _criteria: List[str]
    _raw_criteria: str

    def __init__(self, criteria: str):
        self._criteria = cast(
            List[str],
            fix_ns(
                criteria, split=True, propagate_ns=False,
                default_ns='jabber:client'
            )
        )
        self._raw_criteria = criteria

    def match(self, stanza: StanzaBase) -> bool:
        """
        Compare a stanza against a "stanza path". A stanza path is similar to
        an XPath expression, but uses the stanza's interfaces and plugins
        instead of the underlying XML. See the documentation for the stanza
        :meth:`~slixmpp.xmlstream.stanzabase.StanzaBase.match()` method
        for more information.

        :param stanza: The :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                       stanza to compare against.
        """
        return stanza.match(self._criteria) or stanza.match(self._raw_criteria)
