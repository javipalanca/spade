import factory
from aioxmpp import PresenceShow, PresenceState
from asynctest import CoroutineMock, Mock

from spade.agent import Agent


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = CoroutineMock()
        self._async_register = CoroutineMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = CoroutineMock()
        self.stream = Mock()


class MockedAgentFactory(factory.Factory):
    class Meta:
        model = MockedConnectedAgent

    jid = "fake@jid"
    password = "fake_password"


class MockedPresenceConnectedAgent(Agent):
    def __init__(
        self, available=None, show=None, status=None, priority=0, *args, **kwargs
    ):
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


class MockedPresenceAgentFactory(factory.Factory):
    class Meta:
        model = MockedPresenceConnectedAgent

    jid = "fake@jid"
    password = "fake_password"
    available = None
    show = None
    status = {}
    priority = 0
