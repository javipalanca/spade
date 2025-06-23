# slixmpp.xmlstream.handler.callback
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from __future__ import annotations

from typing import Optional, Callable, Any, TYPE_CHECKING
from slixmpp.xmlstream.handler.base import BaseHandler
from slixmpp.xmlstream.matcher.base import MatcherBase

if TYPE_CHECKING:
    from slixmpp.xmlstream.stanzabase import StanzaBase
    from slixmpp.xmlstream.xmlstream import XMLStream


class Callback(BaseHandler):

    """
    The Callback handler will execute a callback function with
    matched stanzas.

    The handler may execute the callback either during stream
    processing or during the main event loop.

    Callback functions are all executed in the same thread, so be aware if
    you are executing functions that will block for extended periods of
    time. Typically, you should signal your own events using the Slixmpp
    object's :meth:`~slixmpp.xmlstream.xmlstream.XMLStream.event()`
    method to pass the stanza off to a threaded event handler for further
    processing.


    :param string name: The name of the handler.
    :param matcher: A :class:`~slixmpp.xmlstream.matcher.base.MatcherBase`
                    derived object for matching stanza objects.
    :param pointer: The function to execute during callback.
    :param bool once: Indicates if the handler should be used only
                      once. Defaults to False.
    :param bool instream: Indicates if the callback should be executed
                          during stream processing instead of in the
                          main event loop.
    :param stream: The :class:`~slixmpp.xmlstream.xmlstream.XMLStream`
                   instance this handler should monitor.
    """
    _once: bool
    _instream: bool

    def __init__(self, name: str, matcher: MatcherBase,
                 pointer: Callable[[StanzaBase], Any],
                 once: bool = False, instream: bool = False,
                 stream: Optional[XMLStream] = None):
        BaseHandler.__init__(self, name, matcher, stream)
        self._pointer: Callable[[StanzaBase], Any] = pointer
        self._pointer = pointer
        self._once = once
        self._instream = instream

    def prerun(self, payload: StanzaBase) -> None:
        """Execute the callback during stream processing, if
        the callback was created with ``instream=True``.

        :param payload: The matched
            :class:`~slixmpp.xmlstream.stanzabase.StanzaBase` object.
        """
        if self._once:
            self._destroy = True
        if self._instream:
            self.run(payload, True)

    def run(self, payload: StanzaBase, instream: bool = False) -> None:
        """Execute the callback function with the matched stanza payload.

        :param payload: The matched
            :class:`~slixmpp.xmlstream.stanzabase.StanzaBase` object.
        :param bool instream: Force the handler to execute during stream
                              processing. This should only be used by
                              :meth:`prerun()`. Defaults to ``False``.
        """
        if not self._instream or instream:
            self._pointer(payload)
            if self._once:
                self._destroy = True
                del self._pointer
