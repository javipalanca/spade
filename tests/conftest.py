import asyncio

import pytest
from slixmpp import JID, Iq

from spade.message import Message


pytest_plugins = "pytest_asyncio"


@pytest.fixture
def jid():
    return JID("friend@localhost/home")


@pytest.fixture
def message():
    return Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={"metadata1": "value1", "metadata2": "value2"},
    )


@pytest.fixture
def message2():
    return Message(
        to="to2@localhost",
        sender="sender2@localhost",
        body="message body",
        thread="thread-id",
    )


@pytest.fixture
def iq():
    iq = Iq()
    iq["type"] = "result"
    iq["id"] = "123"
    iq["to"] = "friend@localhost/home"
    iq["from"] = "localhost"
    # set namespace to roster
    iq["roster"]["xmlns"] = "jabber:iq:roster"
    iq["type"] = "result"
    iq["roster"]["items"] = {
        "friend@localhost": {
            "name": "My Friend",
            "subscription": "both",
            "groups": ["Friends"],
        },
        "friend2@localhost": {
            "name": "User Two",
            "subscription": "to",
            "groups": ["Work"],
        },
    }
    return iq


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    pass


async def wait_for_behaviour_is_killed(behaviour, tries=500, sleep=0.01):
    counter = 0
    while not behaviour.is_killed() and counter < tries:
        await asyncio.sleep(sleep)
        counter += 1
    if not behaviour.is_killed():
        raise Exception("Behaviour not finished")
