import time
import pytest
from aioxmpp import PresenceShow, PresenceState
from asynctest import Mock, CoroutineMock

from spade.agent import Agent
from spade.container import Container
from spade import quit_spade


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


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = CoroutineMock()
        self._async_register = CoroutineMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = CoroutineMock()
        self.stream = Mock()


def make_connected_agent(jid="fake@jid", password="fake_password"):
    return MockedConnectedAgent(jid, password)


class MockedPresenceConnectedAgent(Agent):
    def __init__(self,
                 available=None,
                 show=None,
                 status=None,
                 priority=0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        if status is None:
            status = {}
        self._async_connect = CoroutineMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = CoroutineMock()

        self.available = available
        self.show = show
        self.status = status
        self.priority = priority

    def mock_presence(self):
        show = self.show if self.show is not None else PresenceShow.NONE
        available = self.available if self.available is not None else False
        state = PresenceState(available, show)
        self.presence.presenceserver.set_presence(state, self.status, self.priority)


def make_presence_connected_agent(jid="fake@jid", password="fake_password",
                                  available=None,
                                  show=None,
                                  status=None,
                                  priority=0):
    status = {} if status is None else status
    return MockedPresenceConnectedAgent(jid=jid, password=password,
                                        available=available,
                                        show=show,
                                        status=status,
                                        priority=priority)


def wait_for_behaviour_is_killed(behaviour, tries=500, sleep=0.01):
    counter = 0
    while not behaviour.is_killed() and counter < tries:
        time.sleep(sleep)
        counter += 1
    if not behaviour.is_killed():
        raise Exception("Behaviour not finished")
