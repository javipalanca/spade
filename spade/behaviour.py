import collections
import logging
from abc import ABCMeta, abstractmethod
from threading import Event
from datetime import timedelta
from datetime import datetime

import asyncio

now = datetime.now

logger = logging.getLogger('spade.behaviour')


class BehaviourNotFinishedException(Exception):
    pass


class NotValidState(Exception):
    pass


class NotValidTransition(Exception):
    pass


class CyclicBehaviour(object, metaclass=ABCMeta):
    """
    this behaviour is executed cyclically until it is stopped.
    """

    def __init__(self):
        self.agent = None
        self.template = None
        self._force_kill = Event()
        self._exit_code = 0
        self.presence = None
        self.web = None

        self.queue = None

    def set_agent(self, agent):
        """
        links behaviour with its owner agent
        :param agent: the agent who owns the behaviour
        :type agent: :class:`spade.agent.Agent`
        """
        self.agent = agent
        self.queue = asyncio.Queue(loop=self.agent.loop)
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
        self.agent.submit(self._start())

    async def _start(self):
        """
        start coroutine. runs on_start coroutine and then
        runs the _step coroutine where the body of the behaviour
        is called.
        """
        self.agent._alive.wait()
        try:
            await self.on_start()
        except Exception as e:
            logger.error("Exception running on_start in behaviour {}: {}".format(self, e))
            self.kill(exit_code=e)
        await self._step()

    def kill(self, exit_code=None):
        """
        stops the behaviour
        :param exit_code: the exit code of the behaviour
        :type exit_code: :class:`object`
        """
        self._force_kill.set()
        if exit_code is not None:
            self._exit_code = exit_code
        logger.info("Killing behavior {0} with exit code: {1}".format(self, exit_code))

    def is_killed(self):
        """
        Checks if the behaviour was killed by means of the kill() method.
        :return: whether the behaviour is killed or not
        :rtype: :class:`bool`
        """
        return self._force_kill.is_set()

    @property
    def exit_code(self):
        """
        Returns the exit_code of the behaviour.
        It only works when the behaviour is done or killed,
        otherwise it raises an exception.
        :return: the exit code of the behaviour
        :rtype: :class:`object`
        :raises: BehaviourNotFinishedException
        """
        if self.done() or self.is_killed():
            return self._exit_code
        else:
            raise BehaviourNotFinishedException

    @exit_code.setter
    def exit_code(self, value):
        """
        Sets a new exit code to the behaviour.
        :param value: the new exit code
        :type value: :class:`object`
        """
        self._exit_code = value

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
        raise NotImplementedError  # pragma: no cover

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
            try:
                await self._run()
            except Exception as e:
                logger.error("Exception running behaviour {}: {}".format(self, e))
                self.kill(exit_code=e)
        try:
            await self.on_end()
        except Exception as e:
            logger.error("Exception running on_end in behaviour {}: {}".format(self, e))
            self.kill(exit_code=e)

    async def enqueue(self, message):
        """
        Enqueues a message in the behaviour's mailbox
        :param message: the message to be enqueued
        :type message: spade.message.Message
        """
        await self.queue.put(message)

    def mailbox_size(self):
        """
        checks if there is a message in the mailbox
        :return: the number of messages in the mailbox
        :rtype: int
        """
        return self.queue.qsize()

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
        msg.sent = True
        self.agent.traces.append(msg, category=str(self))

    async def receive(self, timeout=None):
        """
        receives a message for this behaviour.
        if timeout is not None it returns the message or "None"
        after timeout is done.
        :param timeout: number of seconds until return
        :type timeout: :class:`float`
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
                msg = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                msg = None
        return msg

    def __str__(self):
        return "{}/{}".format("/".join(base.__name__ for base in self.__class__.__bases__), self.__class__.__name__)


class OneShotBehaviour(CyclicBehaviour, metaclass=ABCMeta):
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


class PeriodicBehaviour(CyclicBehaviour, metaclass=ABCMeta):
    """
    this behaviour is executed periodically with an interval
    """

    def __init__(self, period, start_at=None):
        """
        Creates a periodic behaviour
        :param period: interval of the behaviour in seconds
        :type period: :class:`float`
        :param start_at: whether to start the behaviour with an offset
        :type start_at: :class:`datetime.datetime`
        """
        super().__init__()
        self._period = None
        self.period = period

        if start_at:
            self._next_activation = start_at
        else:
            self._next_activation = now()

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if value < 0:
            raise ValueError("Period must be greater or equal than zero.")
        self._period = timedelta(seconds=value)

    async def _run(self):
        if now() >= self._next_activation:
            logger.debug(f"Periodic behaviour activated: {self}")
            await self.run()
            if self.period <= timedelta(seconds=0):
                self._next_activation = now()
            else:
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
                await self.run()
                self._timeout_triggered = True

    def done(self):
        return self._timeout_triggered


class State(OneShotBehaviour, metaclass=ABCMeta):
    """
    A state of a FSMBehaviour is a OneShotBehaviour
    """

    def __init__(self):
        super().__init__()
        self.next_state = None

    def set_next_state(self, state_name):
        """
        Set the state to transition to when this state is finished.
        state_name must be a valid state and the transition must be registered.
        If set_next_state is not called then current state is a final state.
        :param state_name: the name of the state to transition to
        :type state_name: str
        """
        self.next_state = state_name


class FSMBehaviour(CyclicBehaviour):
    """
    A behaviour composed of states (oneshotbehaviours) that may transition from one state to another.
    """

    def __init__(self):
        super().__init__()
        self._states = {}
        self._transitions = collections.defaultdict(list)
        self.current_state = None
        self.setup()

    def setup(self):
        pass

    def add_state(self, name, state, initial=False):
        """
        Adds a new state to the FSM.
        :param name: the name of the state, which is used as its identifier.
        :type name: str
        :param state: The state class
        :type state: spade.behaviour.State
        :param initial: wether the state is the initial state or not. (Only one initial state is allowed)
        :type initial: bool
        """
        if not issubclass(state.__class__, State):
            raise AttributeError("state must be subclass of spade.behaviour.State")
        self._states[name] = state
        if initial:
            self.current_state = name

    def add_transition(self, source, dest):
        """
        Adds a transition from one state to another.
        :param source: the name of the state from where the transition starts
        :type source: str
        :param dest: the name of the state where the transition ends
        :type dest: str
        """
        self._transitions[source].append(dest)

    def is_valid_transition(self, source, dest):
        """
        Checks if a transitions is registered in the FSM
        :param source: the source state name
        :type source: str
        :param dest: the destination state name
        :type dest: str
        :return: wether the transition is valid or not
        :rtype: bool
        """
        if dest not in self._states or source not in self._states:
            raise NotValidState
        elif dest not in self._transitions[source]:
            raise NotValidTransition
        return True

    async def _run(self):
        behaviour = self._states[self.current_state]
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
            except NotValidState as e:
                logger.error(f"FSM could not transitate to state {dest}. That state does not exist.")
                self.kill(exit_code=e)
            except NotValidTransition as e:
                logger.error(f"FSM could not transitate to state {dest}. That transition is not registered.")
                self.kill(exit_code=e)
        else:
            logger.info("FSM arrived to a final state (no transitions found). Killing FSM.")
            self.kill()

    async def run(self):
        """
        In this kind of behaviour there is no need to overload run.
        The run methods to be overloaded are in the State class.
        """
        raise RuntimeError  # pragma: no cover

    def to_graphviz(self):
        """
        Converts the FSM behaviour structure to Graphviz syntax
        :return: the graph in Graphviz syntax
        :rtype: str
        """
        graph = "digraph finite_state_machine { rankdir=LR; node [fixedsize=true];"
        for origin, dest in self._transitions.items():
            origin = origin.replace(" ", "_")
            for d in dest:
                d = d.replace(" ", "_")
                graph += "{0} -> {1};".format(origin, d)
        graph += "}"
        return graph
