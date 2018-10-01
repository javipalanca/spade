from singletonify import singleton


@singleton()
class Container(object):
    def __init__(self):
        self.__agents = {}

    def reset(self):
        self.__agents = {}

    def register(self, agent):
        self.__agents[str(agent.jid)] = agent
        agent.set_container(self)

    def has_agent(self, jid):
        return jid in self.__agents

    def get_agent(self, jid):
        return self.__agents[jid]

    async def send(self, msg, behaviour):
        to = str(msg.to)
        if to in self.__agents:
            self.__agents[to].dispatch(msg)
        else:
            await behaviour._xmpp_send(msg)
