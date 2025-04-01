import asyncio
from unittest.mock import patch, MagicMock

import pytest
from singletonify import _Box

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.container import Container
from spade.message import Message
from spade.template import Template

JID = "test@localhost"
JID2 = "test2@localhost"
PWD = "1234"


@pytest.fixture(autouse=True)
async def cleanup():
    yield
    # The Container class is a Singleton, and is reused across all the test
    # SPADE run closes the container event loop on the spade.run() exit, and blocks
    # further executions in the session. It's necessary to force a new instance of the
    # Container class to make sure each test retrieves a new event loop in order to work
    # Singleton Issue ==> https://github.com/Cologler/singletonify-python/issues/1
    for closure_cell in Container.__class__.__call__.__closure__:
        if isinstance(closure_cell.cell_contents, _Box):
            box = closure_cell.cell_contents    # this should be the box instance
            box.value = None                    # set to None


def test_connection(capsys):
    class DummyAgent(Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))
            await self.stop()

    async def main():
        dummy = DummyAgent(JID, PWD)
        await spade.start_agents([dummy])

    spade.run(main(), True)

    output = capsys.readouterr().out
    assert output in f"Hello World! I'm agent {JID}\n"


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
