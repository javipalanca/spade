from unittest.mock import Mock
import pytest
from slixmpp.stanza import Presence, Iq
from slixmpp import JID

from spade.presence import ContactNotFound, PresenceShow, PresenceType, Contact
from .factories import MockedPresenceAgentFactory


async def test_get_state_not_available():
    agent = MockedPresenceAgentFactory(available=False, show=PresenceShow.NONE)

    await agent.start(auto_register=False)

    assert agent.presence.is_available() is False
    assert agent.presence.get_status() is None
    assert agent.presence.get_show() is PresenceShow.NONE


async def test_get_state_available():
    agent = MockedPresenceAgentFactory(available=True)

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.is_available() is True


async def test_set_presence_available():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_presence(PresenceType.AVAILABLE)

    assert agent.presence.is_available()


async def test_set_available_with_show():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_presence(PresenceType.AVAILABLE, show=PresenceShow.CHAT)

    assert agent.presence.is_available()
    assert agent.presence.get_show() == PresenceShow.CHAT


async def test_set_unavailable():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_unavailable()

    assert agent.presence.is_available() is False


async def test_get_state_show():
    agent = MockedPresenceAgentFactory(available=True, show=PresenceShow.AWAY)

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_show() == PresenceShow.AWAY


async def test_get_status_empty():
    agent = MockedPresenceAgentFactory(status="")

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_status() == ""


async def test_get_status_string():
    agent = MockedPresenceAgentFactory(status="Working")

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_status() == "Working"


async def test_get_status_dict():
    agent = MockedPresenceAgentFactory(status="Working")

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_status() == "Working"


async def test_get_priority_default():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_priority() == 0


async def test_get_priority():
    agent = MockedPresenceAgentFactory(priority=10)

    await agent.start(auto_register=False)

    agent.mock_presence()

    assert agent.presence.get_priority() == 10


async def test_set_presence_unavailable():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_unavailable()

    assert agent.presence.is_available() is False


async def test_set_presence_status():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_presence(status="Lunch")

    assert agent.presence.get_status() == "Lunch"


async def test_set_presence_priority():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_presence(priority=5)

    assert agent.presence.get_priority() == 5


async def test_set_presence():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.set_presence(show=PresenceShow.AWAY, status="Lunch", priority=2)

    assert agent.presence.is_available()
    assert agent.presence.get_show() == PresenceShow.AWAY
    assert agent.presence.get_status() == "Lunch"
    assert agent.presence.get_priority() == 2


async def test_get_contacts_empty():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    assert agent.presence.get_contacts() == {}


async def test_get_contacts(jid: JID, iq: Iq):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.handle_roster_update(iq)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare
    assert bare_jid in contacts
    assert len(contacts) == 2
    assert isinstance(contacts[bare_jid], Contact)
    assert contacts[bare_jid].name == "My Friend"
    assert contacts[bare_jid].subscription == "both"
    assert contacts[bare_jid].groups == ["Friends"]
    assert contacts[bare_jid].ask == "none"
    assert hasattr(contacts[bare_jid], "resources")
    assert isinstance(contacts[bare_jid].resources, dict)


async def test_get_contacts_with_update(jid: JID, iq: Iq):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.handle_roster_update(iq)

    stanza = Presence()
    stanza["from"] = jid
    stanza.set_show(PresenceShow.CHAT.value)
    stanza["status"] = "Just Chatting"
    stanza.set_priority(2)

    agent.presence.handle_presence(stanza)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare
    assert bare_jid in contacts
    assert isinstance(contacts[bare_jid], Contact)
    assert contacts[bare_jid].name == "My Friend"
    assert contacts[bare_jid].subscription == "both"
    assert contacts[bare_jid].groups == ["Friends"]
    assert contacts[bare_jid].ask == "none"
    assert hasattr(contacts[bare_jid], "resources")
    assert isinstance(contacts[bare_jid].resources, dict)
    assert contacts[bare_jid].resources[jid.resource].type == PresenceType.AVAILABLE
    assert contacts[bare_jid].resources[jid.resource].show == PresenceShow.CHAT
    assert contacts[bare_jid].resources[jid.resource].status == "Just Chatting"
    assert contacts[bare_jid].resources[jid.resource].priority == 2


async def test_get_contacts_with_update_unavailable(jid: JID, iq: Iq):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.handle_roster_update(iq)

    stanza = Presence()
    stanza["from"] = jid
    stanza.set_type(PresenceType.UNAVAILABLE.value)

    agent.presence.handle_presence(stanza)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare
    assert bare_jid in contacts
    assert isinstance(contacts[bare_jid], Contact)
    assert contacts[bare_jid].name == "My Friend"
    assert contacts[bare_jid].subscription == "both"
    assert contacts[bare_jid].groups == ["Friends"]
    assert contacts[bare_jid].ask == "none"
    assert hasattr(contacts[bare_jid], "resources")
    assert isinstance(contacts[bare_jid].resources, dict)
    assert contacts[bare_jid].resources[jid.resource].type == PresenceType.UNAVAILABLE
    assert contacts[bare_jid].resources[jid.resource].show == PresenceShow.NONE
    assert contacts[bare_jid].resources[jid.resource].status is None
    assert contacts[bare_jid].resources[jid.resource].priority == 0


async def test_get_contact(jid: JID, iq: Iq):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.handle_roster_update(iq)
    contact = agent.presence.get_contact(jid)

    assert isinstance(contact, Contact)
    assert contact.name == "My Friend"
    assert contact.subscription == "both"
    assert len(contact.groups) == 1
    assert contact.ask == "none"
    assert hasattr(contact, "resources")
    assert isinstance(contact.resources, dict)


async def test_get_invalid_jid_contact():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    with pytest.raises(ContactNotFound):
        agent.presence.get_contact(JID("invalid@contact"))


async def test_get_invalid_str_contact():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    with pytest.raises(ContactNotFound):
        agent.presence.get_contact("invalid@contact")


async def test_subscribe(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.client.send_presence = Mock()
    agent.presence.subscribe(jid)

    assert agent.client.send_presence.mock_calls
    arg = agent.client.send_presence.call_args[1]

    assert arg["pto"] == jid
    assert arg["ptype"] == "subscribe"


async def test_unsubscribe(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.client.send_presence = Mock()
    agent.presence.unsubscribe(jid)

    assert agent.client.send_presence.mock_calls
    arg = agent.client.send_presence.call_args[1]

    assert arg["pto"] == jid
    assert arg["ptype"] == "unsubscribe"


async def test_approve(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.client.send_presence = Mock()
    agent.presence.approve_subscription(jid)

    assert agent.client.send_presence.mock_calls
    arg = agent.client.send_presence.call_args[1]

    assert arg["pto"] == jid
    assert arg["ptype"] == "subscribed"


async def test_on_available(jid: JID):
    import logging

    log = logging.getLogger("xmlstream")
    log.setLevel(logging.DEBUG)
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.on_available = Mock()

    stanza = Presence()
    stanza["from"] = jid
    stanza["type"] = PresenceType.AVAILABLE

    agent.client.event("presence_available", stanza)

    assert agent.presence.on_available.mock_calls

    assert len(agent.presence.on_available.mock_calls) == 2
    jid_arg = agent.presence.on_available.call_args[0][0]
    presence_info = agent.presence.on_available.call_args[0][1]
    last_presence = agent.presence.on_available.call_args[0][2]

    assert jid_arg == jid
    assert presence_info.type == PresenceType.AVAILABLE
    assert last_presence is None


async def test_on_unavailable(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.on_unavailable = Mock()

    stanza = Presence()
    stanza["from"] = jid
    stanza["type"] = "unavailable"

    agent.client.event("presence_unavailable", stanza)

    assert agent.presence.on_unavailable.mock_calls

    jid_arg = agent.presence.on_unavailable.call_args[0][0]
    presence_info = agent.presence.on_unavailable.call_args[0][1]
    last_presence = agent.presence.on_unavailable.call_args[0][2]

    assert jid_arg == jid
    assert presence_info.type == PresenceType.UNAVAILABLE
    assert last_presence is None


async def test_on_changed_status(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    # Create a presence stanza with the desired change
    stanza = Presence()
    stanza["from"] = jid
    stanza["show"] = PresenceShow.CHAT.value

    # Trigger the 'changed_status' event with the presence stanza
    agent.client.event("changed_status", stanza)
    agent.presence.subscribe(jid.bare)

    # Verify that the contact in the roster has the updated presence
    contacts = agent.presence.get_contacts()
    bare_jid = jid.bare

    # Check that the contact is in the roster and has the correct presence
    assert bare_jid in contacts
    contact = contacts[bare_jid]

    # Verify that the contact has updated presence information
    assert contact.resources is not None
    assert len(contact.resources) > 0

    # Get the presence information for the resource and verify the 'show' state
    resource_presence = contact.resources.get(jid.resource)
    assert resource_presence is not None
    assert resource_presence.show == PresenceShow.CHAT


async def test_on_subscribe(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.on_subscribe = Mock()

    stanza = Presence()
    stanza["from"] = jid
    stanza["type"] = PresenceType.SUBSCRIBE.value

    agent.client.event("presence_subscribe", stanza)

    assert agent.presence.on_subscribe.mock_calls

    jid_arg = agent.presence.on_subscribe.call_args[0][0]

    assert jid_arg == jid.bare


async def test_on_subscribed(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.on_subscribed = Mock()

    stanza = Presence()
    stanza["from"] = jid
    stanza["type"] = PresenceType.SUBSCRIBED.value

    agent.client.event("presence_subscribed", stanza)

    assert agent.presence.on_subscribed.mock_calls

    jid_arg = agent.presence.on_subscribed.call_args[0][0]

    assert jid_arg == jid.bare


async def test_on_unsubscribe(jid: JID):
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    agent.presence.on_unsubscribe = Mock()

    stanza = Presence()
    stanza["from"] = jid
    stanza["type"] = PresenceType.UNSUBSCRIBE.value

    agent.client.event("presence_unsubscribe", stanza)

    assert agent.presence.on_unsubscribe.mock_calls

    jid_arg = agent.presence.on_unsubscribe.call_args[0][0]

    assert jid_arg == jid.bare


async def test_ignore_self_presence():
    agent = MockedPresenceAgentFactory()

    await agent.start(auto_register=False)

    jid_ = agent.jid

    stanza = Presence()
    stanza["from"] = jid_
    stanza["type"] = PresenceType.AVAILABLE.value
    stanza["show"] = PresenceShow.CHAT.value

    agent.client.event("presence_available", stanza)

    with pytest.raises(ContactNotFound):
        agent.presence.get_contact(jid_)

    await agent.stop()
