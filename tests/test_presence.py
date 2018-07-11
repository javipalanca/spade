from unittest.mock import Mock

from aioxmpp import PresenceState, PresenceShow, JID, PresenceType, Presence
from aioxmpp.roster import Item
from aioxmpp.roster.xso import Item as XSOItem
from pytest import fixture

from tests.utils import make_presence_connected_agent


@fixture
def jid():
    return JID.fromstr("friend@localhost/home")


def test_get_state_not_available():
    agent = make_presence_connected_agent(available=False, show=PresenceShow.NONE)

    assert type(agent.presence.state) == PresenceState
    assert agent.presence.state.available is False
    assert agent.presence.state.show == PresenceShow.NONE
    assert not agent.presence.is_available()


def test_get_state_available():
    agent = make_presence_connected_agent(available=True)

    assert agent.presence.state.available
    assert agent.presence.is_available()


def test_set_available():
    agent = make_presence_connected_agent()
    agent.presence.set_available()

    assert agent.presence.is_available()


def test_set_available_with_show():
    agent = make_presence_connected_agent()
    agent.presence.set_available(show=PresenceShow.CHAT)

    assert agent.presence.is_available()
    assert agent.presence.state.show == PresenceShow.CHAT


def test_set_unavailable():
    agent = make_presence_connected_agent()
    agent.presence.set_unavailable()

    assert not agent.presence.is_available()


def test_get_state_show():
    agent = make_presence_connected_agent(available=True, show=PresenceShow.AWAY)

    assert agent.presence.state.show == PresenceShow.AWAY


def test_get_status_empty():
    agent = make_presence_connected_agent(status={})

    assert agent.presence.status == {}


def test_get_status_string():
    agent = make_presence_connected_agent(status="Working")

    assert agent.presence.status == {None: "Working"}


def test_get_status_dict():
    agent = make_presence_connected_agent(status={"en": "Working"})

    assert agent.presence.status == {"en": "Working"}


def test_get_priority_default():
    agent = make_presence_connected_agent()

    assert agent.presence.priority == 0


def test_get_priority():
    agent = make_presence_connected_agent(priority=10)

    assert agent.presence.priority == 10


def test_set_presence_available():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(state=PresenceState(available=True))

    assert agent.presence.is_available()


def test_set_presence_unavailable():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(state=PresenceState(available=False))

    assert not agent.presence.is_available()


def test_set_presence_status():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(status="Lunch")

    assert agent.presence.status == {None: "Lunch"}


def test_set_presence_status_dict():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(status={"en": "Lunch"})

    assert agent.presence.status == {"en": "Lunch"}


def test_set_presence_priority():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(priority=5)

    assert agent.presence.priority == 5


def test_set_presence():
    agent = make_presence_connected_agent()

    agent.presence.set_presence(
        state=PresenceState(True, PresenceShow.PLAIN),
        status="Lunch",
        priority=2
    )

    assert agent.presence.is_available()
    assert agent.presence.state.show == PresenceShow.PLAIN
    assert agent.presence.status == {None: "Lunch"}
    assert agent.presence.priority == 2


def test_get_contacts_empty():
    agent = make_presence_connected_agent()

    assert agent.presence.get_contacts() == {}


def test_get_contacts(jid):
    agent = make_presence_connected_agent()

    item = XSOItem(jid=jid)
    item.approved = True
    item.name = "My Friend"

    agent.presence.roster._update_entry(item)

    contacts = agent.presence.get_contacts()

    assert jid in contacts
    assert type(contacts[jid]) == Item
    assert contacts[jid].approved
    assert contacts[jid].name == "My Friend"
    assert contacts[jid].ask is None
    assert contacts[jid].jid == jid
    assert contacts[jid].subscription == 'none'
    assert len(contacts[jid].groups) == 0


def test_subscribe(jid):
    peer_jid = str(jid)
    agent = make_presence_connected_agent()

    agent.aiothread.client.enqueue = Mock()
    agent.presence.subscribe(peer_jid)

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBE


def test_unsubscribe(jid):
    peer_jid = str(jid)
    agent = make_presence_connected_agent()

    agent.aiothread.client.enqueue = Mock()
    agent.presence.unsubscribe(peer_jid)

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.UNSUBSCRIBE


def test_approve(jid):
    peer_jid = str(jid)
    agent = make_presence_connected_agent()

    agent.aiothread.client.enqueue = Mock()
    agent.presence.approve(peer_jid)

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBED


def test_on_available(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_available = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.AVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    jid_arg = agent.presence.on_available.call_args[0][0]
    stanza_arg = agent.presence.on_available.call_args[0][1]

    assert jid_arg == str(jid)
    assert stanza_arg.type_ == PresenceType.AVAILABLE


def test_on_unavailable(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_unavailable = Mock()
    agent.presence.presenceclient._presences[jid.bare()] = {"home": None}

    stanza = Presence(from_=jid, type_=PresenceType.UNAVAILABLE)
    agent.presence.presenceclient.handle_presence(stanza)

    jid_arg = agent.presence.on_unavailable.call_args[0][0]
    stanza_arg = agent.presence.on_unavailable.call_args[0][1]

    assert jid_arg == str(jid)
    assert stanza_arg.type_ == PresenceType.UNAVAILABLE


def test_on_subscribe(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_subscribe = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBE)
    agent.presence.roster.handle_subscribe(stanza)

    jid_arg = agent.presence.on_subscribe.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_subscribe_approve_all(jid):
    agent = make_presence_connected_agent()
    agent.presence.approve_all = True
    agent.aiothread.client.enqueue = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBE)
    agent.presence.roster.handle_subscribe(stanza)

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.SUBSCRIBED


def test_on_subscribed(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_subscribed = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.SUBSCRIBED)
    agent.presence.roster.handle_subscribed(stanza)

    jid_arg = agent.presence.on_subscribed.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_unsubscribe(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_unsubscribe = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBE)
    agent.presence.roster.handle_unsubscribe(stanza)

    jid_arg = agent.presence.on_unsubscribe.call_args[0][0]

    assert jid_arg == str(jid)


def test_on_unsubscribe_approve_all(jid):
    agent = make_presence_connected_agent()
    agent.presence.approve_all = True
    agent.aiothread.client.enqueue = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBE)
    agent.presence.roster.handle_unsubscribe(stanza)

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid.bare()
    assert arg.type_ == PresenceType.UNSUBSCRIBED


def test_on_unsubscribed(jid):
    agent = make_presence_connected_agent()
    agent.presence.on_unsubscribed = Mock()

    stanza = Presence(from_=jid, type_=PresenceType.UNSUBSCRIBED)
    agent.presence.roster.handle_unsubscribed(stanza)

    jid_arg = agent.presence.on_unsubscribed.call_args[0][0]

    assert jid_arg == str(jid)
