
# slixmpp.xmlstream.handler.collector
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2012 Nathanael C. Fritz, Lance J.T. Stout
# :license: MIT, see LICENSE for more details
from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

from slixmpp.xmlstream.stanzabase import StanzaBase
from slixmpp.xmlstream.handler.base import BaseHandler
from slixmpp.xmlstream.matcher.base import MatcherBase

if TYPE_CHECKING:
    from slixmpp.xmlstream.xmlstream import XMLStream

log = logging.getLogger(__name__)


class Collector(BaseHandler):

    """
    The Collector handler allows for collecting a set of stanzas
    that match a given pattern. Unlike the Waiter handler, a
    Collector does not block execution, and will continue to
    accumulate matching stanzas until told to stop.

    :param string name: The name of the handler.
    :param matcher: A :class:`~slixmpp.xmlstream.matcher.base.MatcherBase`
                    derived object for matching stanza objects.
    :param stream: The :class:`~slixmpp.xmlstream.xmlstream.XMLStream`
                   instance this handler should monitor.
    """
    _stanzas: List[StanzaBase]

    def __init__(self, name: str, matcher: MatcherBase, stream: Optional[XMLStream] = None):
        BaseHandler.__init__(self, name, matcher, stream=stream)
        self._stanzas = []

    def prerun(self, payload: StanzaBase) -> None:
        """Store the matched stanza when received during processing.

        :param payload: The matched
            :class:`~slixmpp.xmlstream.stanzabase.StanzaBase` object.
        """
        self._stanzas.append(payload)

    def run(self, payload: StanzaBase) -> None:
        """Do not process this handler during the main event loop."""
        pass

    def stop(self) -> List[StanzaBase]:
        """
        Stop collection of matching stanzas, and return the ones that
        have been stored so far.
        """
        stream_ref = self.stream
        if stream_ref is None:
            raise ValueError('stop() called without a stream!')
        stream = stream_ref()
        if stream is None:
            raise ValueError('stop() called without a stream!')
        self._destroy = True
        stream.remove_handler(self.name)
        return self._stanzas
