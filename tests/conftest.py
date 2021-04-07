import time

import pytest
from aioxmpp import JID

from spade import quit_spade
from spade.container import Container
from spade.message import Message


@pytest.fixture
def jid():
    return JID.fromstr("friend@localhost/home")


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


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before your test, for example:
    # A test function will be run at this point
    container = Container()
    if not container.is_running:
        container.__init__()
    yield
    # Code that will run after your test, for example:
    quit_spade()


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    quit_spade()


def wait_for_behaviour_is_killed(behaviour, tries=500, sleep=0.01):
    counter = 0
    while not behaviour.is_killed() and counter < tries:
        time.sleep(sleep)
        counter += 1
    if not behaviour.is_killed():
        raise Exception("Behaviour not finished")
