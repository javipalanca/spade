import asyncio
import getpass

import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class DummyAgent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counter = 0

        async def run(self):
            print("Counter: {}".format(self.counter))
            self.counter += 1
            await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()

    dummy = DummyAgent(jid, passwd)
    await dummy.start()
    print("DummyAgent started. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")

    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main())
