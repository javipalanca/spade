import logging
from threading import Event

logger = logging.getLogger('spade.Behaviour')


class Behaviour(object):
    def __init__(self):
        self._aiothread = None
        self.agent = None
        self._force_kill = Event()

    def set_aiothread(self, aiothread):
        self._aiothread = aiothread

    def set_agent(self, agent):
        self.agent = agent

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

    async def run(self):
        raise NotImplementedError


class OneShotBehaviour(Behaviour):
    """
    this behaviour is only executed once
    """

    def __init__(self):
        super().__init__()
        self._already_executed = False

    def done(self):
        if not self._already_executed:
            self._already_executed = not self._already_executed
            return not self._already_executed
        return self._already_executed
