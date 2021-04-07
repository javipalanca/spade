# coding=utf-8
import asyncio
import datetime
import random
import time

import aioxmpp
import click
from aioxmpp import PresenceType, Presence, JID, PresenceShow, MessageType
from aioxmpp.roster.xso import Item

from spade import agent, behaviour
from spade.behaviour import State
from spade.message import Message
from spade.template import Template


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
        def setup(self):
            class S(State):
                async def run(self):
                    await asyncio.sleep(1)

            self.add_state("S 1", S(), initial=True)
            self.add_state("S 2", S())
            self.add_state("S 3", S())
            self.add_state("S 4", S())
            self.add_state("S 5", S())
            self.add_transition("S 1", "S 2")
            self.add_transition("S 2", "S 1")
            self.add_transition("S 1", "S 3")
            self.add_transition("S 3", "S 5")
            self.add_transition("S 2", "S 4")
            self.add_transition("S 4", "S 5")

    def setup(self):
        self.web.start(templates_path="examples")
        template1 = Template(sender="agent0@fake_server")
        template2 = Template(sender="agent1@fake_server")
        template3 = Template(sender="agent2@fake_server")
        template4 = Template(sender="agent3@fake_server")

        # Create some dummy behaviours
        dummybehav = self.DummyBehav()
        self.add_behaviour(dummybehav, template=template1)
        periodbehav = self.DummyPeriodBehav(period=12.7)
        self.add_behaviour(periodbehav, template=template2)
        timeoutbehav = self.DummyTimeoutBehav(start_at=datetime.datetime.now())
        self.add_behaviour(timeoutbehav, template=template3)
        fsm_behav = self.DummyFSMBehav()
        self.add_behaviour(fsm_behav, template=template4)
        behavs = [dummybehav, periodbehav, timeoutbehav, fsm_behav]

        # Create some fake contacts
        self.add_fake_contact("agent0@fake_server", PresenceType.AVAILABLE)
        self.add_fake_contact(
            "agent1@fake_server", PresenceType.AVAILABLE, show=PresenceShow.AWAY
        )
        self.add_fake_contact(
            "agent2@fake_server",
            PresenceType.AVAILABLE,
            show=PresenceShow.DO_NOT_DISTURB,
        )
        self.add_fake_contact("agent3@fake_server", PresenceType.UNAVAILABLE)
        self.add_fake_contact(
            "agent4@fake_server", PresenceType.AVAILABLE, show=PresenceShow.CHAT
        )
        self.add_fake_contact("agent5@fake_server", PresenceType.UNAVAILABLE)

        # Send and Receive some fake messages
        self.traces.reset()
        for i in range(20):
            number = random.randint(0, 3)
            from_ = JID.fromstr("agent{}@fake_server".format(number))
            msg = aioxmpp.Message(from_=from_, to=self.jid, type_=MessageType.CHAT)
            msg.body[None] = "Hello from {}! This is a long message.".format(
                from_.localpart
            )
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
        jid = JID.fromstr(jid)
        item = Item(jid=jid)
        item.approved = True

        self.presence.roster._update_entry(item)

        if show:
            stanza = Presence(from_=jid, type_=presence, show=show)
        else:
            stanza = Presence(from_=jid, type_=presence)
        self.presence.presenceclient.handle_presence(stanza)


@click.command()
@click.option("--jid", prompt="Agent JID> ")
@click.option("--pwd", prompt="Password>", hide_input=True)
@click.option("--port", default=10000)
def run(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port

    async def hello(request):
        return {"number": 42}

    a.web.add_get("/hello", hello, "hello.html")
    a.start(auto_register=True)

    print("Agent web at {}:{}".format(a.web.hostname, a.web.port))
    print(a.jid)
    while a.is_alive():
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            a.stop()


if __name__ == "__main__":
    run()
