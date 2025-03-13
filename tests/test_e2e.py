import asyncio
import logging
import threading
import time
from sys import stdout
from unittest.mock import Mock, MagicMock

import loguru
import pytest

import spade
from spade import wait_until_finished, start_agents
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
    loguru.logger.add(
        sink=stdout,
        enqueue=True,
        format="<green>{time}</green> - <level>{level}: {message}</level>",
        level='TRACE',
    )
    logging.getLogger("spade.Agent")
    class DummyAgent(Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))
            await self.stop()

    dummy = DummyAgent(JID, PWD)
    dummy.set_loop(server)
    await start_agents([dummy])
    # await wait_until_finished(dummy)

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
    await start_agents([receiver, sender])
    await wait_until_finished(receiver)

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

    await spade.start_agents([receiver, sender])
    await spade.wait_until_finished([receiver, sender])
    try:
        res = await msg_received
        assert f"Hello World {JID}" in res
    except AssertionError as e:
        pytest.fail()
    except Exception as e:
        pytest.fail("TEST ERROR")

@pytest.mark.asyncio
async def test_ping_pong_container(server, capsys):
    ping_future = asyncio.Future()
    pong_future = asyncio.Future()

    class PingAgent(Agent):
        def __init__(self, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            super().__init__(*args, **kwargs)

        class PingBehav(OneShotBehaviour):
            async def run(self):
                msg = Message(to=self.agent.recv_jid)
                msg.set_metadata("performative", "inform")
                msg.body = "Ping {}".format(self.agent.recv_jid)

                await self.send(msg)
                msg_response = await self.receive(timeout=5)
                if msg_response:
                    pong_future.set_result(msg_response.body)

                await self.agent.stop()

        async def setup(self):
            b = self.PingBehav()
            self.add_behaviour(b)

    class PongAgent(Agent):
        def __init__(self, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            super().__init__(*args, **kwargs)

        class PongBehav(OneShotBehaviour):
            async def run(self):
                msg = await self.receive(timeout=5)
                if msg:
                    ping_future.set_result(msg.body)
                    msg_response = Message(to=self.agent.recv_jid)
                    msg_response.set_metadata("performative", "inform")
                    msg_response.body = "Pong {}".format(self.agent.recv_jid)
                    await self.send(msg_response)

                await self.agent.stop()

        async def setup(self):
            b = self.PongBehav()
            self.add_behaviour(b)

    ping = PingAgent(f"{JID2}", f"{JID}", PWD)
    pong = PongAgent(f"{JID}", f"{JID2}", PWD)

    await start_agents(pong)
    time.sleep(1)
    await start_agents(ping)
    await wait_until_finished([ping, pong])

    assert ping_future.result() == 'Ping test2@localhost'
    assert pong_future.result() == 'Pong test@localhost'


@pytest.mark.asyncio
async def test_ping_pong_xmpp(server, capsys):
    ping_future = asyncio.Future()
    pong_future = asyncio.Future()

    class PingAgent(Agent):
        def __init__(self, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            super().__init__(*args, **kwargs)

        class PingBehav(OneShotBehaviour):
            async def run(self):
                self.agent.container.reset()
                msg = Message(to=self.agent.recv_jid)
                msg.set_metadata("performative", "inform")
                msg.body = "Ping {}".format(self.agent.recv_jid)

                await self.send(msg)
                msg_response = await self.receive(timeout=5)
                if msg_response:
                    pong_future.set_result(msg_response.body)

                await self.agent.stop()

        async def setup(self):
            b = self.PingBehav()
            self.add_behaviour(b)

    class PongAgent(Agent):
        def __init__(self, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            super().__init__(*args, **kwargs)

        class PongBehav(OneShotBehaviour):
            async def run(self):
                msg = await self.receive(timeout=5)
                if msg:
                    ping_future.set_result(msg.body)
                    msg_response = Message(to=self.agent.recv_jid)
                    msg_response.set_metadata("performative", "inform")
                    msg_response.body = "Pong {}".format(self.agent.recv_jid)
                    self.agent.container.reset()
                    await self.send(msg_response)

                await self.agent.stop()

        async def setup(self):
            b = self.PongBehav()
            self.add_behaviour(b)

    ping = PingAgent(f"{JID2}", f"{JID}", PWD)
    pong = PongAgent(f"{JID}", f"{JID2}", PWD)

    await start_agents(pong)
    time.sleep(1)
    await start_agents(ping)
    await wait_until_finished([ping, pong])

    assert ping_future.result() == 'Ping test2@localhost'
    assert pong_future.result() == 'Pong test@localhost'
    # assert ping.

@pytest.mark.asyncio
async def test_ping_pong(server, capsys):
    ping_future = asyncio.Future()
    pong_future = asyncio.Future()

    class PingAgent(Agent):
        def __init__(self, beh, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            self.beh = beh
            super().__init__(*args, **kwargs)

        async def setup(self):
            self.add_behaviour(self.beh)

    class PingBehav(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.recv_jid)
            msg.set_metadata("performative", "inform")
            msg.body = "Ping {}".format(self.agent.recv_jid)

            await self.send(msg)
            msg_response = await self.receive(timeout=5)
            if msg_response:
                pong_future.set_result(msg_response.body)

            await self.agent.stop()

    class PongAgent(Agent):
        def __init__(self, beh, recv_jid, *args, **kwargs):
            self.recv_jid = recv_jid
            self.beh = beh
            super().__init__(*args, **kwargs)

        async def setup(self):
            self.add_behaviour(self.beh)

    class PongBehav(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                ping_future.set_result(msg.body)
                msg_response = Message(to=self.agent.recv_jid)
                msg_response.set_metadata("performative", "inform")
                msg_response.body = "Pong {}".format(self.agent.recv_jid)
                await self.send(msg_response)

            await self.agent.stop()

    ping_beh = PingBehav()
    pong_beh = PongBehav()
    ping = PingAgent(ping_beh, f"{JID2}", f"{JID}", PWD)
    pong = PongAgent(pong_beh, f"{JID}", f"{JID2}", PWD)

    ping.dispatch = MagicMock(side_effect=ping.dispatch)
    pong.dispatch = MagicMock(side_effect=pong.dispatch)

    await start_agents([pong])
    time.sleep(1)
    await start_agents([ping])
    await wait_until_finished([ping, pong])

    assert ping_future.result() == 'Ping test2@localhost'
    assert pong_future.result() == 'Pong test@localhost'
    # assert ping.dispatch.assert_called()
    assert pong.dispatch.assert_called()

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
