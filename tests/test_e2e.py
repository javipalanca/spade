import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio
from pyjabber.server import Server
from pyjabber.server_parameters import Parameters
from slixmpp import Presence

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.presence import Contact
from spade.template import Template

JID = "test@localhost"
JID2 = "test2@localhost"
PWD = "1234"


@pytest_asyncio.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="function")
async def server(event_loop):
    server = Server(Parameters(database_in_memory=True))
    task = event_loop.create_task(server.start())
    yield task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_connection():
    class DummyAgent(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.res = ""

        class DummyBehav(OneShotBehaviour):
            async def run(self):
                self.agent.res += f"Hello World! I'm agent {JID}"
                await self.agent.stop()

        async def setup(self):
            self.add_behaviour(self.DummyBehav())

    dummy = DummyAgent(JID, PWD)

    await dummy.start()
    await spade.wait_until_finished([dummy])

    assert dummy.res == f"Hello World! I'm agent {JID}"


@pytest.mark.asyncio
async def test_msg_via_container():
    msg = Message(to=f"{JID}/1")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}/1"

    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                await self.send(msg)
                self.kill(exit_code=0)

            async def on_end(self):
                await self.agent.stop()

        async def setup(self):
            b = self.InformBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.res = ""

        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=5)
                if msg_res:
                    self.agent.res = msg_res.body

                self.kill(exit_code=0)

            async def on_end(self):
                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    receiver = ReceiverAgent(f"{JID}/1", PWD)
    sender = SenderAgent(f"{JID}/2", PWD)

    await receiver.start()
    await sender.start()
    await spade.wait_until_finished(receiver)

    assert receiver.res == msg.body


@pytest.mark.asyncio
async def test_msg_via_xmpp():
    msg = Message(to=f"{JID}")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}"

    class SenderAgent(Agent):
        class SendBehav(OneShotBehaviour):
            async def run(self):
                await self.send(msg)

        async def setup(self):
            b = self.SendBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.res = ""

        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=10)
                if msg_res:
                    self.agent.res = msg.body
                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    receiver = ReceiverAgent(f"{JID}", PWD)
    sender = SenderAgent(f"{JID2}", PWD)

    with patch("spade.container.Container.send") as mock_send:

        async def send(*args):
            await args[1]._xmpp_send(msg=args[0])

        mock_send.side_effect = send

        await spade.start_agents([receiver])
        await spade.start_agents([sender])
        await spade.wait_until_finished(receiver)
        await sender.stop()

    assert receiver.res == msg.body


@pytest.mark.asyncio
async def test_presence_subscribe():
    class Agent1(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.presence_trace = []

        async def setup(self):
            self.add_behaviour(self.Behav1())

        class Behav1(OneShotBehaviour):
            def on_subscribe(self, jid):
                self.presence.approve_subscription(jid)

            def on_subscribed(self, peer_jid):
                pass

            def on_presence_received(self, presence: Presence):
                asyncio.create_task(self.agent.stop())

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_presence_received = self.on_presence_received
                self.presence.subscribe(self.agent.jid2)

    class Agent2(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.presence_trace = []

        async def setup(self):
            self.add_behaviour(self.Behav2())

        class Behav2(OneShotBehaviour):
            def on_subscribe(self, jid):
                self.presence.approve_subscription(jid)
                self.presence.subscribe(jid)

            def on_subscribed(self, peer_jid):
                pass

            def on_presence_received(self, presence: Presence):
                asyncio.create_task(self.agent.stop())

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_presence_received = self.on_presence_received

    agent2 = Agent2(JID2, PWD)
    agent1 = Agent1(JID, PWD)
    agent1.jid2 = JID2
    agent2.jid1 = JID

    await agent2.start()
    await agent1.start()
    try:
        await asyncio.wait_for(spade.wait_until_finished([agent1, agent2]), 3)
    except asyncio.TimeoutError:
        pass

    assert JID2 in agent1.presence.get_contacts()
    contact2: Contact = agent1.presence.get_contact(JID2)
    assert contact2.jid == JID2
    assert contact2.subscription == "both"

    assert JID in agent2.presence.get_contacts()
    contact1: Contact = agent2.presence.get_contact(JID)
    assert contact1.jid == JID
    assert contact1.subscription == "both"
