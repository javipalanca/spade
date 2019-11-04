import getpass
import time
from sys import getsizeof

from spade import quit_spade
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
    async def setup(self):
        self.add_behaviour(RecvBehav())


class Sender(Agent):
    async def setup(self):
        self.add_behaviour(SendBehav())


def run_experiment(credentials, num_msg=1000, body="0"):
    sender_jid = credentials["sender_jid"]
    sender_passwd = credentials["sender_passwd"]
    recv_jid = credentials["recv_jid"]
    recv_passwd = credentials["recv_passwd"]

    receiver = Receiver(recv_jid, recv_passwd)
    sender = Sender(sender_jid, sender_passwd)
    sender.receiver_jid = recv_jid
    receiver.n = 0

    receiver.nmax = num_msg
    sender.nmax = num_msg
    sender.body = body

    future = receiver.start(auto_register=True)
    future.result()
    future = sender.start(auto_register=True)
    future.result()
    print("Go")
    t1 = time.time()
    while receiver.n < num_msg:
        time.sleep(0.1)
    t2 = time.time()

    size = getsizeof(body)

    print("{} Messages of size {} bytes received w/container: {}".format(receiver.n, size, t2 - t1))

    sender.stop()
    receiver.stop()


if __name__ == "__main__":
    agent_credentials = {
        "sender_jid": input("SenderAgent JID> "),
        "sender_passwd": getpass.getpass(),
        "recv_jid": input("ReceiverAgent JID> "),
        "recv_passwd": getpass.getpass()
    }

    run_experiment(agent_credentials)

    run_experiment(agent_credentials, num_msg=10000)

    run_experiment(agent_credentials, body="0" * 1000)

    run_experiment(agent_credentials, num_msg=10000, body="0" * 1000)

    run_experiment(agent_credentials, num_msg=10000, body="0" * 100000)

    run_experiment(agent_credentials, num_msg=100000, body="0" * 100000)

    quit_spade()
