import asyncio
import datetime
import time
from threading import Event

import aioxmpp
import pytest
from pytest import fixture
from asynctest import CoroutineMock, MagicMock

from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, TimeoutBehaviour, FSMBehaviour, State, \
    NotValidState, NotValidTransition, BehaviourNotFinishedException
from spade.message import Message
from spade.template import Template
from tests.utils import make_connected_agent

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"


def wait_for_behaviour_is_killed(behaviour, tries=500, sleep=0.01):
    counter = 0
    while not behaviour.is_killed() and counter < tries:
        time.sleep(sleep)
        counter += 1
    if not behaviour.is_killed():
        raise Exception("Behaviour not finished")


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


@fixture
def fsm():
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

    agent = make_connected_agent()
    agent.on_start_flag = False
    agent.on_end_flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.on_start_flag is False
    assert agent.on_end_flag is False

    agent.start(auto_register=False)

    wait_for_behaviour_is_killed(behaviour)

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

    agent = make_connected_agent()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    wait_for_behaviour_is_killed(behaviour)

    assert type(behaviour.exit_code) == ZeroDivisionError
    assert not agent.flag
    agent.stop()


def test_on_run_exception():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            result = 1 / 0
            self.agent.flag = True

    agent = make_connected_agent()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    wait_for_behaviour_is_killed(behaviour)

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

    agent = make_connected_agent()
    agent.flag = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    wait_for_behaviour_is_killed(behaviour)

    assert type(behaviour.exit_code) == ZeroDivisionError
    assert not agent.flag
    agent.stop()


def test_add_behaviour():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.kill()

    agent = make_connected_agent()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.has_behaviour(behaviour)

    agent.start(auto_register=False)

    assert behaviour.agent == agent
    assert behaviour.template is None
    assert behaviour.presence == agent.presence
    assert behaviour.web == agent.web
    assert behaviour.queue.empty()

    wait_for_behaviour_is_killed(behaviour)

    assert behaviour.done()
    agent.stop()


def test_remove_behaviour():
    class EmptyBehaviour(CyclicBehaviour):
        async def run(self):
            pass

    agent = make_connected_agent()
    behaviour = EmptyBehaviour()
    agent.add_behaviour(behaviour)
    assert agent.has_behaviour(behaviour)

    agent.remove_behaviour(behaviour)

    assert not agent.has_behaviour(behaviour)


def test_remove_behaviour_not_added():
    class EmptyBehaviour(CyclicBehaviour):
        async def run(self):
            pass

    agent = make_connected_agent()
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

    agent = make_connected_agent()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    agent.start(auto_register=False)

    wait_for_behaviour_is_killed(behaviour)

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

    agent = make_connected_agent()
    agent.start(auto_register=False)

    agent.aiothread.stream = MagicMock()
    agent.stream.send = CoroutineMock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    wait_for_behaviour_is_killed(behaviour)

    assert agent.stream.send.await_count == 1
    msg_arg = agent.stream.send.await_args[0][0]
    assert msg_arg.body[None] == "message body"
    assert msg_arg.to == aioxmpp.JID.fromstr("to@localhost")
    assert msg_arg.thread == "thread-id"

    agent.stop()


def test_send_message_without_sender():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message()
            await self.send(msg)
            self.kill()

    agent = make_connected_agent()
    agent.start(auto_register=False)

    agent.aiothread.stream = MagicMock()
    agent.stream.send = CoroutineMock()
    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)

    wait_for_behaviour_is_killed(behaviour)

    msg_arg = agent.stream.send.await_args[0][0]
    assert msg_arg.from_ == aioxmpp.JID.fromstr("fake@jid")

    agent.stop()


def test_receive():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(body="received body")
            await asyncio.wait_for(self.queue.put(msg), 5.0)
            self.agent.recv_msg = await self.receive()
            self.kill()

    agent = make_connected_agent()

    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour)
    assert behaviour.mailbox_size() == 0

    agent.start(auto_register=False)
    assert agent.is_alive()
    assert agent.has_behaviour(behaviour)

    wait_for_behaviour_is_killed(behaviour)

    assert agent.recv_msg.body == "received body"

    agent.stop()


def test_receive_with_timeout():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive(5.0)
            self.kill()

    agent = make_connected_agent()

    msg = Message(body="received body")
    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)
    assert behaviour.mailbox_size() == 0

    agent.start(auto_register=False)
    agent._message_received(msg.prepare())
    assert agent.is_alive()
    assert agent.has_behaviour(behaviour)

    wait_for_behaviour_is_killed(behaviour)

    assert agent.recv_msg.body == "received body"
    assert agent.recv_msg == msg

    agent.stop()


def test_receive_with_timeout_error():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive(0.01)
            self.kill()

    agent = make_connected_agent()

    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)

    agent.start(auto_register=False)
    wait_for_behaviour_is_killed(behaviour)

    assert behaviour.mailbox_size() == 0
    assert agent.recv_msg is None
    agent.stop()


def test_receive_with_empty_queue():
    class RecvBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.recv_msg = await self.receive()
            self.kill()

    agent = make_connected_agent()

    template = Template(body="received body")
    behaviour = RecvBehaviour()
    agent.add_behaviour(behaviour, template)

    agent.start(auto_register=False)
    wait_for_behaviour_is_killed(behaviour)

    assert behaviour.mailbox_size() == 0
    assert agent.recv_msg is None
    agent.stop()


def test_set_get():
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            self.set("key", "value")
            assert self.get("key") == "value"
            self.kill()

    agent = make_connected_agent()
    agent.start(auto_register=False)

    behaviour = SendBehaviour()
    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

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

    agent = make_connected_agent()

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

    agent.start(auto_register=False)
    agent._message_received(msg1)
    agent._message_received(msg2)
    agent._message_received(msg3)

    wait_for_behaviour_is_killed(behaviour)

    assert agent.msg1.get_metadata("performative") == "template1"
    assert agent.msg2.get_metadata("performative") == "template2"
    assert agent.msg3.get_metadata("performative") == "template3"
    agent.stop()


def test_kill_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.kill()

    agent = make_connected_agent()
    behaviour = TestCyclicBehaviour()
    agent.start(auto_register=False)

    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

    assert behaviour.is_killed()
    assert behaviour.exit_code == 0

    agent.stop()


def test_exit_code_from_kill_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.kill(42)

    agent = make_connected_agent()
    behaviour = TestCyclicBehaviour()
    agent.start(auto_register=False)

    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

    assert behaviour.is_killed()
    assert behaviour.exit_code == 42

    agent.stop()


def test_set_exit_code_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.exit_code = 1024
            agent.event.wait()
            self.kill()

    agent = make_connected_agent()
    behaviour = TestCyclicBehaviour()
    agent.event = Event()
    agent.start(auto_register=False)

    agent.add_behaviour(behaviour)

    with pytest.raises(BehaviourNotFinishedException):
        assert behaviour.exit_code

    agent.event.set()
    wait_for_behaviour_is_killed(behaviour)

    agent.stop()

    assert behaviour.exit_code == 1024

    assert not agent.is_alive()


def test_notfinishedexception_behaviour():
    class TestBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.event.wait()

    agent = make_connected_agent()
    agent.event = Event()
    behaviour = TestBehaviour()
    agent.start(auto_register=False)

    agent.add_behaviour(behaviour)

    with pytest.raises(BehaviourNotFinishedException):
        assert behaviour.exit_code

    agent.event.set()

    assert behaviour.exit_code == 0

    agent.stop()

    assert not agent.is_alive()


def test_cyclic_behaviour():
    class TestCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            self.agent.cycles += 1
            if self.agent.cycles > 2:
                self.kill()

    agent = make_connected_agent()
    agent.cycles = 0
    behaviour = TestCyclicBehaviour()
    agent.start(auto_register=False)
    assert agent.cycles == 0

    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

    assert agent.cycles == 3
    assert behaviour.is_killed()

    agent.stop()


def test_oneshot_behaviour():
    class TestOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.agent.one_shot_behaviour_executed = True
            self.kill()

    agent = make_connected_agent()
    agent.one_shot_behaviour_executed = False
    behaviour = TestOneShotBehaviour()
    agent.add_behaviour(behaviour)

    assert agent.one_shot_behaviour_executed is False

    agent.start(auto_register=False)
    wait_for_behaviour_is_killed(behaviour)

    assert agent.one_shot_behaviour_executed is True
    agent.stop()


def test_periodic_behaviour():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.periodic_behaviour_execution_counter += 1
            self.kill()

    agent = make_connected_agent()
    agent.periodic_behaviour_execution_counter = 0
    behaviour = TestPeriodicBehaviour(0.01)
    agent.add_behaviour(behaviour)

    assert agent.periodic_behaviour_execution_counter == 0

    agent.start(auto_register=False)
    wait_for_behaviour_is_killed(behaviour)

    assert agent.periodic_behaviour_execution_counter == 1
    agent.stop()


def test_periodic_behaviour_period_zero():
    class TestPeriodicBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.periodic_behaviour_execution_counter += 1
            self.kill()

    agent = make_connected_agent()
    agent.periodic_behaviour_execution_counter = 0
    behaviour = TestPeriodicBehaviour(0)
    agent.add_behaviour(behaviour)

    assert agent.periodic_behaviour_execution_counter == 0

    agent.start(auto_register=False)
    wait_for_behaviour_is_killed(behaviour)

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

    agent = make_connected_agent()
    agent.start(auto_register=False)

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0.01)
    behaviour = TestPeriodicBehaviour(period=0.01, start_at=start_at)

    assert behaviour._next_activation == start_at

    agent.add_behaviour(behaviour)

    wait_for_behaviour_is_killed(behaviour)

    assert agent.delay >= start_at

    agent.stop()


def test_timeout_behaviour():
    class TestTimeoutBehaviour(TimeoutBehaviour):
        async def run(self):
            self.agent.delay = datetime.datetime.now()
            self.kill()

    agent = make_connected_agent()
    agent.start(auto_register=False)

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0.01)
    behaviour = TestTimeoutBehaviour(start_at=start_at)

    assert behaviour._timeout == start_at
    assert not behaviour._timeout_triggered

    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

    assert agent.delay >= start_at
    assert behaviour._timeout_triggered
    assert behaviour.done()

    agent.stop()


def test_timeout_behaviour_zero():
    class TestTimeoutBehaviour(TimeoutBehaviour):
        async def run(self):
            self.agent.delay = datetime.datetime.now()
            self.kill()

    agent = make_connected_agent()
    agent.start(auto_register=False)

    start_at = datetime.datetime.now() + datetime.timedelta(seconds=0)
    behaviour = TestTimeoutBehaviour(start_at=start_at)

    assert behaviour._timeout == start_at

    assert not behaviour._timeout_triggered

    agent.add_behaviour(behaviour)
    wait_for_behaviour_is_killed(behaviour)

    assert agent.delay >= start_at
    assert behaviour._timeout_triggered
    assert behaviour.done()

    agent.stop()


def test_fsm_behaviour(fsm):
    agent = make_connected_agent()
    agent.sync1_behaviour = asyncio.Event()
    agent.sync2_behaviour = asyncio.Event()
    agent.start(auto_register=False)

    assert len(fsm._transitions) == 2
    assert fsm.current_state == STATE_ONE

    agent.add_behaviour(fsm)
    wait_for_behaviour_is_killed(fsm.state_one)
    assert fsm.current_state == STATE_ONE
    assert agent.state == STATE_ONE
    agent.loop.call_soon_threadsafe(agent.sync1_behaviour.set)

    wait_for_behaviour_is_killed(fsm.state_two)
    assert fsm.current_state == STATE_TWO
    assert agent.state == STATE_TWO
    agent.loop.call_soon_threadsafe(agent.sync2_behaviour.set)

    wait_for_behaviour_is_killed(fsm.state_three)
    assert fsm.current_state == STATE_THREE
    assert agent.state == STATE_THREE

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

    agent = make_connected_agent()
    agent.start(auto_register=False)

    assert fsm_.current_state == STATE_ONE

    agent.add_behaviour(fsm_)

    wait_for_behaviour_is_killed(state_one)
    assert fsm_.current_state == STATE_ONE

    wait_for_behaviour_is_killed(fsm_)
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

    agent = make_connected_agent()
    agent.start(auto_register=False)

    assert fsm_.current_state == STATE_ONE

    agent.add_behaviour(fsm_)

    wait_for_behaviour_is_killed(state_one)
    assert fsm_.current_state == STATE_ONE

    wait_for_behaviour_is_killed(fsm_)
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


def test_to_graphviz(fsm):
    assert fsm.to_graphviz() == "digraph finite_state_machine { rankdir=LR; node [fixedsize=true];STATE_ONE -> STATE_TWO;STATE_TWO -> STATE_THREE;}"
