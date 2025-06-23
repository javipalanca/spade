# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission
import logging
from asyncio import Event, Task, FIRST_COMPLETED, wait, CancelledError
from enum import Enum
from typing import Optional, Tuple, Union

from slixmpp.stanza import Message, Presence
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.jid import JID
from slixmpp.plugins import BasePlugin
from slixmpp.types import ErrorConditions


log = logging.getLogger(__name__)


class PingStatus(Enum):
    """
    Enum representing the status of a ping.

    - `UNTRIED`: the ping was not sent yet
    - `JOINED`: we were considered still in the MUC at the last ping
    - `JOINED_NICKCHANGED`: we were joined but another client just changed
      the nick.
    - `DISCONNECTED`: we got disconnected
    - `TIMEOUT`: slixmpp was unable to reach the server
    """
    UNTRIED = 0
    JOINED = 1
    JOINED_NICKCHANGED = 1
    DISCONNECTED = 2
    TIMEOUT = 3


class PingTask:
    """
    Class representing a current muc self-ping task.
    """
    _event: Event
    _current_task: Task
    _timeout: float
    _interval: float
    _plugin: 'XEP_0410'

    def __init__(self, muc_resource: JID, orig_jid: JID,
                 plugin: 'XEP_0410', interval: float, timeout: float) -> None:
        self._event = Event()
        self._plugin = plugin
        self._interval = interval
        self._timeout = timeout
        self._current_task = plugin.xmpp.loop.create_task(self.run(
            muc_resource,
            orig_jid,
        ))

    def reset_timer(self) -> None:
        """
        Triggers the internal event to reset the internal timer.
        """
        self._event.set()

    def cancel(self) -> None:
        """Cancel the task before dying"""
        self._current_task.cancel()

    async def run(self, muc_resource: JID, orig_jid: JID) -> None:
        """
        Loop that goes on forever and sends pings at the desired interval.
        """
        while True:
            # Wait on the event or timeout, whichever comes first
            try:
                done, pending = await wait(
                    [self._plugin.xmpp.loop.create_task(self._event.wait())],
                    return_when=FIRST_COMPLETED,
                    timeout=self._interval,
                )
                # If the event is set, then the timer was reset and we clear it
                # before going back to waiting
                if self._event.is_set():
                    self._event.clear()
                    continue
                result = await self._plugin.send_self_ping(
                    muc_resource,
                    orig_jid,
                    timeout=self._timeout,
                )
                key = (muc_resource, orig_jid)
                self._plugin._update_ping_results(key, result)
            except CancelledError:
                return
            except:
                log.exception("Error while trying to ping a muc resource")
                return


class XEP_0410(BasePlugin):

    """
    XEP-0410: MUC Self-Ping (Schrödinger's Chat)

    This plugin provides features for clients (or non-MUC components) to
    enable or disable self-ping.

    Configuration options:

    - `ping_interval`: the number of seconds between the last activity and a ping.

    Ping status is represented using the :class:`~slixmpp.plugins.XEP_0410.PingStatus` class.

    Users of this plugin can either schedule the pings manually and send them
    using `send_self_ping`, or they can use the provided scheduler with
    `enable_self_ping` and `disable_self_ping`.

    Doing so requires calling `update_nick` if your nickname in a MUC changes,
    because the plugin is not aware of this. The scheduled ping will trigger
    a `muc_ping_changed` event in case the ping status changes, which should
    be handled properly.
    """

    name = 'xep_0410'
    description = 'XEP-0410: MUC Self-Ping (Schrödinger\'s Chat)'
    dependencies = {'xep_0045', 'xep_0199'}
    default_config = {
        "ping_interval": 900,
        "ping_timeout": 30,
    }
    ping_interval: Union[int, float]
    # Cache of the last bound JID, to be able to recover if we bind to
    # another resource while running
    boundjid: Optional[JID] = None
    # Dictionary mapping a (muc resource, from jid) to an asyncio task in
    # the process of being executed
    ping_timers: dict[Tuple[JID, JID], PingTask]
    # Cache of the latest ping results
    last_ping_results: dict[Tuple[JID, JID], PingStatus]


    def plugin_init(self):
        self.ping_timers = dict()
        self.boundjid = None
        self.last_ping_results = dict()
        self.xmpp.add_event_handler(
            'groupchat_message',
            self._on_muc_activity
        )
        self.xmpp.add_event_handler(
            'groupchat_presence',
            self._on_muc_activity,
        )

    def plugin_end(self):
        self.ping_timers = dict()
        self.last_ping_results = dict()

    def session_bind(self, jid: JID):
        self.__update_boundjid(jid)

    def __update_boundjid(self, jid: JID):
        """
        If the bound JID has changed, we need to update the timers so that
        the ping stanzas have the correct from value.

        This is a bit painful.
        """
        new_boundjid = jid
        if self.boundjid and self.boundjid != new_boundjid:
            self.ping_results = dict()
            for key, timer in list(self.ping_timers.items()):
                if key[1] == self.boundjid:
                    del self.ping_timers[key]
                    timer.cancel()
                    key = (key[0], new_boundjid)
                    self.ping_timers[key] = PingTask(
                        key[0],
                        key[1],
                        self,
                        timeout=timer.timeout,
                        interval=timer.interval,
                    )
        self.boundjid = jid

    def update_nick(self, previous_jid: JID, new_jid: JID) -> None:
        """
        Update the self-ping targets when a nickname changes.

        :param previous_jid: full JID of the previous MUC resource.
        :param new_jid: full JID of the new MUC resource.
        """
        for key, timer in list(self.ping_timers.items()):
            if key[0] == previous_jid:
                del self.ping_timers[key]
                timer.cancel()
                key = (new_jid, key[1])
                self.ping_timers[key] = PingTask(
                    key[0],
                    key[1],
                    self,
                    timeout=timer.timeout,
                    interval=timer.interval,
                )

    def enable_self_ping(self, muc_resource: JID,
                         orig_jid: Optional[JID] = None,
                         interval: Optional[float] = None,
                         timeout: Optional[float] = None) -> None:
        """
        Enable client self-ping.
        The given MUC resource will be pinged periodically if the MUC is inactive,
        and an event will be generated in case of changes.

        :param muc_resource: The MUC resource to send the ping to.
        :param orig_jid: The "from" resource to send the ping from (for components).
        """
        if orig_jid is None:
            orig_jid = self.xmpp.boundjid
        if timeout is None:
            timeout = self.ping_timeout
        if interval is None:
            interval = self.ping_interval
        key = (muc_resource, orig_jid)
        if key not in self.ping_timers:
            self.ping_timers[key] = PingTask(
                muc_resource=muc_resource,
                orig_jid=orig_jid,
                plugin=self,
                timeout=timeout,
                interval=interval,
            )

    def disable_self_ping(self, muc_resource: JID,
                                 orig_jid: Optional[JID] = None) -> None:
        """
        Disable client self-ping. Cancels the scheduled pings for the given
        MUC resource.

        :param muc_resource: The MUC resource to send the ping to.
        :param orig_jid: The "from" resource the ping was sent from (for components).
        """
        if orig_jid is None:
            orig_jid = self.xmpp.boundjid
        key = (muc_resource, orig_jid)
        if key in self.ping_timers:
            self.ping_timers[key].cancel()
            del self.ping_timers[key]
        if key in self.last_ping_results:
            del self.last_ping_results[key]

    def get_ping_status(self, muc_resource: JID,
                        orig_jid: Optional[JID] = None) -> PingStatus:
        """
        Return the last pinged status for a specific muc resource.

        :param muc_resource: The MUC resource to send the ping to.
        :param orig_jid: The "from" resource the ping was sent from (for components).
        :return: The status, or None if no ping has been sent yet.
        """
        if orig_jid is None:
            orig_jid = self.xmpp.boundjid
        key = (muc_resource, orig_jid)
        return self.last_ping_results.get(key, PingStatus.UNTRIED)

    def _on_muc_activity(self, event: Union[Presence, Message]):
        """Handle both messages and presences from mucs to see if we need to
        reset the timer"""
        if event['type'] == 'error':
            return
        key = (event['from'], event['to'])
        if key in self.ping_timers:
            self.ping_timers[key].reset_timer()

    def _handle_condition(self, condition: ErrorConditions) -> PingStatus:
        """
        Interpret the error conditions as defined in XEP-0410.
        """
        if condition in ('service-unavailable', 'feature-not-implemented'):
            return PingStatus.JOINED
        elif condition == 'item-not-found':
            return PingStatus.JOINED_NICKCHANGED
        elif condition in ('remote-server-not-found',
                           'remote-server-timeout'):
            return PingStatus.TIMEOUT
        else:
            return PingStatus.DISCONNECTED

    async def send_self_ping(self, muc_resource: JID,
                             orig_jid: Optional[JID] = None,
                             timeout: Optional[float] = None) -> PingStatus:
        """
        Send a single self-ping to a MUC, and return the result.

        :param muc_resource: The MUC resource to send the ping to.
        :param orig_jid: The "from" resource the ping was sent from (for components).
        :return: The ping status
        """
        if orig_jid is None:
            orig_jid = self.xmpp.boundjid
        result = PingStatus.UNTRIED
        try:
            await self.xmpp.plugin['xep_0199'].send_ping(
                muc_resource,
                ifrom=orig_jid,
                timeout=timeout,
            )
            result = PingStatus.JOINED
        except IqTimeout:
            result = PingStatus.TIMEOUT
        except IqError as exc:
            result = self._handle_condition(exc.condition)
        return result

    def _update_ping_results(self, key: Tuple[JID, JID], result: PingStatus) -> None:
        """
        Internal use only: used to update the ping results dict from the timer.
        """
        previous = self.last_ping_results.get(key, PingStatus.UNTRIED)
        self.last_ping_results[key] = result
        if result != previous:
            self.xmpp.event('muc_ping_changed', {
                "key": key,
                "previous": previous,
                "result": result
            })
