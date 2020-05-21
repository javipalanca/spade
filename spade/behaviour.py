import asyncio
import collections
import logging
import time
import traceback
from abc import ABCMeta, abstractmethod
from asyncio import CancelledError
from datetime import timedelta, datetime
from threading import Event
from typing import Any, Union

from .message import Message
from .template import Template

now = datetime.now

logger = logging.getLogger("spade.behaviour")


class BehaviourNotFinishedException(Exception):
    """ """

    pass


class NotValidState(Exception):
    """ """

    pass


class NotValidTransition(Exception):
    """ """

    pass


class CyclicBehaviour(object, metaclass=ABCMeta):
    """ This behaviour is executed cyclically until it is stopped. """

    def __init__(self):
        self.agent = None
        self.template = None
        self._force_kill = Event()
        self._is_done = asyncio.Event()
        self._is_done.set()
        self._exit_code = 0
        self.presence = None
        self.web = None
        self.is_running = False

        self.queue = None

    def set_agent(self, agent):
        """
        Links behaviour with its owner agent

        Args:
          agent (spade.agent.Agent): the agent who owns the behaviour

        """
        self.agent = agent
        self.queue = asyncio.Queue(loop=self.agent.loop)
        self.presence = agent.presence
        self.web = agent.web

    def set_template(self, template: Template):
        """
        Sets the template that is used to match incoming
        messages with this behaviour.

        Args:
          template (spade.template.Template): the template to match with

        """
        self.template = template

    def match(self, message: Message) -> bool:
        """
        Matches a message with the behaviour's template

        Args:
          message(spade.message.Message): the message to match with

        Returns:
          bool: wheter the messaged matches or not

        """
        if self.template:
            return self.template.match(message)
        return True

    def set(self, name: str, value: Any) -> None:
        """
        Stores a knowledge item in the agent knowledge base.

        Args:
          name (str): name of the item
          value (Any): value of the item

        """
        self.agent.set(name, value)

    def get(self, name: str) -> Any:
        """
        Recovers a knowledge item from the agent's knowledge base.

        Args:
          name (str): name of the item

        Returns:
          Any: the object retrieved or None

        """
        return self.agent.get(name)

    def start(self):
        """starts behaviour in the event loop"""
        self.agent.submit(self._start())
        self.is_running = True

    async def _start(self):
        """
        Start coroutine. runs on_start coroutine and then
        runs the _step coroutine where the body of the behaviour
        is called.
        """
        self.agent._alive.wait()
        try:
            await self.on_start()
        except Exception as e:
            logger.error(
                "Exception running on_start in behaviour {}: {}".format(self, e)
            )
            self.kill(exit_code=e)
        await self._step()
        self._is_done.clear()

    def kill(self, exit_code: Any = None):
        """
        Stops the behaviour

        Args:
          exit_code (object, optional): the exit code of the behaviour (Default value = None)

        """
        self._force_kill.set()
        if exit_code is not None:
            self._exit_code = exit_code
        logger.info("Killing behavior {0} with exit code: {1}".format(self, exit_code))

    def is_killed(self) -> bool:
        """
        Checks if the behaviour was killed by means of the kill() method.

        Returns:
          bool: whether the behaviour is killed or not

        """
        return self._force_kill.is_set()

    @property
    def exit_code(self) -> Any:
        """
        Returns the exit_code of the behaviour.
        It only works when the behaviour is done or killed,
        otherwise it raises an exception.

        Returns:
          object: the exit code of the behaviour

        """
        if self._done() or self.is_killed():
            return self._exit_code
        else:
            raise BehaviourNotFinishedException

    @exit_code.setter
    def exit_code(self, value: Any):
        """
        Sets a new exit code to the behaviour.

        Args:
          value (object): the new exit code

        """
        self._exit_code = value

    def _done(self) -> bool:
        """
        Returns True if the behaviour has finished
        else returns False

        Returns:
          bool: whether the behaviour is finished or not

        """
        return False

    def is_done(self):
        return not self._is_done.is_set()

    def join(self, timeout=None):

        try:
            in_coroutine = asyncio.get_event_loop() == self.agent.loop
        except RuntimeError:  # pragma: no cover
            in_coroutine = False

        if not in_coroutine:
            t_start = time.time()
            while not self.is_done():
                time.sleep(0.001)
                t = time.time()
                if timeout is not None and t - t_start > timeout:
                    raise TimeoutError
        else:
            return self._async_join(timeout=timeout)

    async def _async_join(self, timeout):
        t_start = time.time()
        while not self.is_done():
            await asyncio.sleep(0.001)
            t = time.time()
            if timeout is not None and t - t_start > timeout:
                raise TimeoutError

    async def on_start(self):
        """
        Coroutine called before the behaviour is started.
        """
        pass

    async def on_end(self):
        """
        Coroutine called after the behaviour is done or killed.
        """
        pass

    @abstractmethod
    async def run(self):
        """
        Body of the behaviour.
        To be implemented by user.
        """
        raise NotImplementedError  # pragma: no cover

    async def _run(self):
        """
        Function to be overload by more complex behaviours.
        In other case it just calls run() coroutine.
        """
        await self.run()

    async def _step(self):
        """
        Main loop of the behaviour.
        checks whether behaviour is done or killed,
        ortherwise it calls run() coroutine.
        """
        cancelled = False
        while not self._done() and not self.is_killed():
            try:
                await self._run()
                await asyncio.sleep(0)  # relinquish cpu
            except CancelledError:
                logger.info("Behaviour {} cancelled".format(self))
                cancelled = True
            except Exception as e:
                logger.error(
                    "Exception running behaviour {behav}: {exc}".format(
                        behav=self, exc=e
                    )
                )
                logger.error(traceback.format_exc())
                self.kill(exit_code=e)
        try:
            if not cancelled:
                await self.on_end()
        except Exception as e:
            logger.error("Exception running on_end in behaviour {}: {}".format(self, e))
            self.kill(exit_code=e)
        self.agent.remove_behaviour(self)

    async def enqueue(self, message: Message):
        """
        Enqueues a message in the behaviour's mailbox

        Args:
            message (spade.message.Message): the message to be enqueued
        """
        await self.queue.put(message)

    def mailbox_size(self) -> int:
        """
        Checks if there is a message in the mailbox

        Returns:
          int: the number of messages in the mailbox

        """
        return self.queue.qsize()

    async def send(self, msg: Message):
        """
        Sends a message.

        Args:
            msg (spade.message.Message): the message to be sent.
        """
        if not msg.sender:
            msg.sender = str(self.agent.jid)
            logger.debug(f"Adding agent's jid as sender to message: {msg}")
        await self.agent.container.send(msg, self)
        msg.sent = True
        self.agent.traces.append(msg, category=str(self))

    async def _xmpp_send(self, msg: Message):
        aioxmpp_msg = msg.prepare()
        await self.agent.client.send(aioxmpp_msg)

    async def receive(self, timeout: float = None) -> Union[Message, None]:
        """
        Receives a message for this behaviour.
        If timeout is not None it returns the message or "None"
        after timeout is done.

        Args:
            timeout (float): number of seconds until return

        Returns:
            spade.message.Message: a Message or None
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
        return "{}/{}".format(
            "/".join(base.__name__ for base in self.__class__.__bases__),
            self.__class__.__name__,
        )


class OneShotBehaviour(CyclicBehaviour, metaclass=ABCMeta):
    """This behaviour is only executed once"""

    def __init__(self):
        super().__init__()
        self._already_executed = False

    def _done(self) -> bool:
        """ """
        if not self._already_executed:
            self._already_executed = True
            return False
        return True


class PeriodicBehaviour(CyclicBehaviour, metaclass=ABCMeta):
    """This behaviour is executed periodically with an interval"""

    def __init__(self, period, start_at=None):
        """
        Creates a periodic behaviour.

        Args:
            period (float): interval of the behaviour in seconds
            start_at (datetime.datetime): whether to start the behaviour with an offset
        """
        super().__init__()
        self._period = None
        self.period = period

        if start_at:
            self._next_activation = start_at
        else:
            self._next_activation = now()

    @property
    def period(self) -> timedelta:
        """ Get the period. """
        return self._period

    @period.setter
    def period(self, value: float):
        """
        Set the period.

        Args:
          value (float): seconds
        """
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
                logger.debug(
                    f"Periodic behaviour going to sleep for {seconds} seconds: {self}"
                )
                await asyncio.sleep(seconds)


class TimeoutBehaviour(OneShotBehaviour, metaclass=ABCMeta):
    """This behaviour is executed once at after specified datetime"""

    def __init__(self, start_at):
        """
        Creates a timeout behaviour, which is run at start_at

        Args:
            start_at (datetime.datetime): when to start the behaviour
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
                logger.debug(
                    f"Timeout behaviour going to sleep for {seconds} seconds: {self}"
                )
                await asyncio.sleep(seconds)
                await self.run()
                self._timeout_triggered = True

    def _done(self) -> bool:
        """ """
        return self._timeout_triggered


class State(OneShotBehaviour, metaclass=ABCMeta):
    """A state of a FSMBehaviour is a OneShotBehaviour"""

    def __init__(self):
        super().__init__()
        self.next_state = None

    def set_next_state(self, state_name):
        """
        Set the state to transition to when this state is finished.
        state_name must be a valid state and the transition must be registered.
        If set_next_state is not called then current state is a final state.

        Args:
          state_name (str): the name of the state to transition to

        """
        self.next_state = state_name


class FSMBehaviour(CyclicBehaviour):
    """A behaviour composed of states (oneshotbehaviours) that may transition from one state to another."""

    def __init__(self):
        super().__init__()
        self._states = {}
        self._transitions = collections.defaultdict(list)
        self.current_state = None
        self.setup()

    def setup(self):
        """ """
        pass

    def add_state(self, name: str, state: State, initial: bool = False):
        """ Adds a new state to the FSM.

        Args:
          name (str): the name of the state, which is used as its identifier.
          state (spade.behaviour.State): The state class
          initial (bool, optional): wether the state is the initial state or not. (Only one initial state is allowed) (Default value = False)

        """
        if not issubclass(state.__class__, State):
            raise AttributeError("state must be subclass of spade.behaviour.State")
        self._states[name] = state
        if initial:
            self.current_state = name

    def get_state(self, name):
        return self._states[name]

    def get_states(self):
        return self._states

    def add_transition(self, source: str, dest: str):
        """ Adds a transition from one state to another.

        Args:
          source (str): the name of the state from where the transition starts
          dest (str): the name of the state where the transition ends

        """
        self._transitions[source].append(dest)

    def is_valid_transition(self, source: str, dest: str) -> bool:
        """
        Checks if a transitions is registered in the FSM

        Args:
          source (str): the source state name
          dest (str): the destination state name

        Returns:
          bool: wether the transition is valid or not

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
        try:
            await behaviour.on_start()
        except Exception as e:
            logger.error("Exception running on_start in state {}: {}".format(self, e))
            self.kill(exit_code=e)
        try:
            await behaviour.run()
        except Exception as e:
            logger.error("Exception running state {}: {}".format(self, e))
            self.kill(exit_code=e)
        try:
            await behaviour.on_end()
        except Exception as e:
            logger.error("Exception running on_start in state {}: {}".format(self, e))
            self.kill(exit_code=e)

        dest = behaviour.next_state
        behaviour._is_done.clear()

        if dest:
            try:
                if self.is_valid_transition(self.current_state, dest):
                    logger.info(f"FSM transiting from {self.current_state} to {dest}.")
                    self.current_state = dest
            except NotValidState as e:
                logger.error(
                    f"FSM could not transitate to state {dest}. That state does not exist."
                )
                self.kill(exit_code=e)
            except NotValidTransition as e:
                logger.error(
                    f"FSM could not transitate to state {dest}. That transition is not registered."
                )
                self.kill(exit_code=e)
        else:
            logger.info(
                "FSM arrived to a final state (no transitions found). Killing FSM."
            )
            self.kill()

    async def run(self):
        """
        In this kind of behaviour there is no need to overload run.
        The run methods to be overloaded are in the State class.
        """
        raise RuntimeError  # pragma: no cover

    def to_graphviz(self) -> str:
        """
        Converts the FSM behaviour structure to Graphviz syntax

        Returns:
          str: the graph in Graphviz syntax

        """
        graph = "digraph finite_state_machine { rankdir=LR; node [fixedsize=true];"
        for origin, dest in self._transitions.items():
            origin = origin.replace(" ", "_")
            for d in dest:
                d = d.replace(" ", "_")
                graph += "{0} -> {1};".format(origin, d)
        graph += "}"
        return graph
