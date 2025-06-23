
# slixmpp.xmlstream.matcher.id
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from slixmpp.xmlstream.matcher.base import MatcherBase
from slixmpp.xmlstream.stanzabase import StanzaBase


class MatcherId(MatcherBase):

    """
    The ID matcher selects stanzas that have the same stanza 'id'
    interface value as the desired ID.
    """
    _criteria: str

    def match(self, xml: StanzaBase) -> bool:
        """Compare the given stanza's ``'id'`` attribute to the stored
        ``id`` value.

        :param xml: The :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                    stanza to compare against.
        """
        return bool(xml['id'] == self._criteria)
