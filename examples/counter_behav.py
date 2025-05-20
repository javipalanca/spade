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
            if self.counter > 5:
                self.kill(exit_code=10)
                return
            await asyncio.sleep(1)

        async def on_end(self):
            print("Behaviour finished with exit code {}.".format(self.exit_code))
            await self.agent.stop()

    async def setup(self):
        print("Agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)


async def main():
    jid1 = input("Agent JID> ")
    passwd1 = getpass.getpass()
    dummy = DummyAgent(jid1, passwd1)
    await dummy.start()

    await wait_until_finished(dummy)
    print("DummyAgent stopped.")


if __name__ == "__main__":
    spade.run(main(), True)
