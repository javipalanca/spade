=====================
Presence Notification
=====================

One of the most differentiating features of SPADE agents is their ability to maintain a roster or list of contacts
(friends) and to receive notifications in real time about their contacts. This is a feature inherited from instant
messaging technology and that, thanks to XMPP, SPADE powers to the maximum for its agents.

Presence Manager
----------------

Every SPADE agent has a property to manage its presence. This manager is called ``presence`` and has all the methods and
attributes to manage an agent's presence notification.

A presence object has three attributes: the state, the status and the priority. Let's see each one of them:

State
^^^^^

The state of a presence message shows if the agent is **Available** or **Unavailable**. This means that the agent is
connected to the network or not. This is very useful to know, before contacting an agent if it is available to receive
the message in real time or not. This is a boolean attribute.
Besides, the *State* has also an attribute to give additional information about *how available* the contact is. This is
the **Show** attribute. It is used to report information about the availability. The *Show* attribute belongs to the
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

    agent.presence.set_presence(state=PresenceState(True, PresenceShow.CHAT), status="Lunch", priority=2)



