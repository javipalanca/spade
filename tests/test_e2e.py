import asyncio
from unittest.mock import patch, MagicMock

import pytest
from singletonify import _Box

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.container import Container
from spade.message import Message
from spade.presence import PresenceType, Contact
from spade.template import Template

JID = "test@localhost"
JID2 = "test2@localhost"
PWD = "1234"


@pytest.fixture(autouse=True)
async def cleanup():
    # The Container class is a Singleton, and is reused across all the test
    # SPADE run closes the container event loop on the spade.run() exit, and blocks
    # further executions in the session. It's necessary to force a new instance of the
    # Container class to make sure each test retrieves a new event loop in order to work
    # Singleton Issue ==> https://github.com/Cologler/singletonify-python/issues/1
    for closure_cell in Container.__class__.__call__.__closure__:
        if isinstance(closure_cell.cell_contents, _Box):
            box = closure_cell.cell_contents    # this should be the box instance
            box.value = None                    # set to None

    yield


def test_connection(capsys):
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

    async def main():
        await spade.start_agents([dummy])
        await spade.wait_until_finished([dummy])

    spade.run(main(), True)
    assert dummy.res == f"Hello World! I'm agent {JID}"


def test_msg_via_container(capsys):
    msg = Message(to=f"{JID}/1")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}/1"

    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                await self.send(msg)
                await self.agent.stop()

        async def setup(self):
            b = self.InformBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=10)
                if msg_res:
                    print(msg_res.body)

                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    async def main():
        receiver = ReceiverAgent(f"{JID}/1", PWD)
        sender = SenderAgent(f"{JID}/2", PWD)

        await spade.start_agents([receiver, sender])
        await spade.wait_until_finished(receiver)

    spade.run(main(), True)

    assert msg.body in capsys.readouterr().out


def test_msg_via_xmpp(capsys):
    msg = Message(to=f"{JID}")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}"

    msg_res_future = asyncio.Future()

    class SenderAgent(Agent):
        class SendBehav(OneShotBehaviour):
            async def run(self):
                await self.send(msg)
                await self.agent.stop()

        async def setup(self):
            b = self.SendBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=5)
                if msg_res:
                    msg_res_future.set_result(msg.body)
                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    async def main():
        with patch('spade.container.Container.send') as mock_send:
            async def send(*args):
                await args[1]._xmpp_send(msg=args[0])

            mock_send.side_effect = send

            receiver = ReceiverAgent(f"{JID}", PWD)
            sender = SenderAgent(f"{JID2}", PWD)

            await spade.start_agents([receiver, sender])
            await spade.wait_until_finished(receiver)

    spade.run(main(), True)

    assert msg_res_future.result() == msg.body


def test_presence_subscribe():
    class Agent1(Agent):
        async def setup(self):
            self.add_behaviour(self.Behav1())

        class Behav1(OneShotBehaviour):
            def on_subscribe(self, jid):
                self.presence.approve_subscription(jid)
                asyncio.create_task(self.agent.stop())

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.set_presence(PresenceType.AVAILABLE)
                self.presence.subscribe(self.agent.jid2)

    class Agent2(Agent):
        async def setup(self):
            self.add_behaviour(self.Behav2())

        class Behav2(OneShotBehaviour):
            def on_subscribe(self, jid):
                self.presence.approve_subscription(jid)
                self.presence.subscribe(jid)
                asyncio.create_task(self.agent.stop())

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.set_presence(PresenceType.AVAILABLE)

    async def main():
        agent2 = Agent2(JID2, PWD)
        agent1 = Agent1(JID, PWD)
        agent1.jid2 = JID2
        agent2.jid1 = JID
        await agent2.start()
        await agent1.start()

        await spade.wait_until_finished([agent1, agent2])

        try:
            await asyncio.wait_for(spade.wait_until_finished([agent1, agent2]), 10)
        except asyncio.TimeoutError:
            assert pytest.fail()

        assert JID in agent1.presence.get_contacts()
        contact1: Contact = agent1.presence.get_contact(JID)
        assert contact1.jid == JID
        assert contact1.subscription == 'both'

        assert JID2 in agent2.presence.get_contacts()
        contact2: Contact = agent2.presence.get_contact(JID2)
        assert contact2.jid == JID
        assert contact2.subscription == 'both'

    spade.run(main(), True)
