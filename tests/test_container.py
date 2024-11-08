import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock

from slixmpp import JID

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.container import Container
from spade.message import Message
from .factories import MockedAgentFactory


async def test_use_container():
    container = Container()
    container.reset()

    agent = MockedAgentFactory()

    assert agent.container == Container()

    assert container.has_agent(str(agent.jid))
    assert container.get_agent(str(agent.jid)) == agent

    await agent.stop()


async def test_send_message_with_container():
    class FakeReceiverAgent:
        def __init__(self):
            self.jid = "fake_receiver_agent@server"

        def set_container(self, c):
            pass

        def set_loop(self, loop):
            pass

        def stop(self):
            pass

        def is_alive(self):
            return False

    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            message = Message(to="fake_receiver_agent@server")
            await self.send(message)
            self.kill()

    container = Container()
    container.reset()
    fake_receiver_agent = FakeReceiverAgent()
    container.register(fake_receiver_agent)

    fake_receiver_agent.dispatch = MagicMock()

    agent = MockedAgentFactory()
    await agent.start(auto_register=False)

    agent.client.send = Mock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    await behaviour.join()

    assert agent.client.send.call_count == 0

    assert fake_receiver_agent.dispatch.call_count == 1
    assert (
        str(fake_receiver_agent.dispatch.call_args[0][0].to)
        == "fake_receiver_agent@server"
    )

    await agent.stop()


async def test_send_message_to_outer_with_container():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            message = Message(to="to@outerhost")
            await self.send(message)
            self.kill()

    container = Container()
    container.reset()

    agent = MockedAgentFactory()
    await agent.start(auto_register=False)

    behaviour = SendBehaviour()
    behaviour._xmpp_send = AsyncMock()
    agent.add_behaviour(behaviour)

    await behaviour.join()

    assert container.has_agent(str(agent.jid))
    assert not container.has_agent("to@outerhost")

    assert behaviour._xmpp_send.await_count == 1

    args, kwargs = behaviour._xmpp_send.await_args
    msg_arg = kwargs["msg"]
    assert msg_arg.to == JID("to@outerhost")

    await agent.stop()


def test_unregister():
    container = Container()

    agent = MockedAgentFactory()
    agent2 = MockedAgentFactory(jid="agent2@server")

    assert container.has_agent(str(agent.jid))
    assert container.has_agent(str(agent2.jid))

    container.unregister(agent.jid)

    assert not container.has_agent(str(agent.jid))
    assert container.has_agent(str(agent2.jid))


async def test_cancel_tasks():
    agent = MockedAgentFactory()

    class Behav(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(100)
            self.has_finished = True

    behav = Behav()
    behav.has_finished = False
    agent.add_behaviour(behaviour=behav)
    await agent.start()

    assert not behav.has_finished

    await agent.stop()

    assert not behav.has_finished
