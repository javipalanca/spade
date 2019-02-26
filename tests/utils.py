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
        self.async_connect = CoroutineMock()
        self.async_register = CoroutineMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = CoroutineMock()
        self.stream = Mock()


def make_connected_agent(jid="fake@jid", password="fake_password"):
    return MockedConnectedAgent(jid, password)


class MockedPresenceConnectedAgent(Agent):
    def __init__(self,
                 available=None,
                 show=None,
                 status={},
                 priority=0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_connect = CoroutineMock()
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
