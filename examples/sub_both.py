import asyncio
import getpass

import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class Sub1Agent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")

        async def run(self):
            await asyncio.sleep(10)
            print(self.agent.presence.get_contacts())

    async def setup(self):
        print("Agent starting . . .")
        self.presence.subscribe(self.sub2)
        self.presence.on_subscribed = lambda jid: print(jid, "Subscribed")
        self.presence.on_available = lambda jid, info, last: print(jid, "Available")
        self.presence.on_subscribe = self.approve
        # self.presence.approve_all = True
        b = self.MyBehav()
        self.add_behaviour(b)

    def approve(self, jid):
        print("Subscription request from", jid)
        self.presence.approve_subscription(jid)


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()

    hjid = input("Human JID> ")
    passwd = getpass.getpass()

    dummy = Sub1Agent(jid, passwd)
    dummy.sub2 = hjid

    dummy2 = Sub1Agent(hjid, passwd)
    dummy2.sub2 = jid

    await dummy.start()
    await dummy2.start()
    print("DummyAgent started. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")

    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main(), True)
