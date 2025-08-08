import asyncio
import getpass

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class DummyAgent(Agent):
    class LongBehav(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(5)
            print("Long Behaviour has finished")

    class WaitingBehav(OneShotBehaviour):
        async def run(self):
            await self.agent.behav.join()  # this join must be awaited
            print("Waiting Behaviour has finished")

    async def setup(self):
        print("Agent starting . . .")
        self.behav = self.LongBehav()
        self.add_behaviour(self.behav)
        self.behav2 = self.WaitingBehav()
        self.add_behaviour(self.behav2)


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()

    dummy = DummyAgent(jid, passwd)
    await dummy.start()

    await dummy.behav2.join()

    print("Stopping agent.")
    await dummy.stop()


if __name__ == "__main__":
    spade.run(main(), True)
