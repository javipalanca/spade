
# slixmpp.xmlstream.handler.base
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from __future__ import annotations

import weakref
from weakref import ReferenceType
from typing import Optional, TYPE_CHECKING, Union
from slixmpp.xmlstream.matcher.base import MatcherBase
from xml.etree.ElementTree import Element

if TYPE_CHECKING:
    from slixmpp.xmlstream import XMLStream, StanzaBase


class BaseHandler:

    """
    Base class for stream handlers. Stream handlers are matched with
    incoming stanzas so that the stanza may be processed in some way.
    Stanzas may be matched with multiple handlers.

    Handler execution may take place in two phases: during the incoming
    stream processing, and in the main event loop. The :meth:`prerun()`
    method is executed in the first case, and :meth:`run()` is called
    during the second.

    :param string name: The name of the handler.
    :param matcher: A :class:`~slixmpp.xmlstream.matcher.base.MatcherBase`
                    derived object that will be used to determine if a
                    stanza should be accepted by this handler.
    :param stream: The :class:`~slixmpp.xmlstream.xmlstream.XMLStream`
                    instance that the handle will respond to.
    """
    name: str
    stream: Optional[ReferenceType[XMLStream]]
    _destroy: bool
    _matcher: MatcherBase
    _payload: Optional[StanzaBase]

    def __init__(self, name: str, matcher: MatcherBase, stream: Optional[XMLStream] = None):
        #: The name of the handler
        self.name = name

        #: The XML stream this handler is assigned to
        self.stream = None
        if stream is not None:
            self.stream = weakref.ref(stream)
            stream.register_handler(self)

        self._destroy = False
        self._payload = None
        self._matcher = matcher

    def match(self, xml: StanzaBase) -> bool:
        """Compare a stanza or XML object with the handler's matcher.

        :param xml: An XML or
            :class:`~slixmpp.xmlstream.stanzabase.StanzaBase` object
        """
        return self._matcher.match(xml)

    def prerun(self, payload: StanzaBase) -> None:
        """Prepare the handler for execution while the XML
        stream is being processed.

        :param payload: A :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                        object.
        """
        self._payload = payload

    def run(self, payload: StanzaBase) -> None:
        """Execute the handler after XML stream processing and during the
        main event loop.

        :param payload: A :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                        object.
        """
        self._payload = payload

    def check_delete(self) -> bool:
        """Check if the handler should be removed from the list
        of stream handlers.
        """
        return self._destroy
