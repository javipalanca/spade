from enum import Enum
from typing import Dict, Optional, Union

from slixmpp import JID
from slixmpp.stanza import Presence


class ContactNotFound(Exception):
    pass


class PresenceShow(Enum):
    EXTENDED_AWAY = 'xa'
    AWAY = 'away'
    CHAT = 'chat'
    DND = 'dnd'
    NONE = 'none'


class PresenceType(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    ERROR = 'error'
    PROBE = 'probe'
    SUBSCRIBE = 'subscribe'
    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBE = 'unsubscribe'
    UNSUBSCRIBED = 'unsubscribed'


class SubscriptionAsk(Enum):
    NONE = 'none'
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'

class PresenceInfo:
    def __init__(self, presence_type: PresenceType, show: PresenceShow, status: Optional[str], priority: int):
        self.type = presence_type
        self.show = show
        self.status = status
        self.priority = priority

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PresenceInfo(Type: {self.type}, Show: {self.show}, Status: {self.status}, Priority: {self.priority})"


class Contact:
    def __init__(self, jid: JID, name: str, subscription: str,
                 ask: SubscriptionAsk, groups: list, resources: dict):
        self.jid = jid
        self.name = name
        self.subscription = subscription
        self.ask = ask
        self.groups = groups
        self.resources = resources

    def get_presence(self, resource: Optional[str] = None) -> PresenceInfo:
        """
        Get the presence information for a specific resource.

        Args:
            resource (str, optional): The resource to get presence for. If None, return the presence with the highest priority.

        Returns:
            PresenceInfo: The presence information for the resource.

        Raises:
            KeyError: If the resource is not found.
        """
        if resource is None and self.resources:
            return max(self.resources.values(), key=lambda x: x.priority)
        elif resource in self.resources:
            return self.resources[resource]
        else:
            return PresenceInfo(PresenceType.UNAVAILABLE, PresenceShow.NONE, None, 0)

    def is_available(self, resource: Optional[str] = None) -> bool:
        """
        Check if the contact is available.

        Args:
            resource (str, optional): The resource to check availability for. If None, check all resources.

        Returns:
            bool: True if the contact is available, False otherwise.
        """

        def check_presence(presence_info: PresenceInfo) -> bool:
            return (presence_info.type in [PresenceType.AVAILABLE, ""] and
                    presence_info.show not in [PresenceShow.DND, PresenceShow.EXTENDED_AWAY, PresenceShow.AWAY])

        if resource is not None:
            try:
                presence = self.get_presence(resource)
                return check_presence(presence)
            except KeyError:
                return False
        else:
            return any(check_presence(p) for p in self.resources.values())

    def __str__(self):
        return (f"Contact(JID: {self.jid}, Name: {self.name}, "
                f"Available: {self.is_available()}, Subscription: {self.subscription},"
                f" Ask: {self.ask}, Groups: {self.groups}, Presence: {self.resources})")



class PresenceManager:
    def __init__(self, agent):
        """
        Initialize the PresenceManager.

        Args:
            agent: The agent instance managing the presence.
        """
        self.agent = agent
        self.client = agent.client

        self._contacts: Dict[str, Contact] = {}

        self.approve_all = False

        self.current_available: bool = False
        self.current_status: Optional[Dict[Optional[str], str]] = None
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
        Get the availability of the client.

        Returns:
            bool: True if the client is available, False otherwise.
        """
        return self.current_available

    @property
    def status(self) -> Optional[Dict[Optional[str], str]]:
        """
        Get the status of the client.

        Returns:
            dict or None: The current status of the client.
        """
        return self.current_status

    @property
    def show(self) -> PresenceShow:
        """
        Get the current show value of the client.

        Returns:
            PresenceShow: The current show value.
        """
        return self.current_show

    @property
    def priority(self) -> int:
        """
        Get the current priority of the client.

        Returns:
            int: The current priority.
        """
        return self.current_priority

    def set_available(self, show: Optional[PresenceShow] = PresenceShow.NONE, status: Optional[str] = None) -> None:
        """
        Set the client as available.

        Args:
            show (PresenceShow, optional): The show state of the presence.
            status (str, optional): The human-readable status of the presence.
        """
        self.current_available = True
        self.current_show = show
        self.current_status = {None: status} if status is not None else self.current_status

    def set_unavailable(self) -> None:
        """
        Set the client as unavailable.
        """
        self.current_available = False
        self.current_show = PresenceShow.NONE
        self.current_status = None

    def set_presence(
        self,
        show: Optional[PresenceShow] = PresenceShow.NONE,
        status: Optional[Union[str, Dict[Optional[str], str]]] = None,
        priority: Optional[int] = None,
    ) -> None:
        """
        Set the presence information to be broadcasted by the client.

        Args:
            show (PresenceShow, optional): The show state of the presence.
            status (str or dict, optional): The human-readable status of the presence.
            priority (int, optional): The priority of the presence.
        """
        if isinstance(status, str):
            self.current_status = {None: status}
        elif isinstance(status, dict):
            self.current_status = status

        self.current_show = show if show is not None else self.current_show
        self.current_priority = priority if priority is not None else self.current_priority
        self.client.send_presence(
            pshow=self.current_show.value if self.current_show != PresenceShow.NONE else None,
            pstatus=self.current_status,
            ppriority=self.current_priority,
            ptype='unavailable' if not self.current_available else None
        )

    def get_contacts(self) -> Dict[str, Contact]:
        """
        Get the list of contacts in the roster.

        Returns:
            dict: A dictionary of contacts in the roster.
        """
        for jid in self.client.client_roster.keys():
            subscription = self.client.client_roster[jid]['subscription']
            name = self.client.client_roster[jid]['name']
            groups = self.client.client_roster[jid]['groups']
            presence = self.client.client_roster.presence(jid)
            ask_value = self.client.client_roster[jid]['pending_out']
            ask = SubscriptionAsk.SUBSCRIBE if ask_value else SubscriptionAsk.NONE

            bare = JID(jid).bare

            if bare not in self._contacts:
                resources = {}
                contact = Contact(jid, name, subscription, ask, groups, resources)
            else:
                contact = self._contacts[bare]
                contact.subscription = subscription
                contact.name = name
                contact.groups = groups
                contact.ask = ask
                resources = contact.resources

            for resource, presence_info in presence.items():
                show = PresenceShow(presence_info['show']) if presence_info['show'] else PresenceShow.NONE
                status = presence_info['status']
                priority = presence_info['priority']
                presence_type = PresenceType.AVAILABLE if presence_info['show'] != PresenceShow.NONE else PresenceType.UNAVAILABLE
                resources[resource] = PresenceInfo(presence_type, show, status, priority)
            contact.resources = resources

            self._contacts[bare] = contact

        return self._contacts

    def get_contact(self, jid: JID) -> Contact:
        """
        Get a specific contact from the roster.

        Args:
            jid (JID): The JID of the contact.

        Returns:
            Contact: The contact associated with the given JID.

        Raises:
            ContactNotFound: If the contact is not found in the roster.
        """
        if not isinstance(jid, JID):
            raise AttributeError("jid must be an instance of JID")

        try:
            return self.get_contacts()[jid.bare]
        except KeyError:
            raise ContactNotFound

    def _update_roster_with_presence(self, stanza: Presence) -> None:
        """
        Update the roster with presence information from a stanza.

        Args:
            stanza (Presence): The presence stanza containing presence information.
        """
        bare = stanza['from'].bare
        if bare == self.agent.jid.bare:
            return
        resource = stanza['from'].resource
        show = PresenceShow(stanza['show']) if stanza['show'] else PresenceShow.NONE
        status = stanza['status']
        priority = stanza['priority'] or 0
        presence_type = stanza['type']
        try:
            contact = self._contacts[bare]
            contact.resources[resource] = PresenceInfo(presence_type, show, status, priority)
        except KeyError:
            self._contacts[bare] = Contact(bare, "", "", ask=SubscriptionAsk.NONE, groups=[],
                                           resources={resource: PresenceInfo(presence_type, show, status, priority)})

    def subscribe(self, peer_jid: JID) -> None:
        """
        Send a subscription request to a peer.

        Args:
            peer_jid (JID): The JID of the peer to subscribe to.
        """
        self.client.send_presence_subscription(
            pto=peer_jid.bare,
            ptype='subscribe'
        )

    def unsubscribe(self, peer_jid: JID) -> None:
        """
        Send an unsubscription request to a peer.

        Args:
            peer_jid (JID): The JID of the peer to unsubscribe from.
        """
        self.client.send_presence_subscription(
            pto=peer_jid.bare,
            ptype='unsubscribe'
        )

    def approve(self, peer_jid: JID) -> None:
        """
        Approve a subscription request from a peer.

        Args:
            peer_jid (JID): The JID of the peer whose subscription request is being approved.
        """
        self.client.send_presence_subscription(
            pto=peer_jid.bare,
            ptype='subscribed'
        )

    def _on_available(self, stanza: Presence) -> None:
        """
        Handle a presence available event.

        Args:
            stanza (Presence): The presence stanza received.
        """
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza['from']), stanza)

    def _on_unavailable(self, stanza: Presence) -> None:
        """
        Handle a presence unavailable event.

        Args:
            stanza (Presence): The presence stanza received.
        """
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza['from']), stanza)

    def _on_changed(self, stanza: Presence) -> None:
        """
        Handle a changed presence status event.

        Args:
            stanza (Presence): The presence stanza received.
        """
        self._update_roster_with_presence(stanza)

    def _on_subscribe(self, stanza: Presence) -> None:
        """
        Handle an incoming subscription request.

        Args:
            stanza (Presence): The presence stanza received.
        """
        if self.approve_all:
            self.approve(JID(stanza['from'].bare))
        else:
            self.on_subscribe(str(stanza['from']))

    def _on_subscribed(self, stanza: Presence) -> None:
        """
        Handle a subscription approval event.

        Args:
            stanza (Presence): The presence stanza received.
        """
        self.on_subscribed(str(stanza['from']))

    def _on_unsubscribe(self, stanza: Presence) -> None:
        """
        Handle an incoming unsubscription request.

        Args:
            stanza (Presence): The presence stanza received.
        """
        if self.approve_all:
            self.client.send_presence_subscription(
                pto=JID(stanza['from']).bare,
                ptype='unsubscribed'
            )
        else:
            self.on_unsubscribe(str(stanza['from']))

    def _on_unsubscribed(self, stanza: Presence) -> None:
        """
        Handle an unsubscription approval event.

        Args:
            stanza (Presence): The presence stanza received.
        """
        self.on_unsubscribed(str(stanza['from']))

    def on_subscribe(self, peer_jid: str) -> None:
        """
        Callback called when a subscribe query is received.

        Args:
            peer_jid (str): The JID of the agent asking for subscription.
        """
        pass  # pragma: no cover

    def on_subscribed(self, peer_jid: str) -> None:
        """
        Callback called when a subscribed message is received.

        Args:
            peer_jid (str): The JID of the agent that accepted subscription.
        """
        pass  # pragma: no cover

    def on_unsubscribe(self, peer_jid: str) -> None:
        """
        Callback called when an unsubscribe query is received.

        Args:
            peer_jid (str): The JID of the agent asking for unsubscription.
        """
        pass  # pragma: no cover

    def on_unsubscribed(self, peer_jid: str) -> None:
        """
        Callback called when an unsubscribed message is received.

        Args:
            peer_jid (str): The JID of the agent that unsubscribed.
        """
        pass  # pragma: no cover

    def on_available(self, peer_jid: str, stanza: Presence) -> None:
        """
        Callback called when a contact becomes available.

        Args:
            peer_jid (str): The JID of the agent that is available.
            stanza (Presence): The presence stanza containing type, show, priority and status values.
        """
        pass  # pragma: no cover

    def on_unavailable(self, peer_jid: str, stanza: Presence) -> None:
        """
        Callback called when a contact becomes unavailable.

        Args:
            peer_jid (str): The JID of the agent that is unavailable.
            stanza (Presence): The presence stanza containing type, show, priority and status values.
        """
        pass  # pragma: no cover
