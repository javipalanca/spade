import asyncio

from testfixtures import LogCapture
from unittest.mock import AsyncMock, Mock

from slixmpp import Message as slixmppMessage

import spade.xmpp_client
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from .factories import MockedAgentFactory


async def test_create_agent(mocker):
    agent = MockedAgentFactory()

    assert agent.is_alive() is False

    await agent.start(auto_register=False)

    agent._async_connect.assert_called_once()

    await agent.stop()

    assert agent.is_alive() is False


def test_name():
    agent = MockedAgentFactory(jid="john@fake.server")
    assert agent.name == "john"


def test_avatar():
    agent = MockedAgentFactory(jid="test_avatar@fake.server")
    assert (
        agent.avatar
        == "http://www.gravatar.com/avatar/c23af06d68b5e37d3589e7a8748e7b6c?d=monsterid"
    )


async def test_setup():
    agent = MockedAgentFactory()
    agent.setup = AsyncMock()

    await agent.start()

    agent.setup.assert_called_once()

    await agent.stop()


def test_set_get():
    agent = MockedAgentFactory()
    agent.set("KB_name", "KB_value")
    assert agent.get("KB_name") == "KB_value"


def test_get_none():
    agent = MockedAgentFactory()
    assert agent.get("KB_name_unknown") is None


async def test_client():
    agent = MockedAgentFactory()
    assert agent.client is None

    await agent.start(auto_register=False)

    assert isinstance(agent.client, spade.xmpp_client.XMPPClient)

    await agent.stop()


#
# async def test_register():
#     agent = MockedAgentFactory()
#     agent.register = Mock()
#
#     await agent.start()
#
#     assert len(agent._async_register.mock_calls) == 1
#
#     await agent.stop()


def test_receive_without_behaviours():
    agent = MockedAgentFactory()
    slimsg = slixmppMessage()
    slimsg.chat()
    msg = Message.from_node(slimsg)

    assert agent.traces.len() == 0

    with LogCapture() as log:
        agent._message_received(slimsg)
        log.check_present(
            ("spade.Agent", "WARNING", f"No behaviour matched for message: {msg}")
        )

    assert agent.traces.len() == 1
    assert msg == agent.traces.store[0][1]


async def test_create_agent_from_another_agent():
    class DummyBehav(OneShotBehaviour):
        async def run(self):
            self.agent._done = True
            self.kill()

    class CreateBehav(OneShotBehaviour):
        async def run(self):
            self.agent.agent2 = MockedAgentFactory()
            self.agent.agent2._done = False
            self.agent.dummy_behav = DummyBehav()
            self.agent.agent2.add_behaviour(self.agent.dummy_behav)
            await self.agent.agent2.start(auto_register=False)
            self.kill()

    agent1 = MockedAgentFactory()
    agent1.agent2 = None
    create_behav = CreateBehav()
    agent1.add_behaviour(create_behav)

    await agent1.start(auto_register=False)

    await create_behav.join()

    assert agent1.agent2._done

    await agent1.stop()


async def test_create_agent_from_another_agent_from_setup():
    class DummyBehav(OneShotBehaviour):
        async def run(self):
            self.agent._done = True
            self.kill()

    class SetupAgent(Agent):
        async def setup(self):
            self.agent2 = MockedAgentFactory()
            self.agent2._done = False
            self.agent2.dummy_behav = DummyBehav()
            self.agent2.add_behaviour(self.agent2.dummy_behav)
            await self.agent2.start(auto_register=False)

    agent1 = SetupAgent("fake@host", "secret")
    agent1._async_connect = AsyncMock()
    agent1._async_register = AsyncMock()
    agent1.conn_coro = Mock()
    agent1.conn_coro.__aexit__ = AsyncMock()
    agent1.stream = Mock()

    agent1.agent2 = None

    await agent1.start(auto_register=False)
    assert agent1.is_alive()

    await agent1.agent2.dummy_behav.join()

    assert agent1.agent2.is_alive()
    assert agent1.agent2._done

    await agent1.agent2.stop()
    await agent1.stop()


async def test_submit_send():
    agent = MockedAgentFactory()

    class DummyBehav(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive(10)

    template = Template(to="fake@jid")
    behav = DummyBehav()
    agent.add_behaviour(behav, template=template)

    await agent.start(auto_register=False)

    msg_to_send = Message(to="fake@jid", body="BODY", metadata={"performative": "TEST"})
    agent.submit(behav.send(msg_to_send))
    await behav.join()

    assert str(agent.recv_msg.to) == "fake@jid"
    assert agent.recv_msg.body == "BODY"
    assert agent.recv_msg.metadata == {"performative": "TEST"}


async def test_stop_agent_with_blocking_await():
    agent1 = MockedAgentFactory()
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

    await agent1.start(auto_register=False)

    await stopbehah.join()

    assert not agent1.is_alive()
    assert agent1.value == 1000
