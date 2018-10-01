from singletonify import singleton


@singleton()
class Container(object):
    def __init__(self):
        self.__agents = {}

    def register(self, agent):
        self.__agents[str(agent.jid)] = agent
        agent.set_container(self)

    def send(self, msg, behaviour):
        to = str(msg.to)
        if to in self.__agents:
            self.__agents[to].dispatch(msg)
        else:
            behaviour._xmpp_send(msg)
