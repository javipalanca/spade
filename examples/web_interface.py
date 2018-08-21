# coding=utf-8
import asyncio
import getpass

from aioxmpp import PresenceType, Presence, JID, PresenceShow
from aioxmpp.roster.xso import Item
import time

from spade import agent, behaviour


class WebAgent(agent.Agent):
    class DummyBehav(behaviour.CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(1)

        async def on_end(self):
            print("Ending behav.")

    def setup(self):
        self.web.start()
        self.add_behaviour(self.DummyBehav())

        self.add_contact("agent0@server", PresenceType.AVAILABLE)
        self.add_contact("agent1@server", PresenceType.AVAILABLE, show=PresenceShow.AWAY)
        self.add_contact("agent2@server", PresenceType.AVAILABLE, show=PresenceShow.DO_NOT_DISTURB)
        self.add_contact("agent3@server", PresenceType.UNAVAILABLE)
        self.add_contact("agent4@server", PresenceType.AVAILABLE, show=PresenceShow.CHAT)
        self.add_contact("agent5@server", PresenceType.UNAVAILABLE)

    def add_contact(self, jid, presence, show=None):
        jid = JID.fromstr(jid)
        item = Item(jid=jid)
        item.approved = True

        self.presence.roster._update_entry(item)

        if show:
            stanza = Presence(from_=jid, type_=presence, show=show)
        else:
            stanza = Presence(from_=jid, type_=presence)
        self.presence.presenceclient.handle_presence(stanza)


agent_jid = input("Agent JID> ")
agent_passwd = getpass.getpass()

a = WebAgent(agent_jid, agent_passwd)
a.web.port = 10000
a.start(auto_register=True)

print("Agent web at {}:{}".format(a.web.hostname, a.web.port))
print(a.jid)
while a.is_alive():
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        a.stop()
