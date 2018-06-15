from threading import Event

import aioxmpp
import pytest
from pytest import fixture
from asynctest import CoroutineMock, MagicMock

from spade.behaviour import OneShotBehaviour, Behaviour
from spade.message import Message
from tests.utils import make_connected_agent


@fixture
def message():
    return Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={
            "metadata1": "value1",
            "metadata2": "value2"
        }
    )


def test_on_start_on_end():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def on_start(self):
            self.agent.on_start_flag = True

        async def run(self):
            pass

        async def on_end(self):
            self.agent.on_end_flag = True
            self.agent.wait_behaviour.set()

    agent = make_connected_agent()
    agent.on_start_flag = False
    agent.on_end_flag = False
    agent.wait_behaviour = Event()
    agent.add_behaviour(TestOneShotBehaviour())

    agent.start()

    assert agent.on_start_flag is False
    assert agent.on_end_flag is False

    agent.wait_behaviour.wait()

    assert agent.on_start_flag is True
    assert agent.on_end_flag is True
    agent.stop()


def test_add_behaviour():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.wait_behaviour.set()

    agent = make_connected_agent()
    agent.wait_behaviour = Event()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.has_behaviour(behaviour)

    agent.start()

    assert behaviour.agent == agent
    assert behaviour.template is None
    assert behaviour.presence == agent.presence
    assert behaviour.web == agent.web
    assert behaviour.queue.empty()
    agent.wait_behaviour.wait()
    assert behaviour.done()
    agent.stop()


def test_remove_behaviour():
    class EmptyBehaviour(Behaviour):
        async def run(self):
            pass

    agent = make_connected_agent()
    behaviour = EmptyBehaviour()
    agent.add_behaviour(behaviour)
    assert agent.has_behaviour(behaviour)

    agent.remove_behaviour(behaviour)

    assert not agent.has_behaviour(behaviour)


def test_remove_behaviour_not_added():
    class EmptyBehaviour(Behaviour):
        async def run(self):
            pass

    agent = make_connected_agent()
    behaviour = EmptyBehaviour()

    with pytest.raises(ValueError) as e:
        agent.remove_behaviour(behaviour)


def test_wait_for_agent_start():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def on_start(self):
            self.agent.wait_behaviour.set()

        async def run(self):
            pass

    agent = make_connected_agent()
    agent.wait_behaviour = Event()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert not agent.wait_behaviour.is_set()
    agent.start()
    agent.wait_behaviour.wait()
    agent.stop()


def test_send_message(message):
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            await self.send(message)
            self.agent.wait_behaviour.set()

    agent = make_connected_agent()
    agent.wait_behaviour = Event()
    agent.start()

    agent.aiothread.stream = MagicMock()
    agent.stream.send = CoroutineMock()
    agent.add_behaviour(SendBehaviour())
    agent.wait_behaviour.wait()

    aiomsg = message.prepare()

    assert agent.stream.send.await_count == 1
    msg_arg = agent.stream.send.await_args[0][0]
    assert msg_arg.body[None] == "message body"
    assert msg_arg.to == aioxmpp.JID.fromstr("to@localhost")
    assert msg_arg.thread == "thread-id"

    agent.stop()


def test_oneshot_behaviour():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.one_shot_behaviour_executed = True
            self.agent.wait_behaviour.set()

    agent = make_connected_agent()
    agent.one_shot_behaviour_executed = False
    agent.wait_behaviour = Event()
    agent.add_behaviour(TestOneShotBehaviour())

    assert agent.one_shot_behaviour_executed is False

    agent.start()
    agent.wait_behaviour.wait()

    assert agent.one_shot_behaviour_executed is True
    agent.stop()


def test_cyclic_behaviour():
    class TestCyclicBehaviour(Behaviour):
        async def run(self):
            self.agent.cycles += 1
            if self.agent.cycles > 2:
                self.kill()
                self.agent.wait_behaviour.set()

    agent = make_connected_agent()
    agent.cycles = 0
    agent.wait_behaviour = Event()
    behav = TestCyclicBehaviour()
    agent.start()
    assert agent.cycles == 0

    agent.add_behaviour(behav)
    agent.wait_behaviour.wait()

    assert agent.cycles == 3
    assert behav.is_killed()

    agent.stop()
