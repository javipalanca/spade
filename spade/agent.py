import logging

import aiosasl
import sys
import asyncio
from hashlib import md5
from threading import Thread, Event

import aioxmpp
import aioxmpp.ibr as ibr
from aioxmpp.dispatcher import SimpleMessageDispatcher

from spade.message import Message
from spade.presence import PresenceManager
from spade.trace import TraceStore
from spade.web import WebApp

logger = logging.getLogger('spade.Agent')


class AuthenticationFailure(Exception):
    """ """
    pass


class Agent(object):
    def __init__(self, jid, password, verify_security=False, loop=None):
        """
        Creates an agent

        Args:
          jid (str): The identifier of the agent in the form username@server
          password (str): The password to connect to the server
          verify_security (bool): Wether to verify or not the SSL certificates
          loop (an asyncio event loop): the event loop if it was already created (optional)
        """
        self.jid = aioxmpp.JID.fromstr(jid)
        self.password = password
        self.verify_security = verify_security

        self.behaviours = []
        self._values = {}

        self.traces = TraceStore(size=1000)

        if loop:
            self.loop = loop
            self.external_loop = True
        else:
            self.loop = asyncio.new_event_loop()
            self.external_loop = False
        asyncio.set_event_loop(self.loop)

        self.aiothread = AioThread(self, self.loop)
        self._alive = Event()

        # obtain an instance of the service
        self.message_dispatcher = self.client.summon(SimpleMessageDispatcher)

        # Presence service
        self.presence = PresenceManager(self)

        # Web service
        self.web = WebApp(agent=self)

    def start(self, auto_register=True):
        """
        Starts the agent. This fires some actions:

            * if auto_register: register the agent in the server
            * runs the event loop
            * connects the agent to the server
            * runs the registered behaviours

        Args:
          auto_register (bool, optional): register the agent in the server (Default value = True)

        """
        if auto_register:
            self.register()

        self.aiothread.connect()

        self._start()

    async def async_start(self, auto_register=True):
        """
        Starts the agent from a coroutine. This fires some actions:

            * if auto_register: register the agent in the server
            * runs the event loop
            * connects the agent to the server
            * runs the registered behaviours

        Args:
          auto_register (bool, optional): register the agent in the server (Default value = True)

        """
        if auto_register:
            await self.async_register()

        await self.aiothread.async_connect()

        self._start()

    def _start(self):
        self.aiothread.start()
        self._alive.set()
        # register a message callback here
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self._message_received,
        )
        self.setup()

    def register(self):  # pragma: no cover
        """ Register the agent in the XMPP server. """

        metadata = aioxmpp.make_security_layer(None, no_verify=not self.verify_security)
        query = ibr.Query(self.jid.localpart, self.password)
        _, stream, features = self.loop.run_until_complete(aioxmpp.node.connect_xmlstream(self.jid, metadata))
        self.loop.run_until_complete(ibr.register(stream, query))

    async def async_register(self):  # pragma: no cover
        """ Register the agent in the XMPP server from a coroutine. """
        metadata = aioxmpp.make_security_layer(None, no_verify=not self.verify_security)
        query = ibr.Query(self.jid.localpart, self.password)
        _, stream, features = await aioxmpp.node.connect_xmlstream(self.jid, metadata)
        await ibr.register(stream, query)

    def setup(self):
        """
        Setup agent before startup.
        This method may be overloaded.
        """
        pass

    @property
    def name(self):
        """ Returns the name of the agent (the string before the '@') """
        return self.jid.localpart

    @property
    def client(self):
        """ Returns the client that is connected to the xmpp server """
        return self.aiothread.client

    @property
    def stream(self):
        """ Returns the stream of the connection """
        return self.aiothread.stream

    @property
    def avatar(self):
        """
        Generates a unique avatar for the agent based on its JID.
        Uses Gravatar service with MonsterID option.

        Returns:
          str: the url of the agent's avatar

        """
        return self.build_avatar_url(self.jid.bare())

    @staticmethod
    def build_avatar_url(jid):
        """
        Static method to build a gravatar url with the agent's JID

        Args:
          jid (aioxmpp.JID): an XMPP identifier

        Returns:
          str: an URL for the gravatar

        """
        digest = md5(str(jid).encode("utf-8")).hexdigest()
        return "http://www.gravatar.com/avatar/{md5}?d=monsterid".format(md5=digest)

    def submit(self, coro):
        """
        Runs a coroutine in the event loop of the agent.
        this call is not blocking.

        Args:
          coro (coroutine): the coroutine to be run

        Returns:
            asyncio.Future: the future of the coroutine execution

        """
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop)

    def add_behaviour(self, behaviour, template=None):
        """
        Adds and starts a behaviour to the agent.
        If template is not None it is used to match
        new messages and deliver them to the behaviour.

        Args:
          behaviour (spade.behaviour.CyclicBehaviour): the behaviour to be started
          template (spade.template.Template, optional): the template to match messages with (Default value = None)

        """
        behaviour.set_agent(self)
        behaviour.set_template(template)
        self.behaviours.append(behaviour)
        behaviour.start()

    def remove_behaviour(self, behaviour):
        """
        Removes a behaviour from the agent.
        The behaviour is first killed.

        Args:
          behaviour (spade.behaviour.CyclicBehaviour): the behaviour instance to be removed

        """
        if not self.has_behaviour(behaviour):
            raise ValueError("This behaviour is not registered")
        index = self.behaviours.index(behaviour)
        self.behaviours[index].kill()
        self.behaviours.pop(index)

    def has_behaviour(self, behaviour):
        """
        Checks if a behaviour is added to an agent.

        Args:
          behaviour (spade.behaviour.CyclicBehaviour): the behaviour instance to check

        Returns:
          bool: a boolean that indicates wether the behaviour is inside the agent.

        """
        return behaviour in self.behaviours

    def stop(self):
        """ Stops an agent and kills all its behaviours. """
        self.presence.set_unavailable()
        for behav in self.behaviours:
            behav.kill()
        if self.web.server:
            self.web.server.close()
            self.submit(self.web.handler.shutdown(60.0))
        self.submit(self.web.app.shutdown())
        self.submit(self.web.app.cleanup())
        self.aiothread.finalize()
        if self.aiothread.is_alive() and not self.external_loop:
            self.aiothread.loop_exited.wait()
        self._alive.clear()

    def is_alive(self):
        """
        Checks if the agent is alive.

        Returns:
          bool: wheter the agent is alive or not

        """
        return self._alive.is_set()

    def set(self, name, value):
        """
        Stores a knowledge item in the agent knowledge base.

        Args:
          name (str): name of the item
          value (object): value of the item

        """
        self._values[name] = value

    def get(self, name):
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

    def _message_received(self, msg):
        """
        Callback run when an XMPP Message is reveived.
        This callback delivers the message to every behaviour
        that is waiting for it using their templates match.
        the aioxmpp.Message is converted to spade.message.Message

        Args:
          msg (aioxmpp.Messagge): the message just received.

        Returns:
            list(asyncio.Future): a list of futures of the append of the message at each matched behaviour.

        """
        logger.debug(f"Got message: {msg}")

        msg = Message.from_node(msg)
        futures = []
        matched = False
        for behaviour in (x for x in self.behaviours if x.match(msg)):
            futures.append(self.submit(behaviour.enqueue(msg)))
            logger.debug(f"Message enqueued to behaviour: {behaviour}")
            self.traces.append(msg, category=str(behaviour))
            matched = True
        if not matched:
            logger.warning(f"No behaviour matched for message: {msg}")
            self.traces.append(msg)
        return futures


class AioThread(Thread):
    """ The thread that manages the asyncio loop """

    def __init__(self, agent, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.jid = agent.jid
        self.conn_coro = None
        self.stream = None
        self.loop = loop
        self.loop_exited = Event()
        self.loop_exited.clear()

        asyncio.set_event_loop(self.loop)

        self.client = aioxmpp.PresenceManagedClient(agent.jid,
                                                    aioxmpp.make_security_layer(agent.password,
                                                                                no_verify=not agent.verify_security),
                                                    loop=self.loop,
                                                    logger=logging.getLogger(agent.jid.localpart))

    def connect(self):  # pragma: no cover
        """ """
        try:
            self.conn_coro = self.client.connected()
            aenter = type(self.conn_coro).__aenter__(self.conn_coro)
            self.stream = self.loop.run_until_complete(aenter)
            logger.info(f"Agent {str(self.jid)} connected and authenticated.")
        except aiosasl.AuthenticationFailure:
            raise AuthenticationFailure(
                "Could not authenticate the agent. Check user and password or use auto_register=True")

    async def async_connect(self):  # pragma: no cover
        """ """
        try:
            self.conn_coro = self.client.connected()
            aenter = type(self.conn_coro).__aenter__(self.conn_coro)
            self.stream = await aenter
            logger.info(f"Agent {str(self.jid)} connected and authenticated.")
        except aiosasl.AuthenticationFailure:
            raise AuthenticationFailure(
                "Could not authenticate the agent. Check user and password or use auto_register=True")

    def run(self):
        """ """
        if not self.agent.external_loop:
            self.loop_exited.set()
            self.loop.run_forever()
            logger.debug("Loop stopped.")
            self.loop_exited.clear()

    def finalize(self):
        """ """
        if self.agent.is_alive():
            # Disconnect from XMPP server
            self.client.stop()
            aexit = self.conn_coro.__aexit__(*sys.exc_info())
            future = asyncio.run_coroutine_threadsafe(aexit, loop=self.loop)
            try:
                asyncio.wait_for(future, timeout=5)
            except asyncio.TimeoutError:  # pragma: no cover
                logger.error('The client took too long to disconnect, cancelling the task...')
                future.cancel()
            except Exception as e:  # pragma: no cover
                logger.error("Could not disconnect from server: {!r}.".format(e))
            else:
                logger.info("Client disconnected.")
        if not self.agent.external_loop:
            future = self.loop.call_soon_threadsafe(self.loop.stop)
            try:
                asyncio.wait_for(future, timeout=5)
            except asyncio.TimeoutError:  # pragma: no cover
                logger.error('The loop took too long to close...')
                future.cancel()
            except Exception as e:  # pragma: no cover
                logger.error("Exception closing loop: {}".format(e))
            else:
                logger.debug("Loop closed")
