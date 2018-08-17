=====================
The SPADE agent model
=====================

The Agent Model is basically composed of a connection mechanism to the platform, a message dispatcher, and a set of
different behaviours that the dispatcher gives the messages to. Every agent needs an identifier called Jabber ID a.k.a.
JID and a valid password to establish a connection with the XMPP server.

The JID (composed by a username, an @, and a server domain) will be the name that identifies an agent in the platform,
e.g. *myagent@myprovider.com*.

Connection to the platform
---------------------------
Communications in SPADE are handled internally by means of the `XMPP protocol <http://www.xmpp.org>`_.
This protocol has a mechanism to register and authenticate users against an XMPP server.

.. Since the SPADE platform includes an XMPP server component, SPADE agents use the aforementioned mechanism to register in the server as XMPP clients.

After a succesful register, each agent holds an open and persistent XMPP stream of communications with the platform.
This process is automatically triggered as part of the agent registration process.

The message dispatcher
----------------------

Each SPADE agent has an internal message dispatcher component. This message dispatcher acts as a mailman: when a message
for the agent arrives, it places it in the correct "mailbox" (more about that later); and when the agent needs to send a
message, the message dispatcher does the job, putting it in the communication stream. The message dispatching is done
automatically by the SPADE agent library whenever a new message arrives or is to be sent.

The behaviours
--------------

An agent can run serveral behaviours simultaneously. A behaviour is a task that an agent can execute using repeating
patterns. SPADE provides some predefined behaviour types: Cyclic, One-Shot, Periodic, Time-Out and Finite State Machine.
Those behaviour types help to implement the different tasks that an agent can perform. The kind of behaviours supported
by a SPADE agent are the following:

* Cyclic and Periodic behaviours are useful for performing repetitive tasks.

* One-Shot and Time-Out behaviours can be used to perform casual tasks.

* The Finite State Machine allows more complex behaviours to be built.


Every agent can have as many behaviours as desired. When a message arrives to the agent, the message dispatcher redirects
it to the correct behaviour queue. A behaviour has a message template attached to it. Therefore, the message dispatcher
uses this template to determine which behaviour the message is for, by matching it with the correct template. A behaviour
can thus select what kind of messages it wants to receive by using templates.
