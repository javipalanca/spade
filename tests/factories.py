import factory
from unittest.mock import AsyncMock, Mock

from spade.agent import Agent
from spade.presence import PresenceShow, PresenceType


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = AsyncMock()
        self._async_register = AsyncMock()
        self.stream = Mock()


class MockedAgentFactory(factory.Factory):
    class Meta:
        model = MockedConnectedAgent

    jid = "fake@jid"
    password = "fake_password"


class MockedPresenceConnectedAgent(Agent):
    def __init__(
        self,
        available=None,
        show=PresenceShow.NONE,
        status=None,
        priority=0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if status is None:
            status = {}
        self._async_connect = AsyncMock()

        self.available = available
        self.show = show
        self.status = status
        self.priority = priority

    def mock_presence(self):
        show = self.show if self.show is not None else PresenceShow.NONE
        self.presence.set_presence(
            PresenceType.AVAILABLE, show, self.status, self.priority
        )


class MockedPresenceAgentFactory(factory.Factory):
    class Meta:
        model = MockedPresenceConnectedAgent

    jid = "fake@jid.com"
    password = "fake_password"
    available = None
    show = None
    status = {}
    priority = 0
