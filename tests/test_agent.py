import asyncio

import aioxmpp
from aioxmpp import PresenceManagedClient
from asynctest import CoroutineMock, Mock
from testfixtures import LogCapture

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from tests.utils import make_connected_agent, run_around_tests


def test_create_agent(mocker):
    agent = Agent("jid@server", "fake_password")
    agent._async_connect = CoroutineMock()

    assert agent.is_alive() is False

    future = agent.start(auto_register=False)
    assert future.result() is None

    agent._async_connect.assert_called_once()
    assert agent.stream is None

    agent.conn_coro = mocker.Mock()
    agent.conn_coro.__aexit__ = CoroutineMock()

    assert agent.is_alive() is True
    future = agent.stop()
    future.result()

    agent.conn_coro.__aexit__.assert_called_once()

    assert agent.is_alive() is False


def test_connected_agent():
    agent = make_connected_agent()
    assert agent.is_alive() is False

    future = agent.start(auto_register=False)
    assert future.result() is None
    assert agent.is_alive() is True

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


def test_name():
    agent = make_connected_agent(jid="john@fake_server")
    assert agent.name == "john"


def test_avatar():
    agent = make_connected_agent(jid="test_avatar@fake_server")
    assert agent.avatar == "http://www.gravatar.com/avatar/44bdc5585ef57844edb11c5b9711d2e6?d=monsterid"


def test_setup():
    agent = make_connected_agent()
    agent.setup = CoroutineMock()
    future = agent.start(auto_register=False)
    assert future.result() is None

    agent.setup.assert_called_once()
    agent.stop()


def test_set_get():
    agent = make_connected_agent()
    agent.set("KB_name", "KB_value")
    assert agent.get("KB_name") == "KB_value"


def test_get_none():
    agent = make_connected_agent()
    assert agent.get("KB_name_unknown") is None


def test_client():
    agent = make_connected_agent()
    assert agent.client is None

    future = agent.start()
    future.result()
    assert type(agent.client) == PresenceManagedClient


def test_register():
    agent = make_connected_agent()
    agent.register = Mock()

    future = agent.start(auto_register=True)
    assert future.result() is None

    assert len(agent._async_register.mock_calls) == 1

    agent.stop()


def test_receive_without_behaviours():
    agent = make_connected_agent()
    aiomsg = aioxmpp.Message(type_=aioxmpp.MessageType.CHAT)
    msg = Message.from_node(aiomsg)

    assert agent.traces.len() == 0
    future = agent.start(auto_register=False)
    assert future.result() is None

    with LogCapture() as log:
        agent._message_received(aiomsg)
        log.check_present(('spade.Agent', 'WARNING', f"No behaviour matched for message: {msg}"))

    assert agent.traces.len() == 1
    assert msg in agent.traces.store[0]

    agent.stop()


def test_create_agent_from_another_agent():
    class DummyBehav(OneShotBehaviour):
        async def run(self):
            self.agent._done = True
            self.kill()

    class CreateBehav(OneShotBehaviour):
        async def run(self):
            self.agent.agent2 = make_connected_agent()
            self.agent.agent2._done = False
            self.agent.agent2.add_behaviour(DummyBehav())
            await self.agent.agent2.start(auto_register=False)
            self.kill()

    agent1 = make_connected_agent()
    agent1.agent2 = None
    agent1.add_behaviour(CreateBehav())
    future = agent1.start(auto_register=False)
    assert future.result() is None
    assert agent1.is_alive()

    agent1.behaviours[0].join()
    agent1.agent2.behaviours[0].join()

    assert agent1.agent2.is_alive()
    assert agent1.agent2._done

    agent1.agent2.stop()
    agent1.stop()


def test_create_agent_from_another_agent_from_setup():
    class DummyBehav(OneShotBehaviour):
        async def run(self):
            self.agent._done = True
            self.kill()

    class SetupAgent(Agent):
        async def setup(self):
            self.agent2 = make_connected_agent()
            self.agent2._done = False
            self.agent2.add_behaviour(DummyBehav())
            await self.agent2.start(auto_register=False)

    agent1 = SetupAgent("fake@host", "secret")
    agent1._async_connect = CoroutineMock()
    agent1._async_register = CoroutineMock()
    agent1.conn_coro = Mock()
    agent1.conn_coro.__aexit__ = CoroutineMock()
    agent1.stream = Mock()

    agent1.agent2 = None

    future = agent1.start(auto_register=False)
    assert future.result() is None
    assert agent1.is_alive()

    agent1.agent2.behaviours[0].join()

    assert agent1.agent2.is_alive()
    assert agent1.agent2._done

    agent1.agent2.stop()
    agent1.stop()


def test_submit_send():
    agent = make_connected_agent()

    class DummyBehav(OneShotBehaviour):
        async def run(self):
            msg_to_send = Message(to="fake@jid", body="BODY", metadata={"performative": "TEST"})
            coro = self.send(msg_to_send)
            self.agent.submit(coro)
            self.kill()

    template = Template(to="fake@jid")
    behah = DummyBehav()
    agent.add_behaviour(behah, template=template)

    future = agent.start(auto_register=False)
    future.result()

    behah.join()

    assert behah.queue.qsize() == 1
    msg = behah.queue.get_nowait()
    assert str(msg.to) == "fake@jid"
    assert msg.body == "BODY"
    assert msg.metadata == {"performative": "TEST"}


def test_stop_agent_with_blocking_await():
    agent1 = make_connected_agent()
    agent1.value = 1000

    class StopBehav(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(0.5)
            await self.agent.stop()

    class DummyBehav(OneShotBehaviour):
        async def run(self):
            await self.receive(timeout=1000000)
            self.agent.value = 2000

    stopbehah = StopBehav()
    dummybehav = DummyBehav()

    agent1.add_behaviour(dummybehav)
    agent1.add_behaviour(stopbehah)

    future1 = agent1.start(auto_register=False)
    future1.result()

    stopbehah.join()

    assert not agent1.is_alive()
    assert agent1.value == 1000
