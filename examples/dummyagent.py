import getpass

import spade


class DummyAgent(spade.agent.Agent):
    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))


async def main():
    jid = input("JID> ")
    passwd = getpass.getpass()
    dummy = DummyAgent(jid, passwd)
    await dummy.start()


if __name__ == "__main__":
    spade.run(main(), True)
