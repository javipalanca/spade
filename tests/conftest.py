import asyncio
import os
import threading
import time

import loguru
import pytest
import pytest_asyncio
from loguru import logger
from slixmpp import JID, Iq

from spade.message import Message
from pyjabber.server import Server

pytest_plugins = "pytest_asyncio"


@pytest.fixture
def jid():
    return JID("friend@localhost/home")


@pytest.fixture
def message():
    return Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={"metadata1": "value1", "metadata2": "value2"},
    )


@pytest.fixture
def message2():
    return Message(
        to="to2@localhost",
        sender="sender2@localhost",
        body="message body",
        thread="thread-id",
    )


@pytest.fixture
def iq():
    iq = Iq()
    iq["type"] = "result"
    iq["id"] = "123"
    iq["to"] = "friend@localhost/home"
    iq["from"] = "localhost"
    # set namespace to roster
    iq["roster"]["xmlns"] = "jabber:iq:roster"
    iq["type"] = "result"
    iq["roster"]["items"] = {
        "friend@localhost": {
            "name": "My Friend",
            "subscription": "both",
            "groups": ["Friends"],
        },
        "friend2@localhost": {
            "name": "User Two",
            "subscription": "to",
            "groups": ["Work"],
        },
    }
    return iq


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    pass

#
@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
#
# @pytest.fixture
# def thread_loop():
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="function", autouse=False)
def server(event_loop):
    # async def run(loop):
    #     time.sleep(100)
    #     asyncio.set_event_loop(loop)
    #     asyncio.run(run_server_loop(loop))
    #
    # async def run_server_loop(loop):
    #     # asyncio.set_event_loop(loop)
    #     # server = Server(database_in_memory=True)
    #     # loop.run_until_complete(server.start())
    #     loop.run_until_complete(lambda x: asyncio.sleep(100))
    #     try:
    #         await asyncio.sleep(100)
    #         await server.start()# loop.run_forever()
    #     finally:
    #         await server.stop_server()
    #         # loop.run_until_complete(server.stop_server())
    #
    # server_loop = asyncio.new_event_loop()
    # server_thread = threading.Thread(
    #     target=run,
    #     args=(server_loop,),
    #     daemon=True
    # )
    #
    # server_thread.start()
    # time.sleep(0.5)

    loop = event_loop
    # server = Server()
    # loop.create_task(server.start())
    #
    # time.sleep(0.5)

    yield loop

    # loop.run_until_complete(server.stop_server())

    #
    # yield asyncio.new_event_loop()
    #
    # server_loop.call_soon_threadsafe(server_loop.stop)
    # server_thread.join()


async def wait_for_behaviour_is_killed(behaviour, tries=500, sleep=0.01):
    counter = 0
    while not behaviour.is_killed() and counter < tries:
        await asyncio.sleep(sleep)
        counter += 1
    if not behaviour.is_killed():
        raise Exception("Behaviour not finished")
