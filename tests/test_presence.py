from unittest.mock import Mock

import pytest
from aioxmpp import PresenceState, PresenceShow, JID, PresenceType, Presence
from aioxmpp.roster.xso import Item as XSOItem

from spade.presence import ContactNotFound
from .factories import MockedPresenceAgentFactory


def test_get_state_not_available():
    agent = MockedPresenceAgentFactory(available=False, show=PresenceShow.NONE)

    future = agent.start(auto_register=False)
    future.result()

    assert type(agent.presence.state) == PresenceState
    assert agent.presence.state.available is False
    assert agent.presence.state.show == PresenceShow.NONE
    assert not agent.presence.is_available()


def test_get_state_available():
    agent = MockedPresenceAgentFactory(available=True)

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.state.available
    assert agent.presence.is_available()


def test_set_available():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_available()

    assert agent.presence.is_available()


def test_set_available_with_show():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_available(show=PresenceShow.CHAT)

    assert agent.presence.is_available()
    assert agent.presence.state.show == PresenceShow.CHAT


def test_set_unavailable():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_unavailable()

    assert not agent.presence.is_available()


def test_get_state_show():
    agent = MockedPresenceAgentFactory(available=True, show=PresenceShow.AWAY)

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.state.show == PresenceShow.AWAY


def test_get_status_empty():
    agent = MockedPresenceAgentFactory(status={})

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.status == {}


def test_get_status_string():
    agent = MockedPresenceAgentFactory(status="Working")

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.status == {None: "Working"}


def test_get_status_dict():
    agent = MockedPresenceAgentFactory(status={"en": "Working"})

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.status == {"en": "Working"}


def test_get_priority_default():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.priority == 0


def test_get_priority():
    agent = MockedPresenceAgentFactory(priority=10)

    future = agent.start(auto_register=False)
    future.result()
    agent.mock_presence()

    assert agent.presence.priority == 10


def test_set_presence_available():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(state=PresenceState(available=True))

    assert agent.presence.is_available()


def test_set_presence_unavailable():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(state=PresenceState(available=False))

    assert not agent.presence.is_available()


def test_set_presence_status():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(status="Lunch")

    assert agent.presence.status == {None: "Lunch"}


def test_set_presence_status_dict():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(status={"en": "Lunch"})

    assert agent.presence.status == {"en": "Lunch"}


def test_set_presence_priority():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(priority=5)

    assert agent.presence.priority == 5


def test_set_presence():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.set_presence(
        state=PresenceState(True, PresenceShow.PLAIN), status="Lunch", priority=2
    )

    assert agent.presence.is_available()
    assert agent.presence.state.show == PresenceShow.PLAIN
    assert agent.presence.status == {None: "Lunch"}
    assert agent.presence.priority == 2


def test_get_contacts_empty():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    assert agent.presence.get_contacts() == {}


def test_get_contacts(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Friend"

    agent.presence.roster._update_entry(item)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare()
    assert bare_jid in contacts
    assert type(contacts[bare_jid]) == dict
    assert contacts[bare_jid]["approved"]
    assert contacts[bare_jid]["name"] == "My Friend"
    assert contacts[bare_jid]["subscription"] == "none"
    assert "ask" not in contacts[bare_jid]
    assert "groups" not in contacts[bare_jid]


def test_get_contacts_with_presence(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Available Friend"

    agent.presence.roster._update_entry(item)

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare()
    assert bare_jid in contacts
    assert contacts[bare_jid]["name"] == "My Available Friend"

    assert contacts[bare_jid]["presence"].type_ == PresenceType.AVAILABLE


def test_get_contacts_with_presence_on_and_off(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Friend"

    agent.presence.roster._update_entry(item)

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)
    stanza = Presence(from_=jid, type_=PresenceType.UNAVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare()
    assert bare_jid in contacts
    assert contacts[bare_jid]["name"] == "My Friend"

    assert contacts[bare_jid]["presence"].type_ == PresenceType.UNAVAILABLE


def test_get_contacts_with_presence_unavailable(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My UnAvailable Friend"

    agent.presence.roster._update_entry(item)

    stanza = Presence(from_=jid, type_=PresenceType.UNAVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    contacts = agent.presence.get_contacts()

    bare_jid = jid.bare()
    assert bare_jid in contacts
    assert contacts[bare_jid]["name"] == "My UnAvailable Friend"

    assert "presence" not in contacts[bare_jid]


def test_get_contact(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Friend"

    agent.presence.roster._update_entry(item)

    contact = agent.presence.get_contact(jid)

    assert type(contact) == dict
    assert contact["approved"]
    assert contact["name"] == "My Friend"
    assert contact["subscription"] == "none"
    assert "ask" not in contact
    assert "groups" not in contact


def test_get_invalid_jid_contact():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    with pytest.raises(ContactNotFound):
        agent.presence.get_contact(JID.fromstr("invalid@contact"))


def test_get_invalid_str_contact():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    with pytest.raises(AttributeError):
        agent.presence.get_contact("invalid@contact")


def test_subscribe(jid):
    peer_jid = str(jid)
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.client.enqueue = Mock()
    agent.presence.subscribe(peer_jid)

    assert agent.client.enqueue.mock_calls
    arg = agent.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBE


def test_unsubscribe(jid):
    peer_jid = str(jid)
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.client.enqueue = Mock()
    agent.presence.unsubscribe(peer_jid)

    assert agent.client.enqueue.mock_calls
    arg = agent.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.UNSUBSCRIBE


def test_approve(jid):
    peer_jid = str(jid)
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.client.enqueue = Mock()
    agent.presence.approve(peer_jid)

    assert agent.client.enqueue.mock_calls
    arg = agent.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBED


def test_on_available(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_available = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    jid_arg = agent.presence.on_available.call_args[0][0]
    stanza_arg = agent.presence.on_available.call_args[0][1]

    assert jid_arg == str(jid)
    assert stanza_arg.type_ == PresenceType.AVAILABLE


def test_on_unavailable(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_unavailable = Mock()
    agent.presence.presenceclient._presences[jid.bare()] = {"home": None}

    stanza = Presence(from_=jid, type_=PresenceType.UNAVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    jid_arg = agent.presence.on_unavailable.call_args[0][0]
    stanza_arg = agent.presence.on_unavailable.call_args[0][1]

    assert jid_arg == str(jid)
    assert stanza_arg.type_ == PresenceType.UNAVAILABLE


def test_on_subscribe(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_subscribe = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBE)
    agent.presence.roster.handle_subscribe(stanza)

    jid_arg = agent.presence.on_subscribe.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_subscribe_approve_all(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.approve_all = True
    agent.client.enqueue = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBE)
    agent.presence.roster.handle_subscribe(stanza)

    assert agent.client.enqueue.mock_calls
    arg = agent.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBED


def test_on_subscribed(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_subscribed = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBED)
    agent.presence.roster.handle_subscribed(stanza)

    jid_arg = agent.presence.on_subscribed.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_unsubscribe(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_unsubscribe = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBE)
    agent.presence.roster.handle_unsubscribe(stanza)

    jid_arg = agent.presence.on_unsubscribe.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_unsubscribe_approve_all(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.approve_all = True
    agent.client.enqueue = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBE)
    agent.presence.roster.handle_unsubscribe(stanza)

    assert agent.client.enqueue.mock_calls
    arg = agent.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.UNSUBSCRIBED


def test_on_unsubscribed(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    agent.presence.on_unsubscribed = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBED)
    agent.presence.roster.handle_unsubscribed(stanza)

    jid_arg = agent.presence.on_unsubscribed.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_changed(jid):
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Friend"

    agent.presence.roster._update_entry(item)

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE, show=PresenceShow.CHAT)
    agent.presence.presenceclient.handle_presence(stanza)

    contact = agent.presence.get_contact(jid)
    assert contact["name"] == "My Friend"
    assert contact["presence"].show == PresenceShow.CHAT

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE, show=PresenceShow.AWAY)
    agent.presence.presenceclient.handle_presence(stanza)

    contact = agent.presence.get_contact(jid)

    assert contact["name"] == "My Friend"
    assert contact["presence"].show == PresenceShow.AWAY


def test_ignore_self_presence():
    agent = MockedPresenceAgentFactory()

    future = agent.start(auto_register=False)
    future.result()

    jid = agent.jid

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE, show=PresenceShow.CHAT)
    agent.presence.presenceclient.handle_presence(stanza)

    with pytest.raises(ContactNotFound):
        agent.presence.get_contact(jid)

    assert len(agent.presence.get_contacts()) == 0
