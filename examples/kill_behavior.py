import getpass
import time
import asyncio
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
            if self.counter > 3:
                self.kill(exit_code=10)
                return
            await asyncio.sleep(1)

        async def on_end(self):
            print("Behaviour finished with exit code {}.".format(self.exit_code))

    async def setup(self):
        print("Agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)


if __name__ == "__main__":
    jid = input("JID> ")
    passwd = getpass.getpass()

    dummy = DummyAgent(jid, passwd)
    future = dummy.start()
    future.result()  # Wait until the start method is finished

    # wait until user interrupts with ctrl+C
    while not dummy.my_behav.is_killed():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    dummy.stop()
