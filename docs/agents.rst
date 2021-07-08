====================
Agent communications
====================

Using templates
---------------

Templates is the method used by SPADE to dispatch received messages to the behaviour that is waiting for that message.
When adding a behaviour you can set a template for that behaviour, which allows the agent to deliver a message received
by the agent to that registered behaviour. A ``Template`` instance has the same attributes of a ``Message`` and all the
attributes defined in the template must be equal in the message for this to match.

The attributes that can be set in a template are:

* **to**: the jid string of the receiver of the message.
* **sender** the jid string of the sender of the message.
* **body**: the body of the message.
* **thread**: the thread id of the conversation.
* **metadata**: a (key, value) dictionary of strings to define metadata of the message. This is useful, for example, to include `FIPA <http://www.fipa.org>`_ attributes like *ontology*, *performative*, *language*, etc.

An example of template matching::

    template = Template()
    template.sender = "sender1@host"
    template.to = "recv1@host"
    template.body = "Hello World"
    template.thread = "thread-id"
    template.metadata = {"performative": "query"}

    message = Message()
    message.sender = "sender1@host"
    message.to = "recv1@host"
    message.body = "Hello World"
    message.thread = "thread-id"
    message.set_metadata("performative", "query")

    assert template.match(message)

Templates also support boolean operators to create more complex templates. Bitwise operators (&, |, ^ and ~) may be used
to combine simpler templates.

* **&**: Does a boolean AND between templates.
* **|**: Does a boolean OR between templates.
* **^**: Does a boolean XOR between templates.
* **~**: Returns the complement of the template.

Some examples of these operators::

    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}


    m = Message()
    m.sender = "sender1@host"
    m.to = "recv1@host"
    m.metadata = {"performative": "query"}

    # And AND operator
    assert (t1 & t2).match(m)

    t3 = Template()
    t3.sender = "not_valid_sender@host"

    # A NOT complement operator
    assert (~t3).match(m)


Sending and Receiving Messages
------------------------------

As you know, messages are the basis of every MAS. They are the centre of the whole "computing as interaction" paradigm
in which MAS are based. So it is very important to understand which facilities are present in SPADE to work with
agent messages.

First and foremost, threre is a ``Message`` class. This class is ``spade.message.Message`` and you can instantiate it to
create new messages to work with. The class provides a method to introduce metadata into messages, this is useful for
using the fields present in standard FIPA-ACL Messages. When a message is ready to be sent, it can be passed on to the
send() method of the behaviour, which will trigger the internal communication process to actually send it to its
destination. Note that the send function is an async coroutine, so it needs to be called with an ``await`` statement.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Here is a self-explaining example::

    import time
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.message import Message


    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                print("InformBehav running")
                msg = Message(to="receiver@your_xmpp_server")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")       # Set the language of the message content
                msg.body = "Hello World"                    # Set the message content

                await self.send(msg)
                print("Message sent!")

                # set exit_code for the behaviour
                self.exit_code = "Job Finished!"

                # stop agent from behaviour
                await self.agent.stop()

        async def setup(self):
            print("SenderAgent started")
            self.b = self.InformBehav()
            self.add_behaviour(self.b)


    if __name__ == "__main__":
        agent = SenderAgent("sender@your_xmpp_server", "sender_password")
        future = agent.start()
        future.result()

        while agent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                agent.stop()
                break
        print("Agent finished with exit code: {}".format(agent.b.exit_code))



This code would output::

    $ python sender.py
    SenderAgent started
    InformBehav running
    Message sent!
    Agent finished with exit code: Job Finished!



Ok, we have sent a message but now we need someone to receive that message. Show me the code::

    import time
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.message import Message
    from spade.template import Template


    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                print("InformBehav running")
                msg = Message(to="receiver@your_xmpp_server")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = "Hello World"                    # Set the message content

                await self.send(msg)
                print("Message sent!")

                # stop agent from behaviour
                await self.agent.stop()

        async def setup(self):
            print("SenderAgent started")
            b = self.InformBehav()
            self.add_behaviour(b)

    class ReceiverAgent(Agent):
        class RecvBehav(OneShotBehaviour):
            async def run(self):
                print("RecvBehav running")

                msg = await self.receive(timeout=10) # wait for a message for 10 seconds
                if msg:
                    print("Message received with content: {}".format(msg.body))
                else:
                    print("Did not received any message after 10 seconds")

                # stop agent from behaviour
                await self.agent.stop()

        async def setup(self):
            print("ReceiverAgent started")
            b = self.RecvBehav()
            template = Template()
            template.set_metadata("performative", "inform")
            self.add_behaviour(b, template)



    if __name__ == "__main__":
        receiveragent = ReceiverAgent("receiver@your_xmpp_server", "receiver_password")
        future = receiveragent.start()
        future.result() # wait for receiver agent to be prepared.
        senderagent = SenderAgent("sender@your_xmpp_server", "sender_password")
        senderagent.start()

        while receiveragent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                senderagent.stop()
                receiveragent.stop()
                break
        print("Agents finished")


.. note:: It's important to remember that the send and receive functions are **coroutines**, so they **always**
    must be called with the ``await`` statement.

In this example you can see how the ``RecvBehav`` behaviour receives the message because the template includes a
*performative* with the value **inform** in the metadata and the sent message does also include that metadata, so the
message and the template match.

You can also note that we are using an *ugly* ``time.sleep`` to introduce an explicit wait to avoid sending the message
before the receiver agent is up and ready since in another case the message would never be received (remember that spade
is a **real-time** messaging platform. In future sections we'll show you how to use *presence notification* to wait for
an agent to be *available*.

The code below would output::

    $ python send_and_recv.py
    ReceiverAgent started
    RecvBehav running
    SenderAgent started
    InformBehav running
    Message sent!
    Message received with content: Hello World
    Agents finished

