import getpass

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template


class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to=self.agent.recv_jid)  # Instantiate the message
            msg.set_metadata(
                "performative", "inform"
            )  # Set the "inform" FIPA performative
            msg.body = "Hello World {}".format(
                self.agent.recv_jid
            )  # Set the message content

            await self.send(msg)
            print("Message sent!")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)

    def __init__(self, recv_jid, *args, **kwargs):
        self.recv_jid = recv_jid
        super().__init__(*args, **kwargs)


class ReceiverAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


async def main():
    sender_jid = input("SenderAgent JID> ")
    sender_passwd = getpass.getpass()

    recv_jid = input("ReceiverAgent JID> ")
    recv_passwd = getpass.getpass()

    receiveragent = ReceiverAgent(recv_jid, recv_passwd)
    senderagent = SenderAgent(recv_jid, sender_jid, sender_passwd)
    await spade.start_agents([receiveragent, senderagent])
    print("Agents started")

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main(), True)
