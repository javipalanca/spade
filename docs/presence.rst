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

A presence object has three attributes: the **state**, the **status** and the **priority**. Let's see every one of them:

State
^^^^^

The state of a presence message shows if the agent is **Available** or **Unavailable**. This means that the agent is
connected to an XMPP server or not. This is very useful to know, before contacting an agent, if it is available to
receive a message in real time or not. The availability state is a boolean attribute.

Besides, the *State* has also an attribute to give additional information about *how available* the contact is. This is
the **Show** attribute. The *Show* attribute belongs to the
class ``aioxmpp.PresenceShow`` and can take the following values:

    - ``PresenceShow.CHAT``: The entity or resource is actively interested in chatting (i.e. receiving messages).
    - ``PresenceShow.AWAY``: The entity or resource is temporarily away, however it can receive messages (they will probably be attended later)
    - ``PresenceShow.XA``: The entity or resource is away for an extended period (xa = "*eXtended Away*").
    - ``PresenceShow.DND``: The entity or resource is busy (dnd = "*Do Not Disturb*").
    - ``PresenceShow.NONE``: Signifies absence of the *Show* element. Used for unavailable states.


An agent can set its availability and show property::

    agent.presence.set_available(availability=True, show=PresenceShow.CHAT)


.. warning:: If you set your presence to *unavailable* the only possible show state is ``PresenceShow.NONE``.


A short method to set *unavailability* is::

    agent.presence.set_unavailable()



To get your presence state::

    my_state = agent.presence.state  # Gets your current PresenceState instance.

    agent.presence.is_available()  # Returns a boolean to report wether the agent is available or not

    my_show = agent.presence.state.show  # Gets your current PresenceShow info.



.. tip:: If no *Show* element is provided, the entity is assumed to be online and available.

Status
^^^^^^

The status is used to set a textual status to your presence information. It is used to explain with natural language
your current status which is broadcasted when the client connects and when the presence is re-emitted.

An agent can get its status as follows::

    >> agent.presence.status
    {None: "Working..."}


.. warning::
    It should be noted that the status is returned as a dict with a ``None`` key. This is because the status supports
    different languages. If you set the status as a string it is set as the default status (and stored with the key
    ``None``. If you want to set the status in different languages you can specify it using the keys::

        >> agent.presence.status
        {
          None: "Working...",
          "es": "Trabajando...",
          "fr": "Travailler..."
        }



Priority
^^^^^^^^

Since an agent (and indeed any XMPP user) can have multiple connections to an XMPP server, it can set the priority of
each of those connections to establish the level of each one. The value must be an integer between -128 and +127.


Setting the Presence
^^^^^^^^^^^^^^^^^^^^

There is a method that can be used to set the three presence attributes. Since they are all optional, you can change any
of the attribute values with every call::

    agent.presence.set_presence(
                                 state=PresenceState(True, PresenceShow.CHAT),  # available and interested in chatting
                                 status="Lunch",
                                 priority=2
                                )



Availability handlers
---------------------
To get notified when a contact gets available or unavailable you can override the ``on_available`` and ``on_unavailable``
handlers. As you can see in the next example, these handlers receive the peer jid of the contact and the *stanza* of
the XMPP Presence message (class ``aioxmpp.Presence``) which contains all its presence information (availability, show,
state, priority, ...)::

    def my_on_available_handler(peer_jid, stanza):
        print(f"My friend {peer_jid} is now available with show {stanza.show}")

    agent.presence.on_available =  my_on_available_handler


Contact List
------------

Every contact to whom you are subscribed to appears in your *contact list*. You can use the ``get_contacts()`` method to
get the full list of your contacts. This method returns a ``dict`` where the keys are the ``JID`` of your contacts and the
values are an dict that show the information you have about each of your contacts (presence, name, approved,
groups, ask, subscription, ...). Note that the "presence" value is an ``aioxmpp.Presence`` object with the latest updated
information about the contact's presence.

Example::

    >>> contacts = agent.presence.get_contacts()
    >>> contacts[myfriend_jid]
          {
            'presence': Presence(type_=PresenceType.AVAILABLE),
            'subscription': 'both',
            'name': 'My Friend',
            'approved': True
          }



.. warning:: An empty contact list will return an empty dictionary.

Subscribing and unsubscribing to contacts
-----------------------------------------

To subscribe and unsubscribe to/from a contact you have to send a special presence message asking for that subscription.
SPADE helps you by providing some methods that send these special messages::


    # Send a subscription request to a peer_jid
    agent.presence.subscribe(peer_jid)

    # Send an unsubscribe request to a peer_jid
    agent.presence.unsubscribe(peer_jid)


Subscription handlers
^^^^^^^^^^^^^^^^^^^^^

The way you have to get notified when someone wants to subscribe/unsubscribe to you or when you want to get notified if
a subscription/unsubscription process has succeed is by means of handlers.
There are four handlers that you can override to manage these kind of messages: ``on_subscribe``, ``on_unsubscribe``,
``on_subscribed`` and ``on_unsubscribed``::


    def my_on_subscribe_callback(peer_jid):
        if i_want_to_approve_request:
            self.approve(peer_jid)

    agent.presence.on_subscribe = my_on_subscribe_callback


.. note:: In the previous example you can see also how to approve a subscription request by using the ``approve`` method.

.. tip:: If you want to automatically approve all subscription requests you can set the ``approve_all`` flag to ``True``.


Example
-------

This is an example that shows in a practical way the presence module::

    import time
    import getpass

    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour


    class Agent1(Agent):
        async def setup(self):
            print("Agent {} running".format(self.name))
            self.add_behaviour(self.Behav1())

        class Behav1(OneShotBehaviour):
            def on_available(self, jid, stanza):
                print("[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0]))

            def on_subscribed(self, jid):
                print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
                print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))

            def on_subscribe(self, jid):
                print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
                self.presence.approve(jid)

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available

                self.presence.set_available()
                self.presence.subscribe(self.agent.jid2)


    class Agent2(Agent):
        async def setup(self):
            print("Agent {} running".format(self.name))
            self.add_behaviour(self.Behav2())

        class Behav2(OneShotBehaviour):
            def on_available(self, jid, stanza):
                print("[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0]))

            def on_subscribed(self, jid):
                print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
                print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))

            def on_subscribe(self, jid):
                print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
                self.presence.approve(jid)
                self.presence.subscribe(jid)

            async def run(self):
                self.presence.set_available()
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available


    if __name__ == "__main__":

        jid1 = input("Agent1 JID> ")
        passwd1 = getpass.getpass()

        jid2 = input("Agent2 JID> ")
        passwd2 = getpass.getpass()

        agent2 = Agent2(jid2, passwd2)
        agent1 = Agent1(jid1, passwd1)
        agent1.jid2 = jid2
        agent2.jid1 = jid1
        agent2.start()
        agent1.start()

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        agent1.stop()
        agent2.stop()

