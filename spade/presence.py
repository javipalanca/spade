from enum import Enum
from typing import Dict, Optional, Union

from slixmpp import JID
from slixmpp.stanza import Presence


class ContactNotFound(Exception):
    pass


class PresenceNotFound(Exception):
    pass


class PresenceShow(Enum):
    EXTENDED_AWAY = "xa"
    AWAY = "away"
    CHAT = "chat"
    DND = "dnd"
    NONE = "none"


class PresenceType(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    PROBE = "probe"
    SUBSCRIBE = "subscribe"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBE = "unsubscribe"
    UNSUBSCRIBED = "unsubscribed"


class PresenceInfo:
    def __init__(
        self,
        presence_type: PresenceType,
        show: PresenceShow,
        status: Optional[str] = "",
        priority: int = 0,
    ):
        self.type = presence_type
        self.show = show
        self.status = status
        self.priority = priority

    def is_available(self) -> bool:
        return self.type == PresenceType.AVAILABLE

    def __eq__(self, other):
        if not isinstance(other, PresenceInfo):
            return False
        return (
            self.type == other.type
            and self.show == other.show
            and self.status == other.status
            and self.priority == other.priority
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"PresenceInfo(Type: {self.type}, Show: {self.show}, Status: {self.status}, Priority: {self.priority})"

    def __repr__(self) -> str:
        return str(self)


class Contact:
    def __init__(self, jid: JID, name: str, subscription: str, ask: str, groups: list):
        self.jid = jid
        self.name = name
        self.subscription = subscription
        self.ask = ask
        self.groups = groups
        self.resources: Dict[str, PresenceInfo] = {}
        self.current_presence: Optional[PresenceInfo] = None
        self.last_presence: Optional[PresenceInfo] = None

    def update_presence(self, resource: str, presence_info: PresenceInfo):
        # Update the current presence automatically based on priority
        if presence_info == self.resources.get(resource):
            return
        self.resources[resource] = presence_info
        new_presence = max(
            self.resources.values(), key=lambda p: p.priority, default=None
        )
        if new_presence != self.current_presence:
            self.last_presence = self.current_presence
            self.current_presence = new_presence

    def get_presence(self, resource: Optional[str] = None) -> PresenceInfo:
        if resource:
            if resource in self.resources:
                return self.resources[resource]
            else:
                raise KeyError(
                    f"Resource '{resource}' not found for contact {self.jid}."
                )
        if self.current_presence:
            return self.current_presence
        raise PresenceNotFound(
            f"No presence information available for contact {self.jid}."
        )

    def update_subscription(self, subscription: str, ask: str):
        self.subscription = subscription
        self.ask = ask

    def is_available(self) -> bool:
        return (
            self.current_presence is not None
            and self.current_presence.type == PresenceType.AVAILABLE
        )

    def is_subscribed(self) -> bool:
        return self.subscription in ["both", "to"] or self.ask == "subscribe"

    def __str__(self):
        return f"Contact(JID: {self.jid}, Name: {self.name}, Presence: {self.current_presence})"

    def __repr__(self) -> str:
        return str(self)


class PresenceManager:
    def __init__(self, agent, approve_all: bool = False):
        self.contacts: Dict[str, Contact] = {}
        self.agent = agent
        self.current_presence: Optional[PresenceInfo] = None
        self.approve_all = approve_all
        # Adding event handlers to handle incoming presence and subscription events
        self.agent.client.add_event_handler("presence_available", self.handle_presence)
        self.agent.client.add_event_handler(
            "presence_unavailable", self.handle_presence
        )
        self.agent.client.add_event_handler("changed_status", self.handle_presence)
        self.agent.client.add_event_handler(
            "presence_subscribe", self.handle_subscription
        )
        self.agent.client.add_event_handler(
            "presence_subscribed", self.handle_subscription
        )
        self.agent.client.add_event_handler(
            "presence_unsubscribe", self.handle_subscription
        )
        self.agent.client.add_event_handler(
            "presence_unsubscribed", self.handle_subscription
        )
        self.agent.client.add_event_handler("roster_update", self.handle_roster_update)

    def is_available(self) -> bool:
        return (
            self.current_presence is not None and self.current_presence.is_available()
        )

    def get_presence(self) -> PresenceInfo:
        return self.current_presence

    def get_show(self) -> PresenceShow:
        return (
            self.current_presence.show if self.current_presence else PresenceShow.NONE
        )

    def get_status(self) -> Optional[str]:
        return self.current_presence.status if self.current_presence else None

    def get_priority(self) -> int:
        return self.current_presence.priority if self.current_presence else 0

    def handle_presence(self, presence: Presence):
        jid = presence["from"]
        peer_jid = str(jid)
        bare_jid = jid.bare
        if bare_jid == self.agent.jid.bare:
            return
        resource = presence["from"].resource
        presence_type = presence["type"]
        # Normalise the value of `type` if it is a show
        if presence_type in [show.value for show in PresenceShow]:
            presence_type = PresenceType.AVAILABLE
        presence_type = PresenceType(presence_type)

        show = PresenceShow(presence.get("show", "none"))
        status = presence.get("status")
        priority = int(presence.get("priority", 0))

        name = presence.name if presence.name else peer_jid
        presence_info = PresenceInfo(presence_type, show, status, priority)
        if bare_jid not in self.contacts:
            # Create a new contact if it doesn't exist
            self.contacts[bare_jid] = Contact(
                jid=JID(peer_jid), name=name, subscription="none", ask="", groups=[]
            )
        # Update the presence of the contact
        self.contacts[bare_jid].update_presence(resource, presence_info)
        # Call user-defined handler
        if presence_type == PresenceType.AVAILABLE:
            self.on_available(
                peer_jid, presence_info, self.contacts[bare_jid].last_presence
            )
        elif presence_type == PresenceType.UNAVAILABLE:
            self.on_unavailable(
                peer_jid, presence_info, self.contacts[bare_jid].last_presence
            )

        self.on_presence_received(presence)

    def handle_subscription(self, presence: Presence):
        peer_jid = presence["from"].bare
        subscription_type = presence["type"]
        ask = presence.get("ask", "none")

        if peer_jid not in self.contacts:
            # Create a new contact if it doesn't exist
            self.contacts[peer_jid] = Contact(
                jid=JID(peer_jid),
                name=peer_jid,
                subscription="none",
                ask=ask,
                groups=[],
            )

        # Call user-defined handler or automatically approve if approve_all is True
        if subscription_type == "subscribe" and self.approve_all:
            self.approve_subscription(peer_jid)
            self.on_subscribe(peer_jid)
        elif subscription_type == "subscribe":
            self.on_subscribe(peer_jid)
        elif subscription_type == "subscribed":
            self.subscribed(peer_jid)
            self.on_subscribed(peer_jid)
        elif subscription_type == "unsubscribe":
            self.on_unsubscribe(peer_jid)
        elif subscription_type == "unsubscribed":
            self.unsubscribed(peer_jid)
            self.on_unsubscribed(peer_jid)

    def handle_roster_update(self, event):
        """Executed when the roster is received or updated."""

        roster = event["roster"]
        for item in roster:
            bare_jid = item.get_jid().bare
            name = item.get("name", bare_jid)
            subscription = item.get("subscription", "none")
            ask = item.get("ask", "none")
            groups = item.get_groups()

            # Storing contact information in the internal structure
            if bare_jid not in self.contacts:
                self.contacts[bare_jid] = Contact(
                    jid=bare_jid,
                    name=name,
                    subscription=subscription,
                    ask=ask,
                    groups=groups,
                )
            else:
                self.contacts[bare_jid].name = name
                self.contacts[bare_jid].subscription = subscription
                self.contacts[bare_jid].ask = ask
                self.contacts[bare_jid].groups = groups

    def get_contact_presence(
        self, jid: Union[str, JID], resource: Optional[str] = None
    ) -> PresenceInfo:
        if isinstance(jid, JID):
            jid = jid.bare
        else:
            jid = JID(jid).bare
        if jid in self.contacts:
            return self.contacts[jid].get_presence(resource)
        else:
            raise ContactNotFound(f"Contact with JID '{jid}' not found.")

    def get_contact(self, jid: Union[str, JID]) -> Contact:
        if isinstance(jid, JID):
            jid = jid.bare
        else:
            jid = JID(jid).bare
        if jid in self.contacts:
            return self.contacts[jid]
        else:
            raise ContactNotFound(f"Contact with JID '{jid}' not found.")

    def get_contacts(self) -> Dict[str, Contact]:
        return {jid: c for jid, c in self.contacts.items() if c.is_subscribed()}

    def set_presence(
        self,
        presence_type: PresenceType = PresenceType.AVAILABLE,
        show: PresenceShow = PresenceShow.CHAT,
        status: Optional[str] = "",
        priority: int = 0,
    ):
        # This method could be used to set the presence for the local user
        self.current_presence = PresenceInfo(presence_type, show, status, priority)
        # Send the presence stanza to the server
        self.agent.client.send_presence(
            ptype=presence_type.value,
            pshow=show.value,
            pstatus=status,
            ppriority=str(priority),
        )

    def set_available(self):
        # Method to set presence to available
        self.set_presence(PresenceType.AVAILABLE)

    def set_unavailable(self):
        # Method to set presence to unavailable
        self.set_presence(PresenceType.UNAVAILABLE, PresenceShow.NONE, None, 0)

    def subscribe(self, jid: str):
        # Logic to send a subscription request to a contact
        if jid not in self.contacts:
            self.contacts[jid] = Contact(
                jid=JID(jid), name=jid, subscription="to", ask="subscribe", groups=[]
            )
        else:
            if self.contacts[jid].subscription == "from":
                self.contacts[jid].update_subscription("from", "subscribe")
            else:
                self.contacts[jid].update_subscription("to", "subscribe")
        # Send the subscription stanza to the server
        self.agent.client.send_presence(pto=jid, ptype="subscribe")

    def subscribed(self, jid: str):
        # Logic to update contact subscription with subscribe
        if jid not in self.contacts:
            self.contacts[jid] = Contact(
                jid=JID(jid), name=jid, subscription="to", ask="", groups=[]
            )
        else:
            if (
                self.contacts[jid].subscription == "none"
                and self.contacts[jid].ask == "subscribe"
            ):
                self.contacts[jid].update_subscription("to", "")
            elif (
                self.contacts[jid].subscription == "from"
                and self.contacts[jid].ask == "subscribe"
            ):
                self.contacts[jid].update_subscription("both", "")

    def unsubscribe(self, jid: str):
        # Logic to send an unsubscription request to a contact
        if jid in self.contacts:
            if self.contacts[jid].subscription == "both":
                self.contacts[jid].update_subscription("from", "")
            elif self.contacts[jid].subscription == "to":
                self.contacts[jid].update_subscription("none", "")
        # Send the unsubscription stanza to the server
        self.agent.client.send_presence(pto=jid, ptype="unsubscribe")

    def unsubscribed(self, jid: str):
        # Logic to update contact subscription with unsubscribe
        if jid not in self.contacts:
            self.contacts[jid] = Contact(
                jid=JID(jid), name=jid, subscription="none", ask="", groups=[]
            )
        else:
            if self.contacts[jid].subscription == "both":
                self.contacts[jid].update_subscription("to", "")
            elif self.contacts[jid].subscription == "from":
                self.contacts[jid].update_subscription("none", "")

    def approve_subscription(self, jid: str):
        # Logic to approve a subscription request
        if jid in self.contacts:
            if self.contacts[jid].subscription == "to":
                self.contacts[jid].update_subscription("both", "")
            else:
                self.contacts[jid].update_subscription("from", "")
        # Send the subscribed stanza to the server
        self.agent.client.send_presence(pto=jid, ptype="subscribed")

    # User-overridable methods
    def on_subscribe(self, peer_jid: str):
        pass

    def on_subscribed(self, peer_jid: str):
        pass

    def on_unsubscribe(self, peer_jid: str):
        pass

    def on_unsubscribed(self, peer_jid: str):
        pass

    def on_presence_received(self, presence: Presence):
        pass

    def on_available(
        self,
        peer_jid: str,
        presence_info: PresenceInfo,
        last_presence: Optional[PresenceInfo],
    ):
        pass

    def on_unavailable(
        self,
        peer_jid: str,
        presence_info: PresenceInfo,
        last_presence: Optional[PresenceInfo],
    ):
        pass
