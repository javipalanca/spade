import asyncio

import aioxmpp
from aioxmpp import PresenceManagedClient, Message
from asynctest import CoroutineMock, Mock

from spade.agent import Agent
from tests.utils import make_connected_agent
from testfixtures import LogCapture

def test_create_agent(mocker):
    mocker.patch("spade.agent.AioThread.connect")
    agent = Agent("jid@server", "fake_password")

    assert agent.is_alive() is False

    agent.start()

    assert agent.is_alive() is True

    agent.aiothread.connect.assert_called_once()
    assert agent.stream is None

    agent.aiothread.conn_coro = mocker.Mock()
    agent.aiothread.conn_coro.__aexit__ = CoroutineMock()

    agent.stop()

    agent.aiothread.conn_coro.__aexit__.assert_called_once()

    assert agent.is_alive() is False


def test_connected_agent():
    agent = make_connected_agent()
    assert agent.is_alive() is False

    agent.start()
    assert agent.is_alive() is True

    agent.stop()
    assert agent.is_alive() is False


def test_connected_agent_with_loop():
    loop = asyncio.new_event_loop()
    agent = make_connected_agent(loop=loop)
    assert agent.is_alive() is False

    agent.start()
    assert agent.is_alive() is True

    agent.stop()
    assert agent.is_alive() is False


def test_name():
    agent = make_connected_agent(jid="john@fake_server")
    assert agent.name == "john"


def test_avatar():
    agent = make_connected_agent(jid="test_avatar@fake_server")
    assert agent.avatar == "http://www.gravatar.com/avatar/44bdc5585ef57844edb11c5b9711d2e6?d=monsterid"


def test_setup():
    agent = make_connected_agent()
    agent.setup = Mock()
    agent.start()
    agent.setup.assert_called_once()
    agent.stop()


def test_set_get():
    agent = make_connected_agent()
    agent.set("KB_name", "KB_value")
    assert agent.get("KB_name") == "KB_value"


def test_get__none():
    agent = make_connected_agent()
    assert agent.get("KB_name_unknown") is None


def test_client():
    agent = make_connected_agent()
    assert type(agent.client) == PresenceManagedClient


def test_register():
    agent = make_connected_agent()
    agent.register = Mock()

    agent.start(auto_register=True)

    assert len(agent.register.mock_calls) == 1

    agent.stop()


def test_receive_without_behaviours():

    agent = make_connected_agent()
    msg = Message(type_=aioxmpp.MessageType.CHAT)

    assert agent.traces.len() == 0
    agent.start()

    with LogCapture() as log:
        agent._message_received(msg)
        log.check_present(('spade.Agent', 'WARNING', f"No behaviour matched for message: {msg}"))

    assert agent.traces.len() == 1
    assert msg in agent.traces.store[0]

    agent.stop()
