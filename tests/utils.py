from asynctest import Mock, CoroutineMock

from spade.agent import Agent


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiothread.connect = Mock()
        self.aiothread.conn_coro = Mock()
        self.aiothread.conn_coro.__aexit__ = CoroutineMock()


def make_connected_agent(jid="fake@jid", password="fake_password", loop=None):
    return MockedConnectedAgent(jid, password, loop=loop)
