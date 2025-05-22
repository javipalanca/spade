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

        async def run(self):
            msg = await self.receive()
            if msg:
                print("Msg received:", msg)
                reply = msg.make_reply()
                reply.body = msg.body
                await self.send(reply)
            else:
                await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        self.presence.approve_all = True
        self.presence.subscribe(self.human_jid)
        self.presence.on_subscribed = lambda jid: print(jid, "Subscribed")
        self.presence.on_available = lambda jid, stanza: print(jid, "Available")
        b = self.MyBehav()
        self.add_behaviour(b)


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()

    hjid = input("Human JID> ")

    dummy = DummyAgent(jid, passwd)
    dummy.human_jid = hjid
    await dummy.start()
    print("DummyAgent started. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")

    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main(), True)
