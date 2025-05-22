import asyncio
import logging
import sys
import platform
from contextlib import suppress
from typing import Coroutine, Awaitable

import loguru
from pyjabber.server import Server
from pyjabber.server_parameters import Parameters
from singletonify import singleton

from .behaviour import BehaviourType
from .message import Message

logger = logging.getLogger("SPADE")

# check if python is 3.6 or higher
if sys.version_info >= (3, 7) and sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # pragma: no cover


def get_or_create_eventloop():  # pragma: no cover
    """
    Create or retrieve the appropriate event loop, using uvloop on Linux/macOS
    and winloop on Windows if available.
    """
    # Use uvloop or winloop if available
    if platform.system() == "Windows":
        try:
            import winloop  # pyright: ignore[reportMissingImports]

            asyncio.set_event_loop_policy(winloop.EventLoopPolicy())
        except ImportError:
            pass  # winloop is not available, use default
    else:
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass  # uvloop is not available, use default

    # Create or retrieve the event loop
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    return loop


@singleton()
class Container(object):
    """
    The container class allows agents to exchange messages
    without using the XMPP socket if they are in the same
    process.
    The container is a singleton.
    """

    def __init__(self):
        self.__agents = {}
        self.loop = get_or_create_eventloop()
        self.is_running = True

    def reset(self) -> None:
        """Empty the container by unregistering all the agents."""
        self.__init__()

    def register(self, agent) -> None:
        """
        Register a new agent.

        Args:
            agent (spade.agent.Agent): the agent to be registered
        """
        self.__agents[str(agent.jid)] = agent
        agent.set_container(self)
        agent.set_loop(self.loop)

    def unregister(self, jid: str) -> None:
        if str(jid) in self.__agents:
            del self.__agents[str(jid)]

    def has_agent(self, jid: str) -> bool:
        """
        Check if an agent is registered in the container.
        Args:
            jid (str): the jid of the agent to be checked.

        Returns:
            bool: wether the agent is or is not registered.
        """
        return jid in self.__agents

    def get_agent(self, jid: str):
        """
        Returns a registered agent
        Args:
            jid (str): the identifier of the agent

        Returns:
            spade.agent.Agent: the agent you were looking for

        Raises:
            KeyError: if the agent is not found
        """
        return self.__agents[jid]

    def stop_agents(self):
        self.loop.run_until_complete(
            asyncio.gather(*[a.stop() for a in self.__agents.values()])
        )

    async def send(self, msg: Message, behaviour: BehaviourType) -> None:
        """
        This method sends the message using the container mechanism
        when the receiver is also registered in the container. Otherwise,
        it uses the XMPP send method from the original behaviour.
        Args:
            msg (spade.message.Message): the message to be sent
            behaviour: the behaviour that is sending the message
        """
        to = str(msg.to)
        if to in self.__agents:
            self.__agents[to].dispatch(msg)
        else:
            await behaviour._xmpp_send(msg=msg)

    def run(self, coro: Awaitable) -> None:  # pragma: no cover
        self.loop.run_until_complete(coro)


def run_container(
    main_func: Coroutine, embedded_xmpp_server: bool = False
) -> None:  # pragma: no cover
    container = Container()
    server = None

    try:
        if embedded_xmpp_server:
            loguru.logger.remove()  # Silent server
            server_instance = Server(
                Parameters(host="localhost", database_in_memory=True)
            )
            server = container.loop.create_task(server_instance.start())
            container.run(server_instance.ready.wait())
            logger.info("SPADE XMPP server running on localhost:5222")

        container.run(main_func)
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received. Stopping SPADE...")
    except Exception as e:  # pragma: no cover
        logger.error("Exception in the event loop: {}".format(e))

    container.stop_agents()

    # Close server
    if embedded_xmpp_server and server:
        server.cancel()
        container.run(server)

    # Cancel all pending tasks
    if sys.version_info >= (3, 7):  # pragma: no cover
        tasks = asyncio.all_tasks(loop=container.loop)
    else:
        tasks = asyncio.Task.all_tasks(loop=container.loop)

    for task in tasks:
        task.cancel()
        with suppress(asyncio.CancelledError):
            container.run(task)

    # Shutdown asynchronous generators
    container.loop.run_until_complete(container.loop.shutdown_asyncgens())

    # Close the event loop
    container.loop.close()
    logger.debug("Loop closed")
