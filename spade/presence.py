from enum import Enum
from typing import Dict, Optional, Union

from slixmpp import JID
from slixmpp.stanza import Presence


class ContactNotFound(Exception):
    """ """
    pass


class PresenceShow(Enum):
    """
    Enum that contains the possible show values to append in the presence stanzas
    """
    EXTENDED_AWAY = 'xa'
    AWAY = 'away'
    CHAT = 'chat'
    DND = 'dnd'
    NONE = None


class PresenceType(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    ERROR = 'error'
    PROBE = 'probe'
    SUBSCRIBE = 'subscribe'
    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBE = 'unsubscribe'
    UNSUBSCRIBED = 'unsubscribed'


class PresenceManager(object):
    """ """

    def __init__(self, agent):
        self.agent = agent
        self.client = agent.client

        self._contacts = {}

        self.approve_all = False

        self.current_available: Union[bool, None] = None
        self.current_status: Union[Dict[str, str], None] = None
        self.current_show: PresenceShow = PresenceShow.NONE
        self.current_priority: int = 0

        self.client.add_event_handler('presence_available', self._on_available)
        self.client.add_event_handler('presence_unavailable', self._on_unavailable)
        self.client.add_event_handler('changed_status', self._on_changed)

        self.client.add_event_handler('presence_subscribe', self._on_subscribe)
        self.client.add_event_handler('presence_subscribed', self._on_subscribed)
        self.client.add_event_handler('presence_unsubscribe', self._on_unsubscribe)
        self.client.add_event_handler('presence_unsubscribed', self._on_unsubscribed)

    @property
    def available(self) -> bool:
        """
        Availability property. A boolean value that indicates internally
        if a client is available or not.

        :return: The availability of the client
        """
        return self.current_available

    @property
    def status(self) -> Union[Dict[str, str], None]:
        """
        State property. A human-readable string value appended to the presence stanza
        indicating a more detailed presence state

        :return: The availability of the client
        """
        return self.current_status

    @property
    def show(self) -> PresenceShow:
        """
        Show property. A more specific availability value.
        Used internally by the client/server. Not human-readable

        :return: A value of PresenceShow
        """
        return self.current_show

    @property
    def priority(self) -> int:
        """
        Priority property of the presence stanzas sent by the client

        :return: An integer between the values -128 and 127
        (range defined in the RFC 6121)
        """
        return self.current_priority

    def is_available(self) -> bool:
        """
        :return: The availability of the client
        """
        return self.current_available

    def set_available(self, show: Optional[PresenceShow] = PresenceShow.NONE, status: Optional[str] = None):
        """
        Sets the agent availability to True.

        Args:
          show (spade.PresenceShow, optional): the show state of the presence (Default value = PresenceShow.NONE)
          status (string): The human-readable status

        """
        self.current_available = True
        self.current_show = show if show is not None else self.current_show
        self.current_status = status if status is not None else self.current_status

    def set_unavailable(self, show: Optional[PresenceShow] = PresenceShow.NONE, status: Optional[str] = None) -> None:
        """Sets the agent availability to False."""
        self.client.current_state = False
        self.current_show = show if show is not None else self.current_show
        self.current_status = status if status is not None else self.current_status

    def set_presence(
        self,
        show: Optional[PresenceShow] = PresenceShow.NONE,
        status: Optional[str] = None,
        priority: Optional[int] = None,
    ):
        """
        Change the presence broadcast by the client.
        If the client is currently connected, the new presence is broadcast immediately.

        Args:
          show(PresenceShow, optional): New presence state to broadcast (Default value = None)
          status(dict or str, optional): New status information to broadcast (Default value = None)
          priority (int, optional): New priority for the resource (Default value = None)

        """
        if status is not None:
            if type(status) is str:
                self.current_status = {None: status}
            elif type(status) is dict:
                self.current_status = status

        self.current_show = show if show is not None else self.current_show
        self.current_priority = priority if priority is not None else self.current_priority
        self.client.send_presence(
            pshow=show.value if show is not None else None,
            pstatus=status,
            ppriority=priority,
            ptype='unavailable' if self.current_available is None or not self.current_available else None
        )

    def get_contacts(self) -> Dict[str, Dict]:
        """
        Returns list of contacts

        Returns:
          dict: the roster of contacts

        """
        for jid, item in dict(self.client.client_roster).items():
            try:
                self._contacts[JID(jid).bare].update(item._state)
            except KeyError:
                self._contacts[JID(jid).bare] = item

        return self._contacts

    def get_contact(self, jid: JID) -> Dict:
        """
        Returns a contact

        Args:
          jid (JID): jid of the contact

        Returns:
          dict: the roster of contacts

        """
        if type(jid) is not JID:
            raise AttributeError("jid must be an JID")

        try:
            return self.get_contacts()[jid.bare]
        except KeyError:
            raise ContactNotFound

    def _update_roster_with_presence(self, stanza: Presence) -> None:
        """ """
        if stanza['from'].bare == self.agent.jid.bare:
            return
        try:
            self._contacts[stanza['from'].bare].update({"presence": stanza})
        except KeyError:
            self._contacts[stanza['from'].bare] = {"presence": stanza}

    def subscribe(self, peer_jid: str) -> None:
        """
        Asks for subscription

        Args:
          peer_jid (str): the JID you ask for subscriptiion

        """
        self.client.send_presence_subscription(
            pto=JID(peer_jid).bare,
            ptype='subscribe'
        )

    def unsubscribe(self, peer_jid: str) -> None:
        """
        Asks for unsubscription

        Args:
          peer_jid (str): the JID you ask for unsubscriptiion

        """
        self.client.send_presence_subscription(
            pto=JID(peer_jid).bare,
            ptype='unsubscribe'
        )

    def approve(self, peer_jid: str) -> None:
        """
        Approve a subscription request from jid

        Args:
          peer_jid (str): the JID to approve

        """
        self.client.send_presence_subscription(
            pto=JID(peer_jid).bare,
            ptype='subscribed'
        )

    def _on_available(self, stanza: Presence) -> None:
        """ """
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza['from']), stanza)

    def _on_unavailable(self, stanza: Presence) -> None:
        """ """
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza['from']), stanza)

    def _on_changed(self, stanza: Presence) -> None:
        """ """
        self._update_roster_with_presence(stanza)

    def _on_subscribe(self, stanza: Presence) -> None:
        """ """
        if self.approve_all:
            self.client.send_presence_subscription(
                pto=JID(stanza['from'].bare).bare,
                ptype='subscribed'
            )
        else:
            self.on_subscribe(str(stanza['from']))

    def _on_subscribed(self, stanza: Presence) -> None:
        """ """
        self.on_subscribed(str(stanza['from']))

    def _on_unsubscribe(self, stanza: Presence) -> None:
        """ """
        if self.approve_all:
            self.client.send_presence_subscription(
                pto=JID(stanza['from']).bare,
                ptype='unsubscribed'
            )
        else:
            self.on_unsubscribe(str(stanza['from']))

    def _on_unsubscribed(self, stanza: Presence) -> None:
        """ """
        self.on_unsubscribed(str(stanza['from']))

    def on_subscribe(self, peer_jid: str) -> None:
        """
        Callback called when a subscribe query is received.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent asking for subscription

        """
        pass  # pragma: no cover

    def on_subscribed(self, peer_jid: str) -> None:
        """
        Callback called when a subscribed message is received.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that accepted subscription

        """
        pass  # pragma: no cover

    def on_unsubscribe(self, peer_jid: str) -> None:
        """
        Callback called when an unsubscribe query is received.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent asking for unsubscription

        """
        pass  # pragma: no cover

    def on_unsubscribed(self, peer_jid: str) -> None:
        """
        Callback called when an unsubscribed message is received.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that unsubscribed

        """
        pass  # pragma: no cover

    def on_available(self, peer_jid: str, stanza: Presence) -> None:
        """
        Callback called when a contact becomes available.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that is available
          stanza (slixmpp.stanza.Presence): The presence message containing type, show, priority and status values.

        """
        pass  # pragma: no cover

    def on_unavailable(self, peer_jid: str, stanza: Presence) -> None:
        """
        Callback called when a contact becomes unavailable.
        To be overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that is unavailable
          stanza (slixmpp.stanza.Presence): The presence message containing type, show, priority and status values.

        """
        pass  # pragma: no cover
