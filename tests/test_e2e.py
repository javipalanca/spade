import asyncio
import io
from unittest.mock import patch
from uuid import uuid4

import pytest
from slixmpp import Presence

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.presence import Contact
from spade.template import Template

pytestmark = pytest.mark.e2e


async def test_connection():
    jid = f"{str(uuid4())}@localhost"

    class DummyAgent(Agent):
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.res = ""

        class DummyBehav(OneShotBehaviour):
            async def run(self):
                self.agent.res += f"Hello World! I'm agent {jid}"
                await self.agent.stop()

        async def setup(self):
            self.add_behaviour(self.DummyBehav())

    dummy = DummyAgent(jid, "1234")

    await dummy.start()
    await spade.wait_until_finished([dummy])

    assert dummy.res == f"Hello World! I'm agent {jid}"


async def test_msg_via_container():
    jid = f"{str(uuid4())}@localhost"

    msg = Message(to=f"{jid}/1")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {jid}/1"

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

    receiver = ReceiverAgent(f"{jid}/1", "1234")
    sender = SenderAgent(f"{jid}/2", "1234")

    await receiver.start()
    await sender.start()
    await spade.wait_until_finished(receiver)
    await sender.stop()

    assert receiver.res == msg.body


async def test_msg_via_xmpp():
    jid = f"{str(uuid4())}@localhost"
    jid2 = f"{str(uuid4())}@localhost"

    msg = Message(to=f"{jid}")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {jid}"

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

    receiver = ReceiverAgent(f"{jid}", "1234")
    sender = SenderAgent(f"{jid2}", "1234")

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
    jid = f"{str(uuid4())}@localhost"
    jid2 = f"{str(uuid4())}@localhost"

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

    agent2 = Agent2(jid2, "1234")
    agent1 = Agent1(jid, "1234")
    agent1.jid2 = jid2
    agent2.jid1 = jid

    await agent2.start()
    await agent1.start()
    try:
        await asyncio.wait_for(spade.wait_until_finished([agent1, agent2]), 3)
    except asyncio.TimeoutError:
        pass

    assert jid2 in agent1.presence.get_contacts()
    contact2: Contact = agent1.presence.get_contact(jid2)
    assert contact2.jid == jid2
    assert contact2.subscription == "both"

    assert jid in agent2.presence.get_contacts()
    contact1: Contact = agent2.presence.get_contact(jid)
    assert contact1.jid == jid
    assert contact1.subscription == "both"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Wait until fix on PyJabber")
async def test_send_file(tmp_path):
    mock_input_file = io.BytesIO(b"Testing!")

    class UploadBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.url = await self.send_file(
                filename="test.txt", input_file=mock_input_file
            )
            msg = Message(
                to=self.agent.jid_to_send, metadata={"0363_url": self.agent.url}
            )
            await self.send(msg)
            self.kill()

    class DownloadBehaviour(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(10)
            if msg:
                self.agent.url = msg.get_metadata("0363_url")
            self.kill()

    uploader: Agent = Agent(jid="uploader@localhost", password="1234")
    up_beh = UploadBehaviour()
    uploader.add_behaviour(up_beh)
    downloader: Agent = Agent(jid="downloader@localhost", password="1234")
    down_beh = DownloadBehaviour()
    downloader.add_behaviour(down_beh)

    await asyncio.gather(*[uploader.start(), downloader.start()])
    assert uploader.is_alive() and downloader.is_alive()

    await asyncio.gather(*[up_beh.join(), down_beh.join()])

    assert uploader.url is not None
    assert downloader.url is not None
    assert uploader.url == downloader.url
