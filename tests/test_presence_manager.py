import pytest
from slixmpp import Presence

from .factories import MockedPresenceAgentFactory
from spade.presence import PresenceManager, PresenceShow, PresenceType, ContactNotFound


async def test_get_state_not_available():
    agent = MockedPresenceAgentFactory(available=False, show=PresenceShow.NONE)
    await agent.start(auto_register=False)

    await agent.start(auto_register=False)

    assert agent.presence.current_presence is None


async def test_presence_manager_initialization(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=False)
    assert len(manager.contacts) == 0


async def test_handle_presence_available(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=False)

    presence = Presence()
    presence['from'] = jid
    presence['type'] = 'available'
    presence['show'] = 'chat'
    presence['status'] = 'Online'
    presence['priority'] = '5'

    manager.handle_presence(presence)

    contact = manager.get_contact(jid.bare)
    assert contact.is_available()
    assert contact.current_presence.show == PresenceShow.CHAT
    assert contact.current_presence.status == 'Online'


async def test_handle_presence_unavailable(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=False)

    # First, set the contact as available
    presence_available = Presence()
    presence_available['from'] = jid
    presence_available['type'] = 'available'
    presence_available['show'] = 'chat'
    presence_available['status'] = 'Online'
    presence_available['priority'] = '5'

    manager.handle_presence(presence_available)

    # Now, set the contact as unavailable
    presence_unavailable = Presence()
    presence_unavailable['from'] = jid
    presence_unavailable['type'] = 'unavailable'

    manager.handle_presence(presence_unavailable)

    contact = manager.get_contact(jid.bare)
    assert not contact.is_available()


async def test_handle_subscription_approve_all(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=True)

    presence_subscribe = Presence()
    presence_subscribe['from'] = jid
    presence_subscribe['type'] = 'subscribe'
    presence_subscribe['ask'] = 'subscribe'
    presence_subscribe['subscription'] = 'subscribe'

    manager.handle_subscription(presence_subscribe)

    contact = manager.get_contact(jid.bare)
    assert contact.subscription == 'subscribed'


async def test_handle_subscription_manual(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=False)

    presence_subscribe = Presence()
    presence_subscribe['from'] = jid
    presence_subscribe['type'] = 'subscribe'
    presence_subscribe['ask'] = 'subscribe'

    manager.handle_subscription(presence_subscribe)

    contact = manager.get_contact(jid.bare)
    assert contact.subscription == 'subscribe'



async def test_set_presence():
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent)
    manager.set_presence(PresenceType.AVAILABLE, PresenceShow.CHAT, "Busy", 10)

    assert manager.current_presence.type == PresenceType.AVAILABLE
    assert manager.current_presence.show == PresenceShow.CHAT
    assert manager.current_presence.status == "Busy"
    assert manager.current_presence.priority == 10



async def test_get_contact_presence(jid):
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent, approve_all=False)

    presence = Presence()
    presence['from'] = jid
    presence['type'] = 'available'
    presence['show'] = 'chat'
    presence['status'] = 'Online'
    presence['priority'] = '5'

    manager.handle_presence(presence)

    presence_info = manager.get_contact_presence(jid.bare)
    assert presence_info.show == PresenceShow.CHAT
    assert presence_info.status == 'Online'
    assert presence_info.priority == 5



async def test_contact_not_found():
    mocked_agent = MockedPresenceAgentFactory()
    await mocked_agent.start()
    manager = PresenceManager(agent=mocked_agent)

    with pytest.raises(ContactNotFound):
        manager.get_contact("nonexistent@localhost")
