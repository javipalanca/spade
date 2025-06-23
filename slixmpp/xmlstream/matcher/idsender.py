
# slixmpp.xmlstream.matcher.id
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details

from slixmpp.xmlstream.matcher.base import MatcherBase
from slixmpp.xmlstream.stanzabase import StanzaBase
from slixmpp.jid import JID
from slixmpp.types import TypedDict

from typing import Dict


class CriteriaType(TypedDict):
    self: JID
    peer: JID
    id: str


class MatchIDSender(MatcherBase):

    """
    The IDSender matcher selects stanzas that have the same stanza 'id'
    interface value as the desired ID, and that the 'from' value is one
    of a set of approved entities that can respond to a request.
    """
    _criteria: CriteriaType

    def match(self, xml: StanzaBase) -> bool:
        """Compare the given stanza's ``'id'`` attribute to the stored
        ``id`` value, and verify the sender's JID.

        :param xml: The :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                    stanza to compare against.
        """

        selfjid = self._criteria['self']
        peerjid = self._criteria['peer']

        allowed: Dict[str, bool] = {}
        allowed[''] = True
        allowed[selfjid.bare] = True
        allowed[selfjid.domain] = True
        allowed[peerjid.full] = True
        allowed[peerjid.bare] = True
        allowed[peerjid.domain] = True

        _from = xml['from']

        try:
            return xml['id'] == self._criteria['id'] and allowed[_from]
        except KeyError:
            return False
