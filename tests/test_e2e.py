import asyncio
import threading

import pytest

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.presence import PresenceType
from spade.template import Template

JID = "test@localhost"
JID2 = "test2@localhost"
PWD = "1234"


@pytest.mark.asyncio
async def test_connection(server, capsys):
    class DummyAgent(Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))

    dummy = DummyAgent(JID, PWD)
    await dummy.start()
    await dummy.stop()

    output = capsys.readouterr().out
    assert output in f"Hello World! I'm agent {JID}\n"


@pytest.mark.asyncio
async def test_msg_via_container(server, capsys):
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

    receiver = ReceiverAgent(f"{JID}/1", PWD)
    sender = SenderAgent(f"{JID}/2", PWD)
    await spade.start_agents([receiver, sender])
    await spade.wait_until_finished(receiver)

    assert msg.body in capsys.readouterr().out

@pytest.mark.asyncio
async def test_msg_via_xmpp(server, capsys):
    msg = Message(to=f"{JID}")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}"

    msg_received = asyncio.Future()

    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                self.agent.container.reset()
                await self.send(msg)
                await self.agent.stop()

        async def setup(self):
            b = self.InformBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=5)
                if msg_res:
                    msg_received.set_result(msg.body)
                else:
                    msg_received.set_result("NOT RECEIVED")

                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    receiver = ReceiverAgent(f"{JID}", PWD)
    sender = SenderAgent(f"{JID2}", PWD)

    loop = server

    receiver_task = loop.create_task(receiver.start())
    sender_task = loop.create_task(sender.start())

    await asyncio.gather(receiver_task, sender_task)
    try:
        res = await msg_received
        assert f"Hello World {JID}" in res
    except AssertionError as e:
        pytest.fail()
    except Exception as e:
        pytest.fail("TEST ERROR")

@pytest.mark.asyncio
async def test_msg_via_xmpp2(server, capsys):
    msg = Message(to=f"test")
    msg.set_metadata("performative", "inform")
    msg.body = f"Hello World {JID}"

    msg_received = asyncio.Future()

    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                self.agent.container.reset()
                await self.send(msg)
                await self.agent.stop()

        async def setup(self):
            b = self.InformBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        class RecvBehav(OneShotBehaviour):
            async def run(self):
                msg_res = await self.receive(timeout=5)
                if msg_res:
                    msg_received.set_result(msg.body)
                else:
                    msg_received.set_result("NOT RECEIVED")

                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)

    receiver = ReceiverAgent(f"{JID}", PWD)
    sender = SenderAgent(f"{JID2}", PWD)

    loop = server

    receiver_task = loop.create_task(receiver.start())
    sender_task = loop.create_task(sender.start())

    await asyncio.gather(receiver_task, sender_task)
    try:
        res = await msg_received
        assert res == f"Hello World {JID}"
    except AssertionError as e:
        pytest.fail()
    except Exception as e:
        pytest.fail("TEST ERROR")

#
# @pytest.mark.asyncio
# async def test_msg_via_xmpp(server, capsys):
#     class Agent1(Agent):
#         async def setup(self):
#             self.add_behaviour(self.Behav1())
#
#         class Behav1(OneShotBehaviour):
#             def on_available(self, jid, presence_info, last_presence):
#                 print(
#                     "[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0])
#                 )
#
#             def on_subscribed(self, jid):
#                 print(
#                     "[{}] Agent {} has accepted the subscription.".format(
#                         self.agent.name, jid.split("@")[0]
#                     )
#                 )
#                 print(
#                     "[{}] Contacts List: {}".format(
#                         self.agent.name, self.agent.presence.get_contacts()
#                     )
#                 )
#
#             def on_subscribe(self, jid):
#                 print(
#                     "[{}] Agent {} asked for subscription. Let's aprove it.".format(
#                         self.agent.name, jid.split("@")[0]
#                     )
#                 )
#                 self.presence.approve_subscription(jid)
#
#             async def run(self):
#                 self.presence.on_subscribe = self.on_subscribe
#                 self.presence.on_subscribed = self.on_subscribed
#                 self.presence.on_available = self.on_available
#
#                 self.presence.set_presence(PresenceType.AVAILABLE)
#                 print(
#                     f"[{self.agent.name}] Agent {self.agent.name} is asking for subscription to {self.agent.jid2}"
#                 )
#                 self.presence.subscribe(self.agent.jid2)
#
#     class Agent2(Agent):
#         async def setup(self):
#             self.add_behaviour(self.Behav2())
#
#         class Behav2(OneShotBehaviour):
#             def on_available(self, jid, presence_info, last_presence):
#                 print(
#                     "[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0])
#                 )
#
#             def on_subscribed(self, jid):
#                 print(
#                     "[{}] Agent {} has accepted the subscription.".format(
#                         self.agent.name, jid.split("@")[0]
#                     )
#                 )
#                 print(
#                     "[{}] Contacts List: {}".format(
#                         self.agent.name, self.agent.presence.get_contacts()
#                     )
#                 )
#
#             def on_subscribe(self, jid):
#                 print(
#                     "[{}] Agent {} asked for subscription. Let's aprove it.".format(
#                         self.agent.name, jid.split("@")[0]
#                     )
#                 )
#                 print(
#                     f"[{self.agent.name}] Agent {self.agent.name} has received a subscription query from {jid}"
#                 )
#                 self.presence.approve_subscription(jid)
#                 print(
#                     f"[{self.agent.name}] And after approving it, Agent {self.agent.name} is asking for subscription to {jid}"
#                 )
#                 self.presence.subscribe(jid)
#
#             async def run(self):
#                 self.presence.set_presence(PresenceType.AVAILABLE)
#                 self.presence.on_subscribe = self.on_subscribe
#                 self.presence.on_subscribed = self.on_subscribed
#                 self.presence.on_available = self.on_available
