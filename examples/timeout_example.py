import datetime
import getpass

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, TimeoutBehaviour
from spade.message import Message


class TimeoutSenderAgent(Agent):
    class InformBehav(TimeoutBehaviour):
        async def run(self):
            print(f"TimeoutSenderBehaviour running at {datetime.datetime.now().time()}")
            msg = Message(to=self.get("receiver_jid"))  # Instantiate the message
            msg.body = "Hello World"  # Set the message content

            await self.send(msg)

        async def on_end(self):
            await self.agent.stop()

    async def setup(self):
        print(f"TimeoutSenderAgent started at {datetime.datetime.now().time()}")
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        b = self.InformBehav(start_at=start_at)
        self.add_behaviour(b)


class ReceiverAgent(Agent):
    class RecvBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")
            self.kill()

        async def on_end(self):
            await self.agent.stop()

    async def setup(self):
        b = self.RecvBehav()
        self.add_behaviour(b)


async def main():
    receiver_jid = input("Receiver JID> ")
    passwd = getpass.getpass()
    receiveragent = ReceiverAgent(receiver_jid, passwd)

    sender_jid = input("Sender JID> ")
    passwd = getpass.getpass()
    senderagent = TimeoutSenderAgent(sender_jid, passwd)

    await receiveragent.start(auto_register=True)

    # store receiver_jid in the sender knowledge base
    senderagent.set("receiver_jid", receiver_jid)
    await senderagent.start(auto_register=True)

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main(), True)
