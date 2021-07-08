from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class AgentExample(Agent):
    async def setup(self):
        print(f"{self.jid} created.")


class CreateBehav(OneShotBehaviour):
    async def run(self):
        agent2 = AgentExample("agent2_example@your_xmpp_server", "fake_password")
        # This start is inside an async def, so it must be awaited
        await agent2.start(auto_register=True)


if __name__ == "__main__":
    agent1 = AgentExample("agent1_example@your_xmpp_server", "fake_password")
    behav = CreateBehav()
    agent1.add_behaviour(behav)
    # This start is in a synchronous piece of code, so it must NOT be awaited
    future = agent1.start(auto_register=True)
    future.result()

    # wait until the behaviour is finished to quit spade.
    behav.join()
    quit_spade()
