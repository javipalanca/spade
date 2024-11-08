from enum import Enum
from typing import Dict, Optional

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


class PresenceInfo:
    def __init__(self, presence_type: PresenceType, show: PresenceShow, status: Optional[str], priority: int):
        self.type = presence_type
        self.show = show
        self.status = status
        self.priority = priority

    def is_available(self) -> bool:
        return self.type == PresenceType.AVAILABLE

    def __str__(self):
        return f"PresenceInfo(Type: {self.type}, Show: {self.show}, Status: {self.status}, Priority: {self.priority})"


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
        self.resources[resource] = presence_info
        # Update the current presence automatically based on priority
        self.last_presence = self.current_presence
        self.current_presence = max(self.resources.values(), key=lambda p: p.priority, default=None)

    def get_presence(self, resource: Optional[str] = None) -> PresenceInfo:
        if resource:
            if resource in self.resources:
                return self.resources[resource]
            else:
                raise KeyError(f"Resource '{resource}' not found for contact {self.jid}.")
        if self.current_presence:
            return self.current_presence
        raise ContactNotFound(f"No presence information available for contact {self.jid}.")

    def update_subscription(self, subscription: str, ask: str):
        self.subscription = subscription
        self.ask = ask

    def is_available(self) -> bool:
        return self.current_presence is not None and self.current_presence.type == PresenceType.AVAILABLE

    def __str__(self):
        return f"Contact(JID: {self.jid}, Name: {self.name}, Presence: {self.current_presence})"


class PresenceManager:
    def __init__(self, agent, approve_all: bool = False):
        self.contacts: Dict[str, Contact] = {}
        self.agent = agent
        self.current_presence: Optional[PresenceInfo] = None
        self.approve_all = approve_all
        # Adding event handlers to handle incoming presence and subscription events
        self.agent.client.add_event_handler("presence_available", self.handle_presence)
        self.agent.client.add_event_handler("presence_unavailable", self.handle_presence)
        self.agent.client.add_event_handler("presence_subscribe", self.handle_subscription)
        self.agent.client.add_event_handler("presence_subscribed", self.handle_subscription)
        self.agent.client.add_event_handler("presence_unsubscribe", self.handle_subscription)
        self.agent.client.add_event_handler("presence_unsubscribed", self.handle_subscription)

    def is_available(self) -> bool:
        return self.current_presence is not None and self.current_presence.is_available()
    
    def get_presence(self) -> PresenceInfo:
        return self.current_presence
    
    def get_show(self) -> PresenceShow:
        return self.current_presence.show if self.current_presence else PresenceShow.NONE
    
    def get_status(self) -> Optional[str]:
        return self.current_presence.status if self.current_presence else None

    def get_priority(self) -> int:
        return self.current_presence.priority if self.current_presence else 0      

    def handle_presence(self, presence: Presence):
        peer_jid = presence['from'].bare
        resource = presence['from'].resource
        presence_type = presence['type']
        # Normalise the value of `type` if it is a show
        if presence_type in [show.value for show in PresenceShow]:
            presence_type = PresenceType.AVAILABLE.value
        presence_type = PresenceType(presence_type)
        show = PresenceShow(presence.get('show', 'none'))
        status = presence.get('status')
        priority = int(presence.get('priority', 0))

        name = presence.name if presence.name else peer_jid
        presence_info = PresenceInfo(presence_type, show, status, priority)
        if peer_jid not in self.contacts:
            # Create a new contact if it doesn't exist
            self.contacts[peer_jid] = Contact(jid=JID(peer_jid), name=name, subscription='', ask='', groups=[])
        # Update the presence of the contact
        self.contacts[peer_jid].update_presence(resource, presence_info)
        # Call user-defined handler
        if presence_type == PresenceType.AVAILABLE:
            self.on_available(peer_jid, self.contacts[peer_jid].last_presence)
        elif presence_type == PresenceType.UNAVAILABLE:
            self.on_unavailable(peer_jid, self.contacts[peer_jid].last_presence)

    def handle_subscription(self, presence: Presence):
        peer_jid = presence['from'].bare
        subscription_type = presence['type']
        ask = presence.get('ask', 'none')

        if peer_jid not in self.contacts:
            # Create a new contact if it doesn't exist
            self.contacts[peer_jid] = Contact(jid=JID(peer_jid), name=peer_jid, subscription=subscription_type, ask=ask, groups=[])
        else:
            # Update the subscription information
            self.contacts[peer_jid].update_subscription(subscription_type, ask)

        # Call user-defined handler or automatically approve if approve_all is True
        if subscription_type == "subscribe" and self.approve_all:
            self.approve_subscription(peer_jid)
            self.on_subscribe(peer_jid)
        elif subscription_type == "subscribe":
            self.on_subscribe(peer_jid)
        elif subscription_type == "subscribed":
            self.on_subscribed(peer_jid)
        elif subscription_type == "unsubscribe":
            self.on_unsubscribe(peer_jid)
        elif subscription_type == "unsubscribed":
            self.on_unsubscribed(peer_jid)

    def handle_roster_update(self, iq):
        """Se ejecuta cuando el roster es recibido o actualizado"""
        # Get the Slixmpp RosterManager
        roster = self.client.client_roster

        # Iterate over all JIDs in the roster
        for jid in roster.keys():
            name = roster[jid]['name']  # Friendly name of the contact (can be None)
            subscription = roster[jid]['subscription']  # Subscription status (none, to, from, both)
            ask = roster[jid]['ask']  # Subscription request (can be subscribe)
            groups = roster[jid]['groups']  # List of groups to which the contact belongs

            # Storing contact information in the internal structure
            self.contacts[jid] = {
                'name': name,
                'subscription': subscription,
                'ask': ask,
                'groups': groups,
                'resources': {}
            }

    def get_contact_presence(self, jid: str, resource: Optional[str] = None) -> PresenceInfo:
        if jid in self.contacts:
            return self.contacts[jid].get_presence(resource)
        else:
            raise ContactNotFound(f"Contact with JID '{jid}' not found.")

    def get_contact(self, jid: str) -> Contact:
        if jid in self.contacts:
            return self.contacts[jid]
        else:
            raise ContactNotFound(f"Contact with JID '{jid}' not found.")

    def get_contacts(self) -> Dict[str, Contact]:
        return self.contacts

    def set_presence(self, presence_type: PresenceType=PresenceType.AVAILABLE, show: PresenceShow=PresenceShow.CHAT, status: Optional[str]="", priority: int=0):
        # This method could be used to set the presence for the local user
        self.current_presence = PresenceInfo(presence_type, show, status, priority)
        # Send the presence stanza to the server
        self.agent.client.send_presence(ptype=presence_type.value, pshow=show.value, pstatus=status, ppriority=str(priority))

    def set_unavailable(self):
        # Method to set presence to unavailable
        self.set_presence(PresenceType.UNAVAILABLE, PresenceShow.NONE, None, 0)

    def subscribe(self, jid: str):
        # Logic to send a subscription request to a contact
        if jid not in self.contacts:
            self.contacts[jid] = Contact(jid=JID(jid), name=jid, subscription='subscribe', ask='subscribe', groups=[])
        # Send the subscription stanza to the server
        self.agent.client.send_presence(pto=jid, ptype='subscribe')

    def unsubscribe(self, jid: str):
        # Logic to send an unsubscription request to a contact
        if jid in self.contacts:
            self.contacts[jid].update_subscription('unsubscribe', 'unsubscribe')
        # Send the unsubscription stanza to the server
        self.agent.client.send_presence(pto=jid, ptype='unsubscribe')

    def approve_subscription(self, jid: str):
        # Logic to approve a subscription request
        if jid in self.contacts:
            self.contacts[jid].update_subscription('subscribed', '')
        # Send the subscribed stanza to the server
        self.agent.client.send_presence(pto=jid, ptype='subscribed')

    # User-overridable methods
    def on_subscribe(self, peer_jid: str):
        pass

    def on_subscribed(self, peer_jid: str):
        pass

    def on_unsubscribe(self, peer_jid: str):
        pass

    def on_unsubscribed(self, peer_jid: str):
        pass

    def on_available(self, peer_jid: str, last_presence: Optional[PresenceInfo]):
        pass

    def on_unavailable(self, peer_jid: str, last_presence: Optional[PresenceInfo]):
        pass
