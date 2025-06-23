
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Erik Reuterborg Larsson
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from collections.abc import AsyncIterator
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)

from slixmpp.stanza import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.xep_0059 import stanza, Set
from slixmpp.exceptions import XMPPError


log = logging.getLogger(__name__)


class ResultIterator(AsyncIterator):

    """
    An iterator for Result Set Management

    Example:

    .. code-block:: python

       q = Iq()
       q['to'] = 'pubsub.example.com'
       q['disco_items']['node'] = 'blog'
       async for i in ResultIterator(q, 'disco_items', '10'):
           print(i['disco_items']['items'])

    """
    #: Template for the RSM query
    query: Iq
    #: Substanza of the query to send, e.g. "disco_items"
    interface: str
    #: Stanza interface on the query results providing the retrieved
    #: elements (used to count them)
    results: str
    #: From which item id to start
    start: Optional[str]
    #: Amount of elements to retrieve for each page
    amount: int
    #: If True, page backwards through the results
    reverse: bool
    #: Callback to run before sending the stanza
    pre_cb: Optional[Callable[[Iq], None]]
    #: Callback to run after receiving the reply
    post_cb: Optional[Callable[[Iq], None]]
    #: Optional dict of Iq options (timeout, etc…) for Iq.send()
    iq_options: Dict[str, Any]

    def __init__(self, query: Iq, interface: str, results: str = 'substanzas',
                 amount: int = 10,
                 start: Optional[str] = None, reverse: bool = False,
                 recv_interface: Optional[str] = None,
                 pre_cb: Optional[Callable[[Iq], None]] = None,
                 post_cb: Optional[Callable[[Iq], None]] = None,
                 iq_options: Optional[Dict[str, Any]] = None):
        """
        :param query: The template query
        :param interface: The substanza of the query to send, for example
                          disco_items
        :param recv_interface: The substanza of the query to receive, for
                               example disco_items
        :param results: The query stanza's interface which provides a
                        countable list of query results.
        :param amount: The max amounts of items to request per iteration
        :param start: From which item id to start
        :param reverse: If True, page backwards through the results
        :param pre_cb: Callback to run before sending the stanza
        :param post_cb: Callback to run after receiving the reply
        :param iq_options: Optional dict of parameters for Iq.send
        """
        self.query = query
        self.amount = amount
        self.start = start
        if iq_options is None:
            self.iq_options = {}
        else:
            self.iq_options = iq_options
        self.interface = interface
        if recv_interface is not None:
            self.recv_interface = recv_interface
        else:
            self.recv_interface = interface
        self.pre_cb = pre_cb
        self.post_cb = post_cb
        self.results = results
        self.reverse = reverse
        self._stop = False

    def __aiter__(self):
        return self

    async def __anext__(self) -> Iq:
        return await self.next()

    async def next(self) -> Iq:
        """
        Return the next page of results from a query.

        Note: If using backwards paging, then the next page of
              results will be the items before the current page
              of items.
        """
        if self._stop:
            raise StopAsyncIteration
        self.query['id'] = self.query.stream.new_id()
        self.query[self.interface]['rsm']['max'] = str(self.amount)

        if self.start:
            if self.reverse:
                self.query[self.interface]['rsm']['before'] = self.start
            else:
                self.query[self.interface]['rsm']['after'] = self.start
        elif self.reverse:
                self.query[self.interface]['rsm']['before'] = True

        try:
            if self.pre_cb:
                self.pre_cb(self.query)
            r = await self.query.send(**self.iq_options)

            if not r[self.recv_interface]['rsm']['first'] and \
               not r[self.recv_interface]['rsm']['last']:
                raise StopAsyncIteration

            if self.post_cb:
                self.post_cb(r)

            if r[self.recv_interface]['rsm']['count'] and \
               r[self.recv_interface]['rsm']['first_index']:
                count = int(r[self.recv_interface]['rsm']['count'])
                first = int(r[self.recv_interface]['rsm']['first_index'])
                num_items = len(r[self.recv_interface][self.results])
                if first + num_items == count:
                    self._stop = True

            if self.reverse:
                self.start = r[self.recv_interface]['rsm']['first']
            else:
                self.start = r[self.recv_interface]['rsm']['last']
            return r
        except XMPPError:
            raise StopAsyncIteration


class XEP_0059(BasePlugin):

    """
    XEP-0059: Result Set Management
    """

    name = 'xep_0059'
    description = 'XEP-0059: Result Set Management'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        """
        Start the XEP-0059 plugin.
        """
        register_stanza_plugin(self.xmpp['xep_0030'].stanza.DiscoItems,
                               self.stanza.Set)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Set.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Set.namespace)

    def iterate(self, stanza: Iq, interface: str, results: str = 'substanzas',
                amount: int = 10, reverse: bool = False,
                recv_interface: Optional[str] = None,
                pre_cb: Optional[Callable[[Iq], None]] = None,
                post_cb: Optional[Callable[[Iq], None]] = None,
                iq_options: Optional[Dict[str, Any]] = None
                ) -> ResultIterator:
        """
        Create a new result set iterator for a given stanza query.

        :param stanza: A stanza object to serve as a template for
                        queries made each iteration. For example, a
                        basic disco#items query.
        :param interface: The name of the substanza to which the
                          result set management stanza should be
                          appended in the query stanza. For example,
                          for disco#items queries the interface
                          'disco_items' should be used.
        :param recv_interface: The name of the substanza from which the
                               result set management stanza should be
                               read in the result stanza. If unspecified,
                               it will be set to the same value as the
                               ``interface`` parameter.
        :param pre_cb: Callback to run before sending each stanza e.g.
                       setting the MAM queryid and starting a stanza
                       collector.
        :param post_cb: Callback to run after receiving each stanza e.g.
                        stopping a MAM stanza collector in order to
                        gather results.
        :param results: The name of the interface containing the
                        query results (typically just 'substanzas').
        :param iq_options: Optional dict of parameters for Iq.send
        """
        return ResultIterator(stanza, interface, results, amount,
                              reverse=reverse, recv_interface=recv_interface,
                              pre_cb=pre_cb, post_cb=post_cb,
                              iq_options=iq_options)
