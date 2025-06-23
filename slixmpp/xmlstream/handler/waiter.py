
# slixmpp.xmlstream.handler.waiter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from __future__ import annotations

import logging
from asyncio import Event, wait_for, TimeoutError
from typing import Optional, TYPE_CHECKING, Union
from xml.etree.ElementTree import Element

import slixmpp
from slixmpp.xmlstream.stanzabase import StanzaBase
from slixmpp.xmlstream.handler.base import BaseHandler
from slixmpp.xmlstream.matcher.base import MatcherBase

if TYPE_CHECKING:
    from slixmpp.xmlstream.xmlstream import XMLStream

log = logging.getLogger(__name__)


class Waiter(BaseHandler):

    """
    The Waiter handler allows an event handler to block until a
    particular stanza has been received. The handler will either be
    given the matched stanza, or ``False`` if the waiter has timed out.

    :param string name: The name of the handler.
    :param matcher: A :class:`~slixmpp.xmlstream.matcher.base.MatcherBase`
                    derived object for matching stanza objects.
    :param stream: The :class:`~slixmpp.xmlstream.xmlstream.XMLStream`
                   instance this handler should monitor.
    """
    _event: Event

    def __init__(self, name: str, matcher: MatcherBase, stream: Optional[XMLStream] = None):
        BaseHandler.__init__(self, name, matcher, stream=stream)
        self._event = Event()

    def prerun(self, payload: StanzaBase) -> None:
        """Store the matched stanza when received during processing.

        :param payload: The matched
            :class:`~slixmpp.xmlstream.stanzabase.StanzaBase` object.
        """
        if not self._event.is_set():
            self._event.set()
            self._payload = payload

    def run(self, payload: StanzaBase) -> None:
        """Do not process this handler during the main event loop."""
        pass

    async def wait(self, timeout: Optional[int] = None) -> Optional[StanzaBase]:
        """Block an event handler while waiting for a stanza to arrive.

        Be aware that this will impact performance if called from a
        non-threaded event handler.

        Will return either the received stanza, or ``False`` if the
        waiter timed out.

        :param int timeout: The number of seconds to wait for the stanza
            to arrive. Defaults to the the stream's
            :class:`~slixmpp.xmlstream.xmlstream.XMLStream.response_timeout`
            value.
        """
        stream_ref = self.stream
        if stream_ref is None:
            raise ValueError('wait() called without a stream')
        stream = stream_ref()
        if stream is None:
            raise ValueError('wait() called without a stream')
        if timeout is None:
            timeout = slixmpp.xmlstream.RESPONSE_TIMEOUT

        try:
            await wait_for(
                self._event.wait(), timeout,
            )
        except TimeoutError:
            log.warning("Timed out waiting for %s", self.name)
        stream.remove_handler(self.name)
        return self._payload

    def check_delete(self) -> bool:
        """Always remove waiters after use."""
        return True
