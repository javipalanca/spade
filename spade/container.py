from singletonify import singleton


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
