=====================
Presence Notification
=====================

One of the most differentiating features of SPADE agents is their ability to maintain a roster or list of contacts
(friends) and to receive notifications in real time about their contacts. This is a feature inherited from instant
messaging technology and that, thanks to XMPP, SPADE powers to the maximum for its agents.

Presence Manager
----------------

Every SPADE agent has a property to manage its presence. This manager is called ``presence`` and implements all the
methods and attributes to manage an agent's presence notification.

A presence object encapsulates its information in a ``PresenceInfo`` class that contains four main attributes:
**type**, **show**, **status** and **priority**. These attributes work together to provide a complete representation
of an agent's presence state. Let's see every one of them:

State
^^^^^

The state of a presence message shows if the agent is **Available** or **Unavailable**. This means that the agent is
connected to an XMPP server or not. This is very useful to know, before contacting an agent, if it is available to
receive a message in real time or not.

The state is now managed through the ``PresenceType`` enumeration which can have the following values:

    - ``PresenceType.AVAILABLE``: The agent is connected and can receive messages
    - ``PresenceType.UNAVAILABLE``: The agent is disconnected or not able to receive messages

Besides, the *State* has also an attribute to give additional information about *how available* the contact is. This is
the **Show** attribute. The *Show* attribute is managed through the ``PresenceShow`` enumeration and can take the following values:

    - ``PresenceShow.CHAT``: The entity or resource is actively interested in chatting (i.e. receiving messages).
    - ``PresenceShow.AWAY``: The entity or resource is temporarily away, however it can receive messages (they will probably be attended later)
    - ``PresenceShow.EXTENDED_AWAY``: The entity or resource is away for an extended period (xa = "*eXtended Away*").
    - ``PresenceShow.DND``: The entity or resource is busy (dnd = "*Do Not Disturb*").
    - ``PresenceShow.NONE``: Signifies absence of the *Show* element. Used for unavailable states.


An agent can set its availability and show property::

    agent.presence.set_presence(presence_type=PresenceType.AVAILABLE, show=PresenceShow.CHAT)


.. warning:: If you set your presence to *unavailable* the only possible show state is ``PresenceShow.NONE``.


A short method to set *unavailability* is::

    agent.presence.set_unavailable()


To get your presence state::

    presence_info = agent.presence.get_presence()  # Gets your current presence information

    agent.presence.is_available()  # Returns a boolean to report whether the agent is available or not

    current_show = agent.presence.get_show()  # Gets your current PresenceShow info


.. tip:: If no *Show* element is provided, the entity is assumed to be online and available with ``PresenceShow.NONE``.

Status
^^^^^^

The status is used to set a textual status to your presence information. It is used to explain with natural language
your current status which is broadcasted when the client connects and when the presence is re-emitted.

An agent can get its status as follows::

    >> agent.presence.get_status()
    "Working..."

The status can be set when defining a new presence::

    agent.presence.set_presence(
        presence_type=PresenceType.AVAILABLE,
        show=PresenceShow.CHAT,
        status="Working on SPADE agents"
    )

.. note::
    In this new version the status is managed as a simple string value, making it more straightforward
    to set and retrieve status information.

Priority
^^^^^^^^

Since an agent (and indeed any XMPP user) can have multiple connections to an XMPP server, it can set the priority of
each of those connections to establish the level of each one. The value must be an integer between -128 and +127.



Setting the Presence
^^^^^^^^^^^^^^^^^^^^

There is a method that can be used to set all presence attributes. Since they are all optional, you can change any
of the attribute values with every call::

    agent.presence.set_presence(
                                 presence_type=PresenceType.AVAILABLE,  # set availability
                                 show=PresenceShow.CHAT,  # show status
                                 status="Lunch",  # status message
                                 priority=2  # connection priority
                                )

Availability handlers
---------------------
To get notified when a contact gets available or unavailable you can override the ``on_available`` and ``on_unavailable``
handlers. These handlers now receive the peer jid of the contact, the current presence information, and the last known
presence state::

    def my_on_available_handler(peer_jid, presence_info, last_presence):
        print(f"My friend {peer_jid} is now {presence_info.show.value}")
        if last_presence:
            print(f"Previous state was: {last_presence.show.value}")

     agent.presence.on_available = my_on_available_handler

Contact List
------------

Every contact to whom you are subscribed to appears in your *contact list*. You can use the ``get_contacts()`` method to
get the full list of your contacts. This method returns a ``dict`` where the keys are the ``JID`` of your contacts and the
values are ``Contact`` objects that contain all the information about each contact (presence info, name, subscription status,
groups, etc.). The contact's current presence is managed through the ``PresenceInfo`` class.

Example::

    >>> contacts = agent.presence.get_contacts()
    >>> contacts[myfriend_jid]
    Contact(
        JID: my_friend@server.com,
        Name: My Friend,
        Presence: PresenceInfo(Type: PresenceType.AVAILABLE, Show: PresenceShow.CHAT, Status: "Working", Priority: 10)
    )

You can also get a specific contact using::

    contact = agent.presence.get_contact("friend@server.com")

.. warning:: An empty contact list will return an empty dictionary.

.. note:: The Contact class provides helper methods like ``is_available()`` and ``is_subscribed()`` to easily check contact status.


Subscribing and unsubscribing to contacts
-----------------------------------------

To subscribe and unsubscribe to/from a contact you have to send a special presence message asking for that subscription.
SPADE helps you by providing some methods that send these special messages::

    # Send a subscription request to a peer_jid
    agent.presence.subscribe(peer_jid)

    # Send an unsubscribe request to a peer_jid
    agent.presence.unsubscribe(peer_jid)

    # Approve a subscription request
    agent.presence.approve_subscription(peer_jid)

Subscription handlers
^^^^^^^^^^^^^^^^^^^^^

The way you have to get notified when someone wants to subscribe/unsubscribe to you or when you want to get notified if
a subscription/unsubscription process has succeed is by means of handlers.
There are four handlers that you can override to manage these kind of messages: ``on_subscribe``, ``on_unsubscribe``,
``on_subscribed`` and ``on_unsubscribed``::


    def my_on_subscribe_callback(peer_jid):
        if i_want_to_approve_request:
            self.presence.approve_subscription(peer_jid)

    agent.presence.on_subscribe = my_on_subscribe_callback



.. note:: In the previous example you can see also how to approve a subscription request by using the ``approve_subscription`` method.

.. tip:: If you want to automatically approve all subscription requests you can set the ``presence.approve_all`` flag to ``True``.

Example
-------

This is an example that shows in a practical way the presence module::

    import getpass
    import asyncio

    import spade
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.presence import PresenceType, PresenceShow, PresenceInfo


    class Agent1(Agent):
        async def setup(self):
            print(f"Agent {self.name} running")
            self.add_behaviour(self.Behav1())

        class Behav1(OneShotBehaviour):
            def on_available(self, peer_jid, presence_info, last_presence):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} is {presence_info.show.value}")

            def on_subscribed(self, peer_jid):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} has accepted the subscription")
                contacts = self.agent.presence.get_contacts()
                print(f"[{self.agent.name}] Contacts List: {contacts}")

            def on_subscribe(self, peer_jid):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} asked for subscription. Let's approve it")
                self.presence.approve_subscription(peer_jid)

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available

                self.presence.set_presence(
                    presence_type=PresenceType.AVAILABLE,
                    show=PresenceShow.CHAT,
                    status="Ready to chat"
                )
                self.presence.subscribe(self.agent.jid2)


    class Agent2(Agent):
        async def setup(self):
            print(f"Agent {self.name} running")
            self.add_behaviour(self.Behav2())

        class Behav2(OneShotBehaviour):
            def on_available(self, peer_jid, presence_info, last_presence):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} is {presence_info.show.value}")

            def on_subscribed(self, peer_jid):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} has accepted the subscription")
                contacts = self.agent.presence.get_contacts()
                print(f"[{self.agent.name}] Contacts List: {contacts}")

            def on_subscribe(self, peer_jid):
                print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} asked for subscription. Let's approve it")
                self.presence.approve_subscription(peer_jid)
                self.presence.subscribe(peer_jid)

            async def run(self):
                self.presence.set_presence(
                    presence_type=PresenceType.AVAILABLE,
                    show=PresenceShow.CHAT,
                    status="Ready to chat"
                )
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available


    async def main():
        jid1 = input("Agent1 JID> ")
        passwd1 = getpass.getpass()

        jid2 = input("Agent2 JID> ")
        passwd2 = getpass.getpass()

        agent2 = Agent2(jid2, passwd2)
        agent1 = Agent1(jid1, passwd1)
        agent1.jid2 = jid2
        agent2.jid1 = jid1
        await agent2.start()
        await agent1.start()

        while True:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        await agent1.stop()
        await agent2.stop()


    if __name__ == "__main__":
        spade.run(main())
