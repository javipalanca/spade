import asyncio
import logging
from asyncio import Task
from hashlib import md5
from typing import Coroutine, Optional, Type, Any, List, TypeVar

from slixmpp import JID
from slixmpp import Message as slixmppMessage

from .behaviour import BehaviourType, FSMBehaviour, CyclicBehaviour
from .container import Container
from .message import Message
from .presence import PresenceManager
from .template import Template
from .trace import TraceStore
from .web import WebApp
from .xmpp_client import XMPPClient

logger = logging.getLogger("spade.Agent")

AgentType = TypeVar("AgentType", bound="Agent")


class AuthenticationFailure(Exception):
    """ """

    pass


class DisconnectedException(Exception):
    """ """

    pass


class Agent(object):
    def __init__(
        self, jid: str, password: str, port: int = 5222, verify_security: bool = False
    ):
        """
        Creates an agent

        Args:
          jid (str): The identifier of the agent in the form username@server
          password (str): The password to connect to the server
          verify_security (bool): Weather to verify or not the SSL certificates
        """
        self.jid = JID(jid)
        self.password = password
        self.xmpp_port = port
        self.verify_security = verify_security

        self.behaviours: list = []
        self._values: dict = {}

        self.client: Optional[XMPPClient] = None
        self.presence: Optional[PresenceManager] = None
        self.loop = None

        self.container = Container()
        self.container.register(self)

        self.loop = self.container.loop
        asyncio.set_event_loop(self.loop)

        # Web service
        self.web = WebApp(agent=self)

        self.traces = TraceStore(size=1000)

        self._alive = asyncio.Event()

    def set_loop(self, loop) -> None:
        self.loop = loop

    def set_container(self, container: Container) -> None:
        """
        Sets the container to which the agent is attached

        Args:
            container (spade.container.Container): the container to be attached to
        """
        self.container = container

    async def start(self, auto_register: bool = True) -> None:
        """
        Starts this agent.

        Args:
            auto_register (bool): register the agent in the server (Default value = True)

        Returns:
            None
        """
        return await self._async_start(auto_register=auto_register)

    async def _async_start(self, auto_register: bool = True) -> None:
        """
        Starts the agent from a coroutine. This fires some actions:

            * if auto_register: register the agent in the server
            * runs the event loop
            * connects the agent to the server
            * runs the registered behaviours

        Args:
          auto_register (bool, optional): register the agent in the server (Default value = True)

        """
        await self._hook_plugin_before_connection()

        self.client = XMPPClient(
            self.jid, self.password, self.verify_security, auto_register
        )
        # Presence service
        self.presence = PresenceManager(agent=self, approve_all=False)

        await self._async_connect()

        await self._hook_plugin_after_connection()

        await self.setup()
        self._alive.set()
        for behaviour in self.behaviours:
            if not behaviour.is_running:
                behaviour.set_agent(self)
                if issubclass(type(behaviour), FSMBehaviour):
                    for _, state in behaviour.get_states().items():
                        state.set_agent(self)
                behaviour.start()

    async def _hook_plugin_before_connection(self) -> None:
        """
        Overload this method to hook a plugin before connection is done
        """
        pass

    async def _hook_plugin_after_connection(self) -> None:
        """
        Overload this method to hook a plugin after connection is done
        """
        pass

    async def _async_connect(self) -> None:  # pragma: no cover
        """connect and authenticate to the XMPP server. Async mode."""

        self.client.connected_event = asyncio.Event()
        self.client.disconnected_event = asyncio.Event()
        self.client.failed_auth_event = asyncio.Event()

        connected_task = asyncio.create_task(
            self.client.connected_event.wait(), name="connected"
        )
        disconnected_task = asyncio.create_task(
            self.client.disconnected_event.wait(), name="disconnected"
        )
        failed_auth_task = asyncio.create_task(
            self.client.failed_auth_event.wait(), name="failed_auth"
        )

        self.client.add_event_handler(
            "session_start", lambda _: self.client.connected_event.set()
        )
        self.client.add_event_handler(
            "disconnected", lambda _: self.client.disconnected_event.set()
        )
        self.client.add_event_handler(
            "failed_all_auth", lambda _: self.client.failed_auth_event.set()
        )
        self.client.add_event_handler("message", self._message_received)

        self.client.connect(host=self.jid.host, port=self.xmpp_port)

        done, pending = await asyncio.wait(
            [connected_task, disconnected_task, failed_auth_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        for task in done:
            await task

            if task.get_name() == "failed_auth":
                raise AuthenticationFailure(
                    "Could not authenticate the agent. Check user and password or use auto_register=True"
                )
            elif task.get_name() == "disconnected":
                raise DisconnectedException(
                    "Error during the connection with the server"
                )

        logger.info(f"Agent {str(self.jid)} connected and authenticated.")

    async def setup(self) -> None:
        """
        Setup agent before startup.
        This coroutine may be overloaded.
        """
        await asyncio.sleep(0)

    @property
    def name(self) -> str:
        """
        Returns the name of the agent (the string before the '@')

        Returns:
            str: the name of the agent (the string before the '@')
        """
        return self.jid.node

    @property
    def avatar(self) -> str:
        """
        Generates a unique avatar for the agent based on its JID.
        Uses Gravatar service with MonsterID option.

        Returns:
          str: the url of the agent's avatar

        """
        return self.build_avatar_url(self.jid.bare)

    @staticmethod
    def build_avatar_url(jid: str) -> str:
        """
        Static method to build a gravatar url with the agent's JID

        Args:
          jid (aioxmpp.JID): an XMPP identifier

        Returns:
          str: a URL for the gravatar

        """
        digest = md5(str(jid).encode("utf-8")).hexdigest()  # nosec
        return "http://www.gravatar.com/avatar/{md5}?d=monsterid".format(md5=digest)

    def submit(self, coro: Coroutine) -> Task:
        """
        Runs a coroutine in the event loop of the agent.
        this call is not blocking.

        Args:
          coro (Coroutine): the coroutine to be run

        Returns:
            asyncio.Task: the Task assigned to the coroutine execution

        """
        return asyncio.create_task(coro)

    def add_behaviour(
        self, behaviour: BehaviourType, template: Optional[Template] = None
    ) -> None:
        """
        Adds and starts a behaviour to the agent.
        If template is not None it is used to match
        new messages and deliver them to the behaviour.

        Args:
          behaviour (Type[spade.behaviour.CyclicBehaviour]): the behaviour to be started
          template (spade.template.Template, optional): the template to match messages with (Default value = None)

        """
        behaviour.set_agent(agent=self)
        if issubclass(type(behaviour), FSMBehaviour):
            for _, state in behaviour.get_states().items():
                state.set_agent(self)
        behaviour.set_template(template)
        self.behaviours.append(behaviour)
        if self.is_alive():
            behaviour.start()

    def remove_behaviour(self, behaviour: Type[CyclicBehaviour]) -> None:
        """
        Removes a behaviour from the agent.
        The behaviour is first killed.

        Args:
          behaviour (Type[spade.behaviour.CyclicBehaviour]): the behaviour instance to be removed

        """
        if not self.has_behaviour(behaviour):
            raise ValueError("This behaviour is not registered")
        index = self.behaviours.index(behaviour)
        self.behaviours[index].kill()
        self.behaviours.pop(index)

    def has_behaviour(self, behaviour: Type[CyclicBehaviour]) -> bool:
        """
        Checks if a behaviour is added to an agent.

        Args:
          behaviour (Type[spade.behaviour.CyclicBehaviour]): the behaviour instance to check

        Returns:
          bool: a boolean that indicates wether the behaviour is inside the agent.

        """
        return behaviour in self.behaviours

    async def stop(self) -> None:
        """
        Stops this agent.
        """
        return await self._async_stop()

    async def _async_stop(self) -> None:
        """Stops an agent and kills all its behaviours."""
        if self.presence:
            self.presence.set_unavailable()
        for behav in self.behaviours:
            behav.kill()
        if self.web.is_started():
            await self.web.runner.cleanup()

        if self.is_alive():
            # Disconnect from XMPP server
            await self.client.disconnect()
            logger.info("Client disconnected.")

        self._alive.clear()

    def is_alive(self) -> bool:
        """
        Checks if the agent is alive.

        Returns:
          bool: wheter the agent is alive or not

        """
        return self._alive.is_set()

    def set(self, name: str, value: Any):
        """
        Stores a knowledge item in the agent knowledge base.

        Args:
          name (str): name of the item
          value (object): value of the item

        """
        self._values[name] = value

    def get(self, name: str) -> Any:
        """
        Recovers a knowledge item from the agent's knowledge base.

        Args:
          name(str): name of the item

        Returns:
          object: the object retrieved or None

        """
        if name in self._values:
            return self._values[name]
        else:
            return None

    def _message_received(self, msg: slixmppMessage) -> List[Task]:
        """
        Callback run when an XMPP Message is reveived.
        This callback delivers the message to every behaviour
        that is waiting for it. First, the aioxmpp.Message is
        converted to spade.message.Message

        Args:
          msg (slixmpp.Message): the message just received.

        Returns:
            list(asyncio.Future): a list of futures of the appended of the message at each matched behaviour.

        """

        msg = Message.from_node(msg)
        return self.dispatch(msg)

    def dispatch(self, msg: Message) -> List[Task]:
        """
        Dispatch the message to every behaviour that is waiting for
        it using their templates match.

        Args:
          msg (spade.message.Message): the message to dispatch.

        Returns:
            list(asyncio.Future): a list of tasks for each message queuing in each matching behavior.

        """
        logger.debug(f"Got message: {msg}")
        tasks = []
        matched = False
        for behaviour in (x for x in self.behaviours if x.match(msg)):
            tasks.append(self.submit(behaviour.enqueue(msg)))
            logger.debug(f"Message enqueued to behaviour: {behaviour}")
            self.traces.append(msg, category=str(behaviour))
            matched = True
        if not matched:
            logger.warning(f"No behaviour matched for message: {msg}")
            self.traces.append(msg)
        return tasks
