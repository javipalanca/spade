import asyncio
import datetime
from threading import Event

import aioxmpp
import pytest
from asynctest import CoroutineMock, MagicMock, Mock

from spade.agent import Agent
from spade.behaviour import (
    OneShotBehaviour,
    CyclicBehaviour,
    PeriodicBehaviour,
    TimeoutBehaviour,
    FSMBehaviour,
    State,
    NotValidState,
    NotValidTransition,
    BehaviourNotFinishedException,
)
from spade.message import Message, SPADE_X_METADATA
from spade.template import Template
from .conftest import wait_for_behaviour_is_killed
from .factories import MockedAgentFactory

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"


class StateOne(State):
    async def run(self):
        self.agent.state = STATE_ONE
        self.set_next_state(STATE_TWO)
        self.kill()
        await self.agent.sync1_behaviour.wait()


class StateTwo(State):
    async def run(self):
        self.agent.state = STATE_TWO
        self.set_next_state(STATE_THREE)
        self.kill()
        await self.agent.sync2_behaviour.wait()


class StateThree(State):
    async def run(self):
        self.agent.state = STATE_THREE
        self.kill()


@pytest.fixture
def fsm():
    fsm_ = FSMBehaviour()
    state_one = StateOne()
    state_two = StateTwo()
    state_three = StateThree()
    fsm_.add_state(STATE_ONE, state_one, initial=True)
    fsm_.add_state(STATE_TWO, state_two)
    fsm_.add_state(STATE_THREE, state_three)
    fsm_.add_transition(STATE_ONE, STATE_TWO)
    fsm_.add_transition(STATE_TWO, STATE_THREE)

    fsm_.state_one = state_one
    fsm_.state_two = state_two
    fsm_.state_three = state_three

    return fsm_


def test_on_start_on_end():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def on_start(self):
            self.agent.on_start_flag = True

        async def run(self):
            pass

        async def on_end(self):
            self.agent.on_end_flag = True
            self.kill()

    agent = MockedAgentFactory()
    agent.on_start_flag = False
    agent.on_end_flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.on_start_flag is False
    assert agent.on_end_flag is False

    agent.start(auto_register=False)

    behaviour.join()

    assert agent.on_start_flag is True
    assert agent.on_end_flag is True
    agent.stop()


def test_on_start_exception():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def on_start(self):
            result = 1 / 0
            self.agent.flag = True

        async def run(self):
            pass

    agent = MockedAgentFactory()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    behaviour.join()

    assert type(behaviour.exit_code) == ZeroDivisionError
    assert not agent.flag
    agent.stop()


def test_on_run_exception():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            result = 1 / 0
            self.agent.flag = True

    agent = MockedAgentFactory()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    behaviour.join()

    assert type(behaviour.exit_code) == ZeroDivisionError
    assert not agent.flag
    agent.stop()


def test_on_end_exception():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            pass

        async def on_end(self):
            result = 1 / 0
            self.agent.flag = True

    agent = MockedAgentFactory()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    behaviour.join()

    assert type(behaviour.exit_code) == ZeroDivisionError
    assert not agent.flag
    agent.stop()


def test_add_behaviour():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.kill()

    agent = MockedAgentFactory()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.has_behaviour(behaviour)

    future = agent.start(auto_register=False)
    future.result()

    assert behaviour.agent == agent
    assert behaviour.template is None
    assert behaviour.presence == agent.presence
    assert behaviour.web == agent.web
    assert behaviour.queue.empty()

    behaviour.join()

    assert behaviour.is_done()
    agent.stop()


def test_remove_behaviour():
    class EmptyBehaviour(CyclicBehaviour):
        async def run(self):
            pass

    agent = MockedAgentFactory()
    behaviour = EmptyBehaviour()
    agent.add_behaviour(behaviour)
    assert agent.has_behaviour(behaviour)

    agent.remove_behaviour(behaviour)

    assert not agent.has_behaviour(behaviour)


def test_remove_behaviour_not_added():
    class EmptyBehaviour(CyclicBehaviour):
        async def run(self):
            pass

    agent = MockedAgentFactory()
    behaviour = EmptyBehaviour()

    with pytest.raises(ValueError):
        agent.remove_behaviour(behaviour)


def test_wait_for_agent_start():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def on_start(self):
            self.agent.started = True
            self.kill()

        async def run(self):
            pass

    agent = MockedAgentFactory()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    behaviour.join()

    assert agent.started

    agent.stop()


def test_behaviour_match():
    class TestBehaviour(OneShotBehaviour):
        async def run(self):
            pass

    template = Template()
    template.sender = "sender1@host"
    template.to = "recv1@host"
    template.body = "Hello World"
    template.thread = "thread-id"
    template.metadata = {"performative": "query"}

    behaviour = TestBehaviour()
    behaviour.set_template(template)

    msg = Message()
    msg.sender = "sender1@host"
    msg.to = "recv1@host"
    msg.body = "Hello World"
    msg.thread = "thread-id"
    msg.set_metadata("performative", "query")

    assert behaviour.match(msg)


def test_behaviour_match_without_template():
    class TestBehaviour(OneShotBehaviour):
        async def run(self):
            pass

    behaviour = TestBehaviour()

    msg = Message()
    msg.sender = "sender1@host"
    msg.to = "recv1@host"
    msg.body = "Hello World"
    msg.thread = "thread-id"
    msg.set_metadata("performative", "query")

    assert behaviour.match(msg)


def test_send_message(message):
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            await self.send(message)
            self.kill()

    agent = MockedAgentFactory(jid="sender@localhost")
    future = agent.start(auto_register=False)
    future.result()

    agent2 = MockedAgentFactory(jid="to@localhost")
    future = agent2.start(auto_register=False)
    future.result()

    agent2.dispatch = Mock()

    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    behaviour.join()

    assert agent2.dispatch.assert_called
    msg_arg = agent2.dispatch.call_args[0][0]
    assert msg_arg.body == "message body"
    assert msg_arg.to == aioxmpp.JID.fromstr("to@localhost")
    assert msg_arg.thread == "thread-id"

    agent.stop()
    agent2.stop()


def test_send_message_to_external_agent():
    message = Message(
        to="to@external_xmpp.com",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={"metadata1": "value1", "metadata2": "value2"},
    )

    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            await self.send(message)
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    agent.client = MagicMock()
    agent.client.send = CoroutineMock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    behaviour.join()

    assert agent.client.send.await_count == 1
    msg_arg = agent.client.send.await_args[0][0]
    assert msg_arg.body[None] == "message body"
    assert msg_arg.to == aioxmpp.JID.fromstr("to@external_xmpp.com")
    thread_found = False
    for data in msg_arg.xep0004_data:
        if data.title == SPADE_X_METADATA:
            for field in data.fields:
                if field.var == "_thread_node":
                    assert field.values[0] == "thread-id"
                    thread_found = True
    assert thread_found

    agent.stop()


def test_send_message_without_sender():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message()
            await self.send(msg)
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    agent.client = MagicMock()
    agent.client.send = CoroutineMock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    behaviour.join()

    msg_arg = agent.client.send.await_args[0][0]
    assert msg_arg.from_ == aioxmpp.JID.fromstr("fake@jid")

    agent.stop()


def test_receive():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(body="received body")
            await asyncio.wait_for(self.queue.put(msg), 5.0)
            self.agent.recv_msg = await self.receive()
            self.kill()

    agent = MockedAgentFactory()

    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour)
    assert behaviour.mailbox_size() == 0

    future = agent.start(auto_register=False)
    future.result()
    assert agent.is_alive()

    behaviour.join()

    assert agent.recv_msg.body == "received body"

    agent.stop()


def test_receive_with_timeout():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive(5.0)
            self.kill()

    agent = MockedAgentFactory()

    msg = Message(body="received body")
    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)
    assert behaviour.mailbox_size() == 0

    future = agent.start(auto_register=False)
    future.result()
    agent._message_received(msg.prepare())
    assert agent.is_alive()
    assert agent.has_behaviour(behaviour)

    behaviour.join()

    assert agent.recv_msg.body == "received body"
    assert agent.recv_msg == msg

    agent.stop()


def test_receive_with_timeout_error():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive(0.01)
            self.kill()

    agent = MockedAgentFactory()

    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)

    future = agent.start(auto_register=False)
    future.result()
    behaviour.join()

    assert behaviour.mailbox_size() == 0
    assert agent.recv_msg is None
    agent.stop()


def test_receive_with_empty_queue():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive()
            self.kill()

    agent = MockedAgentFactory()

    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)

    future = agent.start(auto_register=False)
    future.result()
    behaviour.join()

    assert behaviour.mailbox_size() == 0
    assert agent.recv_msg is None
    agent.stop()


def test_set_get():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            self.set("key", "value")
            assert self.get("key") == "value"
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert agent.get("key") == "value"

    agent.stop()


def test_multiple_templates():
    class Template1Behaviour(OneShotBehaviour):
        async def run(self):
            self.agent.msg1 = await self.receive(timeout=2)

    class Template2Behaviour(OneShotBehaviour):
        async def run(self):
            self.agent.msg2 = await self.receive(timeout=2)

    class Template3Behaviour(OneShotBehaviour):
        async def run(self):
            self.agent.msg3 = await self.receive(timeout=2)
            self.kill()

    agent = MockedAgentFactory()

    template1 = Template()
    template1.set_metadata("performative", "template1")
    agent.add_behaviour(Template1Behaviour(), template1)

    template2 = Template()
    template2.set_metadata("performative", "template2")
    agent.add_behaviour(Template2Behaviour(), template2)

    template3 = Template()
    template3.set_metadata("performative", "template3")
    behaviour = Template3Behaviour()
    agent.add_behaviour(behaviour, template3)

    msg1 = Message(metadata={"performative": "template1"}).prepare()
    msg2 = Message(metadata={"performative": "template2"}).prepare()
    msg3 = Message(metadata={"performative": "template3"}).prepare()

    future = agent.start(auto_register=False)
    future.result()
    agent._message_received(msg1)
    agent._message_received(msg2)
    agent._message_received(msg3)

    behaviour.join()

    assert agent.msg1.get_metadata("performative") == "template1"
    assert agent.msg2.get_metadata("performative") == "template2"
    assert agent.msg3.get_metadata("performative") == "template3"
    agent.stop()


def test_kill_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.kill()

    agent = MockedAgentFactory()
    behaviour = TestCyclicBehaviour()
    agent.start(auto_register=False)

    agent.add_behaviour(behaviour)
    behaviour.join()

    assert behaviour.is_killed()
    assert behaviour.exit_code == 0

    agent.stop()


def test_exit_code_from_kill_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.kill(42)

    agent = MockedAgentFactory()
    behaviour = TestCyclicBehaviour()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(behaviour)
    behaviour.join()

    assert behaviour.is_killed()
    assert behaviour.exit_code == 42

    agent.stop()


def test_set_exit_code_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.exit_code = 1024
            agent.event.wait()
            self.kill()

    agent = MockedAgentFactory()
    behaviour = TestCyclicBehaviour()
    agent.event = Event()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(behaviour)

    with pytest.raises(BehaviourNotFinishedException):
        assert behaviour.exit_code

    agent.event.set()
    behaviour.join()

    future = agent.stop()
    future.result()

    assert behaviour.exit_code == 1024

    assert not agent.is_alive()


def test_notfinishedexception_behaviour():
    class TestBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.event.wait()

    agent = MockedAgentFactory()
    agent.event = Event()
    behaviour = TestBehaviour()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(behaviour)

    with pytest.raises(BehaviourNotFinishedException):
        assert behaviour.exit_code

    agent.event.set()

    assert behaviour.exit_code == 0

    future = agent.stop()
    future.result()

    assert not agent.is_alive()


def test_cyclic_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.agent.cycles += 1
            if self.agent.cycles > 2:
                self.kill()

    agent = MockedAgentFactory()
    agent.cycles = 0
    behaviour = TestCyclicBehaviour()
    future = agent.start(auto_register=False)
    future.result()

    assert agent.cycles == 0

    agent.add_behaviour(behaviour)
    behaviour.join()

    assert agent.cycles == 3
    assert behaviour.is_killed()

    agent.stop()


def test_oneshot_behaviour():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.one_shot_behaviour_executed = True
            self.kill()

    agent = MockedAgentFactory()
    agent.one_shot_behaviour_executed = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.one_shot_behaviour_executed is False

    future = agent.start(auto_register=False)
    future.result()
    behaviour.join()

    assert agent.one_shot_behaviour_executed is True
    agent.stop()


def test_periodic_behaviour():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.periodic_behaviour_execution_counter += 1
            self.kill()

    agent = MockedAgentFactory()
    agent.periodic_behaviour_execution_counter = 0
    behaviour = TestPeriodicBehaviour(0.01)
    agent.add_behaviour(behaviour)

    assert agent.periodic_behaviour_execution_counter == 0

    future = agent.start(auto_register=False)
    future.result()
    behaviour.join()

    assert agent.periodic_behaviour_execution_counter == 1
    agent.stop()


def test_periodic_behaviour_period_zero():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.periodic_behaviour_execution_counter += 1
            self.kill()

    agent = MockedAgentFactory()
    agent.periodic_behaviour_execution_counter = 0
    behaviour = TestPeriodicBehaviour(0)
    agent.add_behaviour(behaviour)

    assert agent.periodic_behaviour_execution_counter == 0

    future = agent.start(auto_register=False)
    future.result()
    behaviour.join()

    assert agent.periodic_behaviour_execution_counter == 1
    agent.stop()


def test_periodic_behaviour_negative_period():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            pass

    with pytest.raises(ValueError):
        TestPeriodicBehaviour(-1)


def test_set_period():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            pass

    behaviour = TestPeriodicBehaviour(1)
    assert behaviour.period == datetime.timedelta(seconds=1)

    behaviour.period = 2
    assert behaviour.period == datetime.timedelta(seconds=2)


def test_periodic_start_at():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.delay = datetime.datetime.now()
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0.01)
    behaviour = TestPeriodicBehaviour(period=0.01, start_at=start_at)

    assert behaviour._next_activation == start_at

    agent.add_behaviour(behaviour)

    behaviour.join()

    assert agent.delay >= start_at

    agent.stop()


def test_timeout_behaviour():
    class TestTimeoutBehaviour(TimeoutBehaviour):
        async def run(self):
            self.agent.delay = datetime.datetime.now()
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0.01)
    behaviour = TestTimeoutBehaviour(start_at=start_at)

    assert behaviour._timeout == start_at
    assert not behaviour._timeout_triggered

    agent.add_behaviour(behaviour)
    behaviour.join()

    assert agent.delay >= start_at
    assert behaviour._timeout_triggered
    assert behaviour.is_done()

    agent.stop()


def test_timeout_behaviour_zero():
    class TestTimeoutBehaviour(TimeoutBehaviour):
        async def run(self):
            self.agent.delay = datetime.datetime.now()
            self.kill()

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0)
    behaviour = TestTimeoutBehaviour(start_at=start_at)

    assert behaviour._timeout == start_at

    assert not behaviour._timeout_triggered

    agent.add_behaviour(behaviour)
    behaviour.join()

    assert agent.delay >= start_at
    assert behaviour._timeout_triggered
    assert behaviour.is_done()

    agent.stop()


def test_fsm_behaviour(fsm):
    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()
    agent.sync1_behaviour = asyncio.Event(loop=agent.loop)
    agent.sync2_behaviour = asyncio.Event(loop=agent.loop)

    agent.state = None

    assert len(fsm._transitions) == 2
    assert fsm.current_state == STATE_ONE

    agent.add_behaviour(fsm)
    assert fsm.current_state == STATE_ONE
    assert not fsm.state_one.is_done()
    wait_for_behaviour_is_killed(fsm.state_one)
    assert agent.state == STATE_ONE
    agent.loop.call_soon_threadsafe(agent.sync1_behaviour.set)
    fsm.state_one.join()

    assert fsm.current_state == STATE_TWO
    assert not fsm.state_two.is_done()
    wait_for_behaviour_is_killed(fsm.state_two)
    assert agent.state == STATE_TWO
    agent.loop.call_soon_threadsafe(agent.sync2_behaviour.set)
    fsm.state_two.join()

    assert fsm.current_state == STATE_THREE
    wait_for_behaviour_is_killed(fsm.state_three)
    assert agent.state == STATE_THREE
    fsm.state_three.join()

    agent.stop()


def test_fsm_add_bad_state(fsm):
    with pytest.raises(AttributeError):
        fsm.add_state("BAD_STATE", object())


def test_fsm_is_valid_transition(fsm):
    fsm.is_valid_transition(STATE_ONE, STATE_TWO)


def test_fsm_not_valid_transition(fsm):
    with pytest.raises(NotValidTransition):
        fsm.is_valid_transition(STATE_ONE, STATE_THREE)


def test_fsm_not_valid_state(fsm):
    with pytest.raises(NotValidState):
        fsm.is_valid_transition(STATE_ONE, "BAD_STATE")

    with pytest.raises(NotValidState):
        fsm.is_valid_transition("BAD_STATE", STATE_TWO)


def test_fsm_bad_state():
    class StateOne(State):
        async def run(self):
            self.set_next_state("BAD_STATE")
            self.kill()

    class StateTwo(State):
        async def run(self):
            pass

    class BadFSMBehaviour(FSMBehaviour):
        async def on_end(self):
            self.kill()

    fsm_ = BadFSMBehaviour()
    state_one = StateOne()
    state_two = StateTwo()
    fsm_.add_state(STATE_ONE, state_one, initial=True)
    fsm_.add_state(STATE_TWO, state_two)
    fsm_.add_transition(STATE_ONE, STATE_TWO)

    agent = MockedAgentFactory()
    agent.start(auto_register=False)

    assert fsm_.current_state == STATE_ONE

    agent.add_behaviour(fsm_)

    state_one.join()
    assert fsm_.current_state == STATE_ONE

    fsm_.join()
    assert fsm_.is_killed()

    agent.stop()


def test_fsm_bad_transition():
    class StateOne(State):
        async def run(self):
            self.set_next_state(STATE_THREE)
            self.kill()

    class StateTwo(State):
        async def run(self):
            pass

    class StateThree(State):
        async def run(self):
            pass

    class BadFSMBehaviour(FSMBehaviour):
        async def on_end(self):
            self.kill()

    fsm_ = BadFSMBehaviour()
    state_one = StateOne()
    state_two = StateTwo()
    state_three = StateThree()
    fsm_.add_state(STATE_ONE, state_one, initial=True)
    fsm_.add_state(STATE_TWO, state_two)
    fsm_.add_state(STATE_THREE, state_three)
    fsm_.add_transition(STATE_ONE, STATE_TWO)
    fsm_.add_transition(STATE_TWO, STATE_THREE)

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    assert fsm_.current_state == STATE_ONE

    agent.add_behaviour(fsm_)

    state_one.join()
    assert fsm_.current_state == STATE_ONE

    fsm_.join()
    assert fsm_.is_killed()

    agent.stop()


def test_fsm_two_initials():
    class StateOne(State):
        async def run(self):
            self.set_next_state(STATE_THREE)
            self.kill()

    class StateTwo(State):
        async def run(self):
            pass

    class TestFSMBehaviour(FSMBehaviour):
        async def on_end(self):
            self.kill()

    fsm_ = TestFSMBehaviour()
    state_one = StateOne()
    state_two = StateTwo()
    fsm_.add_state(STATE_ONE, state_one, initial=True)
    fsm_.add_state(STATE_TWO, state_two, initial=True)

    assert fsm_.current_state == STATE_TWO


def test_fsm_fail_on_start():
    class StateOne(State):
        async def on_start(self):
            raise Exception

        async def run(self):
            pass

    fsm_ = FSMBehaviour()
    state_one = StateOne()
    fsm_.add_state(STATE_ONE, state_one, initial=True)

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(fsm_)

    fsm_.join()

    assert fsm_.is_killed()

    assert type(fsm_.exit_code) == Exception

    agent.stop()


def test_fsm_fail_on_run():
    class StateOne(State):
        async def run(self):
            raise Exception

    fsm_ = FSMBehaviour()
    state_one = StateOne()
    fsm_.add_state(STATE_ONE, state_one, initial=True)

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(fsm_)

    fsm_.join()

    assert fsm_.is_killed()

    assert type(fsm_.exit_code) == Exception

    agent.stop()


def test_fsm_fail_on_end():
    class StateOne(State):
        async def run(self):
            pass

        async def on_end(self):
            raise Exception

    fsm_ = FSMBehaviour()
    state_one = StateOne()
    fsm_.add_state(STATE_ONE, state_one, initial=True)

    agent = MockedAgentFactory()
    future = agent.start(auto_register=False)
    future.result()

    agent.add_behaviour(fsm_)

    fsm_.join()

    assert fsm_.is_killed()

    assert type(fsm_.exit_code) == Exception

    agent.stop()


def test_to_graphviz(fsm):
    assert (
            fsm.to_graphviz()
            == "digraph finite_state_machine { rankdir=LR; node [fixedsize=true];STATE_ONE -> STATE_TWO;STATE_TWO -> STATE_THREE;}"
    )


def test_join():
    class WaitBehav(OneShotBehaviour):
        async def run(self):
            for i in range(100):
                self.agent.i = i
                await asyncio.sleep(0)

    agent = MockedAgentFactory()
    agent.i = None
    behaviour = WaitBehav()

    agent.add_behaviour(behaviour)
    agent.start(auto_register=False)

    behaviour.join(timeout=None)

    assert behaviour.is_done()
    assert agent.i == 99

    agent.stop()


def test_join_with_timeout():
    class WaitBehav(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(100)

    agent = MockedAgentFactory()
    agent.i = None
    behaviour = WaitBehav()

    agent.add_behaviour(behaviour)
    agent.start(auto_register=False)

    with pytest.raises(TimeoutError):
        behaviour.join(timeout=0.01)

    assert not behaviour.is_done()

    agent.stop()


def test_join_with_long_timeout():
    class WaitBehav(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(0)

    agent = MockedAgentFactory()
    agent.i = None
    behaviour = WaitBehav()

    agent.add_behaviour(behaviour)
    agent.start(auto_register=False)

    behaviour.join(timeout=100)

    assert behaviour.is_done()

    agent.stop()


def test_join_inside_behaviour():
    class Behav1(OneShotBehaviour):
        async def run(self):
            class Behav2(OneShotBehaviour):
                async def run(self):
                    self.agent.behav2 = True

            behav2 = Behav2()
            self.agent.add_behaviour(behav2)
            await behav2.join()
            self.agent.behav1 = True

    agent = MockedAgentFactory()
    agent.behav1 = False
    agent.behav2 = False

    behav1 = Behav1()
    agent.add_behaviour(behav1)

    future = agent.start(auto_register=False)
    future.result()

    behav1.join()

    assert agent.behav1
    assert agent.behav2

    agent.stop()


def test_join_inside_behaviour_with_timeout():
    class Behav1(OneShotBehaviour):
        async def run(self):
            class Behav2(OneShotBehaviour):
                async def run(self):
                    await asyncio.sleep(1)

            behav2 = Behav2()
            self.agent.add_behaviour(behav2)
            with pytest.raises(TimeoutError):
                await behav2.join(timeout=0.001)
            self.agent.behav1 = True

    agent = MockedAgentFactory()
    agent.behav1 = False

    behav1 = Behav1()
    agent.add_behaviour(behav1)

    future = agent.start(auto_register=False)
    future.result()

    behav1.join()

    assert agent.behav1

    agent.stop()


def test_behaviour_at_end():
    class FinalBehav(OneShotBehaviour):
        async def run(self):
            self.agent.value = 2000

    class StopAgent(Agent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._async_connect = CoroutineMock()
            self._async_register = CoroutineMock()
            self.conn_coro = Mock()
            self.conn_coro.__aexit__ = CoroutineMock()
            self.stream = Mock()
            self.value = 1000

        def stop(self):
            behav = FinalBehav()
            self.add_behaviour(behav)
            behav.join()
            return super().stop()

    agent = StopAgent("fakejid@fakeserver", "fakepassword")

    future = agent.start(auto_register=False)
    future.result()

    assert agent.value == 1000
    future = agent.stop()
    future.result()
    assert agent.value == 2000


def test_two_behaviours_at_end():
    class FinalBehav2(OneShotBehaviour):
        async def run(self):
            self.agent.value = 2000

    class FinalBehav1(OneShotBehaviour):
        async def run(self):
            behav = FinalBehav2()
            self.agent.add_behaviour(behav)
            await behav.join()

    class StopAgent(Agent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._async_connect = CoroutineMock()
            self._async_register = CoroutineMock()
            self.conn_coro = Mock()
            self.conn_coro.__aexit__ = CoroutineMock()
            self.stream = Mock()
            self.value = 1000

        def stop(self):
            behav = FinalBehav1()
            self.add_behaviour(behav)
            behav.join()
            return super().stop()

    agent = StopAgent("fakejid@fakeserver", "fakepassword")

    future = agent.start(auto_register=False)
    future.result()

    assert agent.value == 1000
    future = agent.stop()
    future.result()
    assert agent.value == 2000


def test_get_state(fsm):
    assert isinstance(fsm.get_state(STATE_ONE), StateOne)
    assert isinstance(fsm.get_state(STATE_TWO), StateTwo)
    assert isinstance(fsm.get_state(STATE_THREE), StateThree)
