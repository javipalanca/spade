import asyncio
import logging
import sys
from contextlib import suppress
from threading import Thread

from singletonify import singleton

logger = logging.getLogger("SPADE")


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
        self.aiothread = AioThread()
        self.aiothread.start()
        self.loop = self.aiothread.loop
        self.loop.set_debug(False)
        self.is_running = True

    def __in_coroutine(self):
        try:
            return asyncio.get_event_loop() == self.loop
        except RuntimeError:  # pragma: no cover
            return False

    def start_agent(self, agent, auto_register=True):
        coro = agent._async_start(auto_register=auto_register)

        if self.__in_coroutine():
            return coro
        else:
            return asyncio.run_coroutine_threadsafe(coro, loop=self.loop)

    def stop_agent(self, agent):
        coro = agent._async_stop()

        if self.__in_coroutine():
            return coro
        else:
            return asyncio.run_coroutine_threadsafe(coro, loop=self.loop)

    def reset(self):
        """ Empty the container by unregistering all the agents. """
        self.__agents = {}

    def register(self, agent):
        """
        Register a new agent.

        Args:
            agent (spade.agent.Agent): the agent to be registered
        """
        self.__agents[str(agent.jid)] = agent
        agent.set_container(self)
        agent.set_loop(self.loop)

    def unregister(self, jid):
        if str(jid) in self.__agents:
            del self.__agents[str(jid)]

    def has_agent(self, jid):
        """
        Check if an agent is registered in the container.
        Args:
            jid (str): the jid of the agent to be checked.

        Returns:
            bool: wether the agent is or is not registered.
        """
        return jid in self.__agents

    def get_agent(self, jid):
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

    async def send(self, msg, behaviour):
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
            await behaviour._xmpp_send(msg)

    def stop(self):
        agents = [agent.stop() for agent in self.__agents.values() if agent.is_alive()]
        if self.__in_coroutine():
            coro = asyncio.gather(*agents)
            asyncio.run_coroutine_threadsafe(coro, loop=self.loop)
        self.aiothread.finalize()
        self.reset()
        self.is_running = False


class AioThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.new_event_loop()
        self.running = True
        self.daemon = True

    def run(self):
        try:
            self.loop.run_forever()
            if sys.version_info >= (3, 7):
                tasks = asyncio.all_tasks(loop=self.loop)  # pragma: no cover
            else:
                tasks = asyncio.Task.all_tasks(loop=self.loop)  # pragma: no cover
            for task in tasks:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    self.loop.run_until_complete(task)
            self.loop.close()
            logger.debug("Loop closed")
        except Exception as e:  # pragma: no cover
            logger.error("Exception in the event loop: {}".format(e))

    def finalize(self):
        if self.running:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.running = False


def stop_container():
    container = Container()
    container.stop()
