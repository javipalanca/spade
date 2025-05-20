import getpass

from slixmpp import JID

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class AgentExample(Agent):
    async def setup(self):
        print(f"{self.jid} created.")


class CreateBehav(OneShotBehaviour):
    async def run(self):
        agent2 = AgentExample(f"agent2_example@{self.server}", "fake_password")
        # This start is inside an async def, so it must be awaited
        await agent2.start(auto_register=True)


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()
    agent1 = AgentExample(jid, passwd)
    behav = CreateBehav()
    behav.server = JID(jid).domain
    agent1.add_behaviour(behav)
    # This start is in a synchronous piece of code, so it must NOT be awaited
    await agent1.start(auto_register=True)

    # wait until the behaviour is finished to quit spade.
    await behav.join()
    await agent1.stop()

    await spade.wait_until_finished(agent1)


if __name__ == "__main__":
    spade.run(main(), True)
