import getpass
import time
from sys import getsizeof

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class RecvBehav(OneShotBehaviour):
    async def run(self):
        self.agent.n = 0
        while self.agent.n < self.agent.nmax:
            await self.receive(timeout=1000)
            self.agent.n += 1


class SendBehav(OneShotBehaviour):
    async def run(self):
        msg = Message(to=self.agent.receiver_jid, body=self.agent.body)
        for _ in range(self.agent.nmax):
            await self.send(msg)


class Receiver(Agent):
    def setup(self):
        self.add_behaviour(RecvBehav())


class Sender(Agent):
    def setup(self):
        self.add_behaviour(SendBehav())


def run_experiment(credentials, use_container=True, num_msg=1000, body="0"):
    sender_jid = credentials["sender_jid"]
    sender_passwd = credentials["sender_passwd"]
    recv_jid = credentials["recv_jid"]
    recv_passwd = credentials["recv_passwd"]

    receiver = Receiver(recv_jid, recv_passwd, use_container=use_container)
    sender = Sender(sender_jid, sender_passwd, use_container=use_container)
    sender.receiver_jid = recv_jid
    receiver.n = 0

    receiver.nmax = num_msg
    sender.nmax = num_msg
    sender.body = body

    receiver.start(auto_register=True)
    sender.start()
    print("Go")
    t1 = time.time()
    while receiver.n < num_msg:
        time.sleep(0.1)
    t2 = time.time()

    size = getsizeof(body)

    if use_container:
        print("{} Messages of size {} bytes received w/container: {}".format(receiver.n, size, t2 - t1))
    else:
        print("{} Messages of size {} bytes received wo/container: {}".format(receiver.n, size, t2 - t1))

    sender.stop()
    receiver.stop()


if __name__ == "__main__":
    agent_credentials = {
        "sender_jid": input("SenderAgent JID> "),
        "sender_passwd": getpass.getpass(),
        "recv_jid": input("ReceiverAgent JID> "),
        "recv_passwd": getpass.getpass()
    }

    run_experiment(agent_credentials, use_container=True)
    run_experiment(agent_credentials, use_container=False)

    run_experiment(agent_credentials, use_container=True, num_msg=10000)
    run_experiment(agent_credentials, use_container=False, num_msg=10000)

    run_experiment(agent_credentials, use_container=True, body="0" * 1000)
    run_experiment(agent_credentials, use_container=False, body="0" * 1000)

    run_experiment(agent_credentials, use_container=True, num_msg=10000, body="0" * 1000)
    run_experiment(agent_credentials, use_container=False, num_msg=10000, body="0" * 1000)

    run_experiment(agent_credentials, use_container=True, num_msg=10000, body="0" * 100000)

    run_experiment(agent_credentials, use_container=True, num_msg=100000, body="0" * 100000)
