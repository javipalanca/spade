import collections
import logging
from abc import ABCMeta, abstractmethod
from threading import Event
from datetime import timedelta
from datetime import datetime

import asyncio

now = datetime.now

logger = logging.getLogger('spade.Behaviour')


class Behaviour(object, metaclass=ABCMeta):
    def __init__(self):
        self._aiothread = None
        self.agent = None
        self.template = None
        self._force_kill = Event()
        self.presence = None
        self.web = None

        self.queue = None

    def set_aiothread(self, aiothread):
        """
        Links the behaviour with the event loop.
        Also creates the incoming messages queue.
        :param aiothread: the thread with the event loop
        :type aiothread: :class:`spade.agent.AioThread`
        """
        self._aiothread = aiothread
        self.queue = asyncio.Queue(loop=self._aiothread.loop)

    def set_agent(self, agent):
        """
        links behaviour with its owner agent
        :param agent: the agent who owns the behaviour
        :type agent: :class:`spade.agent.Agent`
        """
        self.agent = agent
        self.presence = agent.presence
        self.web = agent.web

    def set_template(self, template):
        """
        Sets the template that is used to match incoming
        messages with this behaviour.
        :param template: the template to match with
        :type template: :class:`spade.template.Template`
        """
        self.template = template

    def match(self, message):
        """
        Matches a message with the behaviour's template
        :param message: the message to match with
        :type message: :class:`spade.messafe.Message`
        :return: wheter the messaged matches or not
        :rtype: :class:`bool`
        """
        if self.template:
            return self.template.match(message)
        return True

    def set(self, name, value):
        """
        Stores a knowledge item in the agent knowledge base.
        :param name: name of the item
        :type name: :class:`str`
        :param value: value of the item
        :type value: :class:`object`
        """
        self.agent.set(name, value)

    def get(self, name):
        """
        Recovers a knowledge item from the agent's knowledge base.
        :param name: name of the item
        :type name: :class:`str`
        :return: the object retrieved or None
        :rtype: :class:`object`
        """
        return self.agent.get(name)

    def start(self):
        """
        starts behaviour in the event loop
        """
        self._aiothread.submit(self._start())

    async def _start(self):
        """
        start coroutine. runs on_start coroutine and then
        runs the _step coroutine where the body of the behaviour
        is called.
        """
        await self.on_start()
        await self._step()

    def kill(self):
        """
        stops the behaviour
        """
        self._force_kill.set()
        logger.info("Killing behavior {}".format(self))

    def is_killed(self):
        """
        Checks if the behaviour was killed by means of the kill() method.
        :return: whether the behaviour is killed or not
        :rtype: :class:`bool`
        """
        return self._force_kill.is_set()

    def done(self):
        """
        returns True if the behaviour has finished
        else returns False
        :return: whether the behaviour is finished or not
        :rtype: :class:`bool`
        """
        return False

    async def on_start(self):
        """
        coroutine called before the behaviour is started.
        """
        pass

    async def on_end(self):
        """
        coroutine called after the behaviour is done or killed.
        """
        pass

    @abstractmethod
    async def run(self):
        """
        body of the behaviour.
        to be implemented by user
        """
        raise NotImplementedError

    async def _run(self):
        """
        function to be overload by more complex behaviours.
        in other case it just calls run() coroutine.
        """
        await self.run()

    async def _step(self):
        """
        main loop of the behaviour.
        checks whether behaviour is done or killed,
        ortherwise it calls run() coroutine.
        """
        while not self.done() and not self.is_killed():
            await self._run()
        await self.on_end()

    async def enqueue(self, message):
        await self.queue.put(message)

    async def send(self, msg):
        """
        Sends a message.
        :param msg: the message to be sent.
        :type msg: :class:`spade.message.Message`
        """
        if not msg.sender:
            msg.sender = str(self.agent.jid)
            logger.debug(f"Adding agent's jid as sender to message: {msg}")
        aioxmpp_msg = msg.prepare()
        await self.agent.stream.send(aioxmpp_msg)

    async def receive(self, timeout=None):
        """
        receives a message for this behaviour.
        if timeout is not None it returns the message or "None"
        after timeout is done.
        :param timeout: number of seconds until return
        :type timeout: :class:`int`
        :return: a Message or None
        :rtype: :class:`spade.message.Message`
        """
        if timeout:
            coro = self.queue.get()
            try:
                msg = await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                msg = None
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


class PeriodicBehaviour(Behaviour, metaclass=ABCMeta):
    """
    this behaviour is executed periodically with an interval
    """

    def __init__(self, period, start_at=None):
        """
        Creates a periodic behaviour
        :param period: interval of the behaviour in seconds
        :type period: :class:`int`
        :param start_at: whether to start the behaviour with an offset
        :type start_at: :class:`datetime.datetime`
        """
        super().__init__()
        self._period = timedelta(seconds=period)

        if start_at:
            self._next_activation = start_at
        else:
            self._next_activation = now()

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    async def _run(self):
        if now() >= self._next_activation:
            logger.debug(f"Periodic behaviour activated: {self}")
            await self.run()
            while self._next_activation <= now():
                self._next_activation += self._period
        else:
            seconds = (self._next_activation - now()).total_seconds()
            if seconds > 0:
                logger.debug(f"Periodic behaviour going to sleep for {seconds} seconds: {self}")
                await asyncio.sleep(seconds)


class TimeoutBehaviour(OneShotBehaviour, metaclass=ABCMeta):
    """
    this behaviour is executed once at after specified datetime
    """

    def __init__(self, start_at):
        """
        Creates a timeout behaviour, which is run at start_at
        :param start_at: when to start the behaviour
        :type start_at: :class:`datetime.datetime`
        """
        super().__init__()

        self._timeout = start_at
        self._timeout_triggered = False

    async def _run(self):
        if now() >= self._timeout:
            logger.debug(f"Timeout behaviour activated: {self}")
            await self.run()
            self._timeout_triggered = True
        else:
            seconds = (self._timeout - now()).total_seconds()
            if seconds > 0:
                logger.debug(f"Timeout behaviour going to sleep for {seconds} seconds: {self}")
                await asyncio.sleep(seconds)

    def done(self):
        return self._timeout_triggered


class State(OneShotBehaviour, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.next_state = None

    def set_next_state(self, state_name):
        self.next_state = state_name


class NotValidState(Exception):
    pass


class NotValidTransition(Exception):
    pass


class FSMBehaviour(Behaviour):
    def __init__(self):
        super().__init__()
        self._states = {}
        self._transitions = collections.defaultdict(list)
        self.current_state = None

    def add_state(self, name, state, initial=False):
        if not issubclass(state.__class__, State):
            raise AttributeError("state must be subclass of spade.behaviour.State")
        self._states[name] = state
        if initial:
            self.current_state = name

    def add_transition(self, source, dest):
        self._transitions[source].append(dest)

    def is_valid_transition(self, source, dest):
        if dest not in self._states:
            raise NotValidState
        elif dest not in self._transitions[source]:
            raise NotValidTransition
        return True

    async def _run(self):
        behaviour = self._states[self.current_state]
        behaviour.set_aiothread(self._aiothread)
        behaviour.set_agent(self.agent)
        behaviour.receive = self.receive
        logger.info(f"FSM running state {self.current_state}")
        await behaviour.on_start()
        await behaviour.run()
        await behaviour.on_end()
        dest = behaviour.next_state

        if dest:
            try:
                if self.is_valid_transition(self.current_state, dest):
                    logger.info(f"FSM transiting from {self.current_state} to {dest}.")
                    self.current_state = dest
            except NotValidState:
                logger.error(f"FSM could not transitate to state {dest}. That state does not exist.")
                self.kill()
            except NotValidTransition:
                logger.error(f"FSM could not transitate to state {dest}. That transition is not registered.")
                self.kill()
        else:
            logger.info("FSM arrived to a final state (no transitions found). Killing FSM.")
            self.kill()

    async def run(self):
        raise RuntimeError
