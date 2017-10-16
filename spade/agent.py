import logging
import sys
import asyncio
from threading import Thread, Event

import aioxmpp

logger = logging.getLogger('spade.Agent')


class Agent(object):
    def __init__(self, jid, password, verify_security=False):
        self.jid = aioxmpp.JID.fromstr(jid)
        self.password = password

        self.behaviours = []
        self._values = {}

        self.aiothread = AioThread(self.jid, password, verify_security)

        self.aiothread.start()
        self.aiothread.event.wait()

        # obtain an instance of the service
        message_dispatcher = self.client.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )

        # register a message callback here
        message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.message_received,
        )

    @property
    def client(self):
        return self.aiothread.client

    @property
    def stream(self):
        return self.aiothread.stream

    def submit(self, coro):
        return self.aiothread.submit(coro)

    def add_behaviour(self, behav):
        behav.set_aiothread(self.aiothread)
        behav.set_agent(self)
        self.behaviours.append(behav)
        behav.start()

    def stop(self):
        for behav in self.behaviours:
            behav.kill()
        self.aiothread.finalize()

    def set(self, name, value):
        self._values[name] = value

    def get(self, name):
        return self._values[name]

    def send(self, msg):
        return self.submit(self.stream.send(msg))

    def message_received(self, msg):
        logger.debug(f"got message: {msg} with content: {msg.body}")


class AioThread(Thread):
    def __init__(self, jid, password, verify_security, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = Event()
        self.conn_coro = None
        self.stream = None

        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(True)
        asyncio.set_event_loop(self.loop)
        self.client = aioxmpp.PresenceManagedClient(jid,
                                                    aioxmpp.make_security_layer(password,
                                                                                no_verify=not verify_security),
                                                    loop=self.loop)
        self.connect()

    def run(self):
        self.loop.call_soon(self.event.set)
        self.loop.run_forever()

    def connect(self):
        self.conn_coro = self.client.connected()
        aenter = type(self.conn_coro).__aenter__(self.conn_coro)
        self.stream = self.loop.run_until_complete(aenter)

    def submit(self, coro):
        fut = asyncio.run_coroutine_threadsafe(coro, loop=self.loop)
        return fut

    def finalize(self):
        aexit = self.conn_coro.__aexit__(*sys.exc_info())
        asyncio.run_coroutine_threadsafe(aexit, loop=self.loop)
        # asyncio.gather(*asyncio.Task.all_tasks()).cancel()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
