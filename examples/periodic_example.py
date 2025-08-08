import getpass
from datetime import datetime, timedelta

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message


class PeriodicSenderAgent(Agent):
    class InformBehav(PeriodicBehaviour):
        async def run(self):
            print(f"PeriodicSenderBehav at {datetime.now().time()}: {self.counter}")
            msg = Message(to=self.get("receiver_jid"))  # Instantiate the message
            msg.body = "Hello World"  # Set the message content

            await self.send(msg)
            print("Message sent!")

            if self.counter == 5:
                self.kill()
            self.counter += 1

        async def on_end(self):
            # stop agent from behaviour
            await self.agent.stop()

        async def on_start(self):
            self.counter = 0

    async def setup(self):
        print(f"PeriodicSenderAgent started at {datetime.now().time()}")
        start_at = datetime.now() + timedelta(seconds=5)
        b = self.InformBehav(period=2, start_at=start_at)
        self.add_behaviour(b)


class ReceiverAgent(Agent):
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print("RecvBehav running")
            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")
                self.kill()

        async def on_end(self):
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        self.add_behaviour(b)


async def main():
    receiver_jid = input("Receiver JID> ")
    passwd = getpass.getpass()
    receiveragent = ReceiverAgent(receiver_jid, passwd)

    sender_jid = input("Sender JID> ")
    passwd = getpass.getpass()
    senderagent = PeriodicSenderAgent(sender_jid, passwd)

    await receiveragent.start(auto_register=True)

    # store receiver_jid in the sender knowledge base
    senderagent.set("receiver_jid", receiver_jid)
    await senderagent.start(auto_register=True)

    await spade.wait_until_finished(senderagent)

    await receiveragent.stop()
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main(), True)
