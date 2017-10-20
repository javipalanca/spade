import logging
from abc import ABCMeta, abstractmethod
from threading import Event

import asyncio

logger = logging.getLogger('spade.Behaviour')


class Behaviour(object, metaclass=ABCMeta):
    def __init__(self):
        self._aiothread = None
        self.agent = None
        self.template = None
        self._force_kill = Event()

        self.queue = None

    def set_aiothread(self, aiothread):
        self._aiothread = aiothread
        self.queue = asyncio.Queue(loop=self._aiothread.loop)

    def set_agent(self, agent):
        self.agent = agent

    def set_template(self, template):
        self.template = template

    def match(self, message):
        if self.template:
            return self.template.match(message)
        return True

    def set(self, name, value):
        self.agent.set(name, value)

    def get(self, name):
        return self.agent.get(name)

    def start(self):
        self._aiothread.submit(self._step())

    def kill(self):
        """
        stops the behaviour
        """
        self._force_kill.set()
        logger.info("Stopping Behavior {}".format(self))

    def is_killed(self):
        return self._force_kill.is_set()

    def done(self):
        """
        returns True if the behaviour has finished
        else returns False
        """
        return False

    async def _step(self):
        if not self.done() and not self.is_killed():
            await self.run()
            self._aiothread.submit(self._step())

    @abstractmethod
    async def run(self):
        raise NotImplementedError

    async def enqueue(self, message):
        await self.queue.put(message)

    def send(self, msg):
        self.agent.send(msg=msg)

    async def receive(self, timeout=None):
        if timeout:
            msg = await asyncio.wait_for(self.queue.get(), timeout=timeout)
        else:
            try:
                msg = await self.queue.get_nowait()
            except asyncio.QueueEmpty:
                msg = None
        return msg


class OneShotBehaviour(Behaviour, metaclass=ABCMeta):
    """
    this behaviour is only executed once
    """

    def __init__(self):
        super().__init__()
        self._already_executed = False

    def done(self):
        if not self._already_executed:
            self._already_executed = True
            return False
        return True
