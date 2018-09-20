from aioxmpp import PresenceShow, PresenceState
from asynctest import Mock, CoroutineMock

from spade.agent import Agent


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiothread.connect = Mock()
        self.aiothread.async_connect = CoroutineMock()
        self.async_register = CoroutineMock()
        self.aiothread.conn_coro = Mock()
        self.aiothread.conn_coro.__aexit__ = CoroutineMock()
        self.aiothread.stream = Mock()


def make_connected_agent(jid="fake@jid", password="fake_password", loop=None):
    return MockedConnectedAgent(jid, password, loop=loop)


class MockedPresenceConnectedAgent(Agent):
    def __init__(self,
                 available=None,
                 show=None,
                 status={},
                 priority=0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiothread.connect = Mock()
        self.aiothread.async_connect = CoroutineMock()
        self.aiothread.conn_coro = Mock()
        self.aiothread.conn_coro.__aexit__ = CoroutineMock()

        show = show if show is not None else PresenceShow.NONE
        available = available if available is not None else False
        state = PresenceState(available, show)
        self.presence.presenceserver.set_presence(state, status, priority)


def make_presence_connected_agent(jid="fake@jid", password="fake_password",
                                  available=None,
                                  show=None,
                                  status=None,
                                  priority=0,
                                  loop=None):
    status = {} if status is None else status
    return MockedPresenceConnectedAgent(jid=jid, password=password,
                                        available=available,
                                        show=show,
                                        status=status,
                                        priority=priority,
                                        loop=loop)
