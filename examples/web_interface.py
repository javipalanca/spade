# coding=utf-8
import asyncio
import datetime
import random

import click
import slixmpp
from slixmpp import JID

import spade
from spade import agent, behaviour
from spade.behaviour import State
from spade.message import Message
from spade.template import Template
from spade.presence import PresenceShow, PresenceType, PresenceInfo, Contact


class WebAgent(agent.Agent):
    class DummyBehav(behaviour.CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(1)

        async def on_end(self):
            print("Ending behav.")

    class DummyPeriodBehav(behaviour.PeriodicBehaviour):
        async def run(self):
            await asyncio.sleep(1)

    class DummyTimeoutBehav(behaviour.TimeoutBehaviour):
        async def run(self):
            await asyncio.sleep(1)

    class DummyFSMBehav(behaviour.FSMBehaviour):
        async def on_start(self) -> None:
            print(f"FSM starting at initial state {self.current_state}")

        async def on_end(self) -> None:
            print(f"FSM finished at state {self.current_state}")

        def setup_states(self):
            class S(State):
                async def run(self):
                    await asyncio.sleep(100)

            print("Preparing FSM")
            self.add_state("S1", S(), initial=True)
            self.add_state("S2", S())
            self.add_state("S3", S())
            self.add_state("S4", S())
            self.add_state("S5", S())
            self.add_transition("S1", "S2")
            self.add_transition("S2", "S1")
            self.add_transition("S1", "S3")
            self.add_transition("S3", "S5")
            self.add_transition("S2", "S4")
            self.add_transition("S4", "S5")
            print("FSM prepared")

    async def setup(self):
        self.web.start(templates_path="examples")
        template1 = Template(sender="agent0@fake.server")
        template2 = Template(sender="agent1@fake.server")
        template3 = Template(sender="agent2@fake.server")
        template4 = Template(sender="agent3@fake.server")

        # Create some dummy behaviours
        dummybehav = self.DummyBehav()
        self.add_behaviour(dummybehav, template=template1)
        periodbehav = self.DummyPeriodBehav(period=12.7)
        self.add_behaviour(periodbehav, template=template2)
        timeoutbehav = self.DummyTimeoutBehav(start_at=datetime.datetime.now())
        self.add_behaviour(timeoutbehav, template=template3)
        fsm_behav = self.DummyFSMBehav()
        fsm_behav.setup_states()
        self.add_behaviour(fsm_behav, template=template4)
        behavs = [dummybehav, periodbehav, timeoutbehav, fsm_behav]

        # Create some fake contacts
        self.add_fake_contact("agent0@fake.server", PresenceType.AVAILABLE)
        self.add_fake_contact(
            "agent1@fake.server", PresenceType.AVAILABLE, show=PresenceShow.AWAY
        )
        self.add_fake_contact(
            "agent2@fake.server",
            PresenceType.AVAILABLE,
            show=PresenceShow.DND,
        )
        self.add_fake_contact("agent3@fake.server", PresenceType.UNAVAILABLE)
        self.add_fake_contact(
            "agent4@fake.server", PresenceType.AVAILABLE, show=PresenceShow.CHAT
        )
        self.add_fake_contact("agent5@fake.server", PresenceType.UNAVAILABLE)
        self.add_fake_contact(
            "agent6@fake.server",
            PresenceType.AVAILABLE,
            show=PresenceShow.EXTENDED_AWAY,
        )

        # Send and Receive some fake messages
        self.traces.reset()
        for i in range(20):
            number = random.randint(0, 3)
            from_ = JID("agent{}@fake.server".format(number))
            msg = slixmpp.Message(sfrom=from_, sto=self.jid)
            msg.chat()
            msg["body"] = "Hello from {}! This is a long message.".format(from_.local)
            msg = Message.from_node(msg)
            msg.metadata = {"performative": "inform", "acl-representation": "xml"}
            msg = msg.prepare()
            self._message_received(msg=msg)
            msg = Message(
                sender=str(self.jid), to=str(from_), body="This is my answer."
            )
            msg.sent = True
            self.traces.append(msg, category=str(behavs[number]))

    def add_fake_contact(self, jid, presence, show=None):
        jid = JID(jid)

        contact = Contact(
            jid.bare, name=jid.bare, subscription="both", ask="", groups=[]
        )

        pinfo = PresenceInfo(presence, show=show)
        contact.update_presence("resource", pinfo)

        self.presence.contacts[jid.bare] = contact


async def main(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port

    async def hello(request):
        return {"number": 42}

    a.web.add_get("/hello", hello, "hello.html")

    await a.start(auto_register=True)

    print("Agent web at {}:{}".format(a.web.hostname, a.web.port))
    await spade.wait_until_finished(a)


@click.command()
@click.option("--jid", prompt="Agent JID> ")
@click.option("--pwd", prompt="Password>", hide_input=True)
@click.option("--port", default=10000)
def run(jid, pwd, port):
    spade.run(main(jid, pwd, port))


if __name__ == "__main__":
    run()
