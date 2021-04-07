import asyncio
import time

import aioxmpp
from asynctest import MagicMock, CoroutineMock

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.container import Container
from spade.message import Message
from .factories import MockedAgentFactory


def test_use_container():
    container = Container()
    container.reset()

    agent = MockedAgentFactory()

    assert agent.container == Container()

    assert container.has_agent(str(agent.jid))
    assert container.get_agent(str(agent.jid)) == agent

    agent.stop()


def test_send_message_with_container():
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
    future = agent.start(auto_register=False)
    future.result()

    agent.client = MagicMock()
    agent.client.send = CoroutineMock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    behaviour.join()

    assert agent.client.send.await_count == 0

    assert fake_receiver_agent.dispatch.call_count == 1
    assert (
        str(fake_receiver_agent.dispatch.call_args[0][0].to)
        == "fake_receiver_agent@server"
    )

    agent.stop()


def test_send_message_to_outer_with_container():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            message = Message(to="to@outerhost")
            await self.send(message)
            self.kill()

    container = Container()
    container.reset()

    agent = MockedAgentFactory()
    agent.start(auto_register=False)

    behaviour = SendBehaviour()
    behaviour._xmpp_send = CoroutineMock()
    agent.add_behaviour(behaviour)

    behaviour.join()

    assert container.has_agent(str(agent.jid))
    assert not container.has_agent("to@outerhost")

    assert behaviour._xmpp_send.await_count == 1
    msg_arg = behaviour._xmpp_send.await_args[0][0]
    assert msg_arg.to == aioxmpp.JID.fromstr("to@outerhost")

    agent.stop()


def test_unregister():
    container = Container()
    container.reset()

    agent = MockedAgentFactory()
    agent2 = MockedAgentFactory(jid="agent2@server")

    assert container.has_agent(str(agent.jid))
    assert container.has_agent(str(agent2.jid))

    container.unregister(agent.jid)

    assert not container.has_agent(str(agent.jid))
    assert container.has_agent(str(agent2.jid))


def test_cancel_tasks():
    agent = MockedAgentFactory()

    class Behav(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(100)
            self.has_finished = True

    behav = Behav()
    behav.has_finished = False
    agent.add_behaviour(behaviour=behav)
    future = agent.start()
    future.result()

    assert not behav.has_finished

    container = Container()
    container.stop()

    assert not behav.has_finished


def test_stop_container():
    agent = MockedAgentFactory()

    class Behav(OneShotBehaviour):
        async def run(self):
            container = Container()
            container.stop()

    behav = Behav()
    agent.add_behaviour(behav)
    future = agent.start(auto_register=False)
    future.result()
    behav.join()

    counter = 0
    while agent.is_alive() and counter < 5:
        time.sleep(0.05)
        counter += 1
    assert not agent.is_alive()
