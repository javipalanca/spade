
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import asyncio
import time
import logging

from asyncio import Future
from typing import Optional, Callable, List

from slixmpp.jid import JID
from slixmpp.stanza import Iq
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0199 import stanza, Ping


log = logging.getLogger(__name__)


class XEP_0199(BasePlugin):

    """
    XEP-0199: XMPP Ping

    Given that XMPP is based on TCP connections, it is possible for the
    underlying connection to be terminated without the application's
    awareness. Ping stanzas provide an alternative to whitespace based
    keepalive methods for detecting lost connections.

    Also see <http://www.xmpp.org/extensions/xep-0199.html>.

    Attributes:
        keepalive -- If True, periodically send ping requests
                     to the server. If a ping is not answered,
                     the connection will be reset.
        interval  -- Time in seconds between keepalive pings.
                     Defaults to 300 seconds.
        timeout   -- Time in seconds to wait for a ping response.
                     Defaults to 30 seconds.
    Methods:
        send_ping -- Send a ping to a given JID, returning the
                     round trip time.
    """

    name = 'xep_0199'
    description = 'XEP-0199: XMPP Ping'
    dependencies = {'xep_0030'}
    stanza = stanza
    default_config = {
        'keepalive': False,
        'interval': 300,
        'timeout': 30
    }

    def plugin_init(self):
        """
        Start the XEP-0199 plugin.
        """
        register_stanza_plugin(Iq, Ping)

        self.__pending_futures: List[Future] = []

        self.xmpp.register_handler(
                Callback('Ping',
                         StanzaPath('iq@type=get/ping'),
                         self._handle_ping))

        if self.keepalive:
            self.xmpp.add_event_handler('session_start',
                                        self.enable_keepalive)
            self.xmpp.add_event_handler('session_resumed',
                                        self.enable_keepalive)
            self.xmpp.add_event_handler('disconnected',
                                        self.disable_keepalive)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Ping.namespace)
        self.xmpp.remove_handler('Ping')
        if self.keepalive:
            self.xmpp.del_event_handler('session_start',
                                        self.enable_keepalive)
            self.xmpp.del_event_handler('session_resumed',
                                        self.enable_keepalive)
            self.xmpp.del_event_handler('disconnected',
                                        self.disable_keepalive)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Ping.namespace)

    def _clear_pending_futures(self):
        """Cancel all pending ping futures"""
        if self.__pending_futures:
            log.debug('Clearing %s pdnding pings', len(self.__pending_futures))
            for future in self.__pending_futures:
                future.cancel()
            self.__pending_futures.clear()

    def enable_keepalive(self, interval: Optional[float] = None,
                         timeout: Optional[float] = None) -> None:
        """
        Enable the ping keepalive on the connection.
        The plugin will send a ping at `interval` and reconnect if the ping
        timeouts.

        :param interval: The interval between each ping
        :param timeout: The timeout of the ping
        """
        if interval:
            self.interval = interval
        if timeout:
            self.timeout = timeout

        self.keepalive = True

        def handler(event=None):
            # Cleanup futures
            if self.__pending_futures:
                tmp_futures = []
                for future in self.__pending_futures[:]:
                    if not future.done():
                        tmp_futures.append(future)
                self.__pending_futures = tmp_futures

            future = asyncio.ensure_future(
                self._keepalive(event),
                loop=self.xmpp.loop,
            )
            self.__pending_futures.append(future)
        self.xmpp.schedule('Ping keepalive',
                           self.interval,
                           handler,
                           repeat=True)

    def disable_keepalive(self, event=None):
        self._clear_pending_futures()
        self.xmpp.cancel_schedule('Ping keepalive')

    session_end = disable_keepalive

    async def _keepalive(self, event=None):
        log.debug("Keepalive ping...")
        try:
            ifrom = None
            if self.xmpp.is_component:
                ifrom = self.xmpp.boundjid
            rtt = await self.ping(
                self.xmpp.boundjid.host,
                timeout=self.timeout,
                ifrom=ifrom
            )
        except IqTimeout:
            log.debug("Did not receive ping back in time. " +
                      "Requesting Reconnect.")
            self.xmpp.reconnect(0.0, "Ping timeout after %ds" % self.timeout)
        else:
            log.debug('Keepalive RTT: %s' % rtt)

    def _handle_ping(self, iq):
        """Automatically reply to ping requests."""
        log.debug("Pinged by %s", iq['from'])
        iq.reply().send()

    def send_ping(self, jid: JID, ifrom: Optional[JID] = None,
                  timeout: Optional[float] = None,
                  callback: Optional[Callable] = None) -> Future[Iq]:
        """Send a ping request.

        :param jid: The JID that will receive the ping.
        """
        if not timeout:
            timeout = self.timeout

        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['to'] = jid
        iq['from'] = ifrom
        iq.enable('ping')

        return iq.send(timeout=timeout, callback=callback)

    async def ping(self, jid: Optional[JID] = None,
                   ifrom: Optional[JID] = None,
                   timeout: Optional[float] = None) -> float:
        """Send a ping request and calculate RTT.
        This is a coroutine.

        :param jid: The JID that will receive the ping.
        :raises IqError: When the remote entity answered an error
        :raises IqTimeout: When the remote entity did not answer
        """
        own_host = False
        if not jid:
            if self.xmpp.is_component:
                jid = self.xmpp.server
            else:
                jid = self.xmpp.boundjid.host
        jid = JID(jid)
        if jid == self.xmpp.boundjid.host or \
                self.xmpp.is_component and jid == self.xmpp.server:
            own_host = True

        if not timeout:
            timeout = self.timeout

        start = time.time()

        log.debug('Pinging %s', jid)
        try:
            await self.send_ping(jid, ifrom=ifrom, timeout=timeout)
        except IqError as e:
            if own_host:
                rtt = time.time() - start
                log.debug('Pinged %s, RTT: %s', jid, rtt)
                return rtt
            else:
                raise e
        else:
            rtt = time.time() - start
            log.debug('Pinged %s, RTT: %s', jid, rtt)
            return rtt
