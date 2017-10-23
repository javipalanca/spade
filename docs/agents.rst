====================
Agent communications
====================

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
Here is a self-explaining example::

    import time
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.message import Message


    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                print("InformBehav running")
                msg = Message(to="receiver@jabber.org")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")       # Set the language of the message content
                msg.body = "Hello World"                    # Set the message content

                await self.send(msg)
                print("Message sent!")

                # stop agent from behaviour
                self.agent.stop()

        def setup(self):
            print("SenderAgent started")
            b = self.InformBehav()
            self.add_behaviour(b)


    if __name__ == "__main__":
        agent = SenderAgent("sender@jabber.org", "sender_password")

        while agent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                agent.stop()
                break
        print("Agent finished")



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
                msg = Message(to="receiver@jabber.org")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = "Hello World"                    # Set the message content

                await self.send(msg)
                print("Message sent!")

                # stop agent from behaviour
                self.agent.stop()

        def setup(self):
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
                self.agent.stop()

        def setup(self):
            print("ReceiverAgent started")
            b = self.RecvBehav()
            template = Template()
            template.metadata = {"performative": "inform"}
            self.add_behaviour(b, template)



    if __name__ == "__main__":
        receiveragent = ReceiverAgent("receiver@jabber.org", "receiver_password")
        time.sleep(2) # wait for receiver agent to be prepared. In next sections we'll use presence notification.
        senderagent = SenderAgent("sender@jabber.org", "sender_password")

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

