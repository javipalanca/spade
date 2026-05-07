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

First and foremost, there is a ``Message`` class. This class is ``spade.message.Message`` and you can instantiate it to
create new messages to work with. The class provides a method to introduce metadata into messages, this is useful for
using the fields present in standard FIPA-ACL Messages. When a message is ready to be sent, it can be passed on to the
send() method of the behaviour, which will trigger the internal communication process to actually send it to its
destination. Note that the send function is an async coroutine, so it needs to be called with an ``await`` statement.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Here is a self-explaining example::

    import spade
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


    async def main():
        senderagent = SenderAgent("sender@your_xmpp_server", "sender_password")
        await senderagent.start(auto_register=True)
        print("Sender started")

        await spade.wait_until_finished(receiveragent)
        print("Agents finished")


    if __name__ == "__main__":
        spade.run(main())



This code would output

.. code-block:: bash

    $ python sender.py
    SenderAgent started
    InformBehav running
    Message sent!
    Agent finished with exit code: Job Finished!



Ok, we have sent a message but now we need someone to receive that message. Show me the code

.. code-block:: python

    import spade
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



    async def main():
        receiveragent = ReceiverAgent("receiver@your_xmpp_server", "receiver_password")
        await receiveragent.start(auto_register=True)
        print("Receiver started")

        senderagent = SenderAgent("sender@your_xmpp_server", "sender_password")
        await senderagent.start(auto_register=True)
        print("Sender started")

        await spade.wait_until_finished(receiveragent)
        print("Agents finished")


    if __name__ == "__main__":
        spade.run(main())


.. note:: It's important to remember that the send and receive functions are **coroutines**, so they **always**
    must be called with the ``await`` statement.

In this example you can see how the ``RecvBehav`` behaviour receives the message because the template includes a
*performative* with the value **inform** in the metadata and the sent message does also include that metadata, so the
message and the template match.

The code below would output

.. code-block:: bash

    $ python send_and_recv.py
    ReceiverAgent started
    Receiver started
    RecvBehav running
    SenderAgent started
    Sender started
    InformBehav running
    Message sent!
    Message received with content: Hello World
    Agents finished

    Process finished with exit code 0

Using FIPA Messages
-------------------

SPADE provides the ``FIPAMessageBuilder`` class to simplify the creation of
FIPA-ACL compliant messages. This is an alternative to the basic ``Message``
class when structured and standardized communication between agents is required.

Creating a Message
~~~~~~~~~~~~~~~~~~

You can create a FIPA message using a fluent interface:

::

    from spade.fipa_message import FIPAMessageBuilder

    msg = (
        FIPAMessageBuilder(sender="agent1@localhost", receiver="agent2@localhost")
        .set_performative("inform")
        .set_body({"data": "Hello World"}, as_json=True)
        .set_ontology("example")
        .build()
    )

    await self.send(msg)

In this example:

* **performative** defines the intention of the message (e.g., ``inform``, ``request``)
* **body** contains the message content (typically JSON)
* **ontology** provides context for the content

The builder automatically includes metadata such as conversation identifiers
and timestamps.

Sending Messages
~~~~~~~~~~~~~~~~

Sending a FIPA message works the same as with a regular message:

::

    await self.send(msg)

.. note::
   The ``send`` method is an asynchronous coroutine and must always be used with ``await``.

Receiving and Parsing Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To process a received FIPA message, use the ``FIPAMessageParser``:

::

    from spade.fipa_message import FIPAMessageParser

    msg = await self.receive(timeout=10)

    if msg:
        parser = FIPAMessageParser(msg)

        print(parser.get_performative())
        print(parser.get_ontology())
        print(parser.parse_body())

The parser extracts metadata and automatically handles JSON content.

Sending Responses
~~~~~~~~~~~~~~~~~

FIPA messages are typically part of a conversation. To reply while preserving
the conversation context, use:

::

    response = FIPAMessageBuilder.create_response_message(
        original_msg=msg,
        content={"status": "ok"},
        performative="confirm"
    )

    await self.send(response)

This ensures that the response keeps the correct conversation identifiers and
references to the original message.

Convenience Methods
~~~~~~~~~~~~~~~~~~~

The builder provides helper methods for common message types:

::

    # Inform message
    msg = FIPAMessageBuilder.create_inform_message(
        sender="a@localhost",
        receiver="b@localhost",
        content={"value": 1}
    )

    # Request message
    msg = FIPAMessageBuilder.create_request_message(
        sender="a@localhost",
        receiver="b@localhost",
        action="get-data",
        parameters={"id": 1}
    )

Notes
~~~~~

* The performative must be a valid FIPA-ACL performative.
* Message content is typically encoded as JSON.
* Responses should be created using the builder to preserve conversation context.
* Templates can be used to filter messages based on performative:

::

    template = Template()
    template.set_metadata("performative", "inform")


Sending large files
-------------------
SPADE includes native support for file exchange between agents via HTTP (XEP-0363).
This allows sharing large files between each online agent in a more secure and robust way compared with
data serialization via XMPP stanzas

Prerequisites
~~~~~~~~~~~~~
To use this feature, ensure that:

* Your XMPP server supports ``urn:xmpp:http:upload:0``.
* The agent has the necessary permissions configured for file uploads on the server component.

.. note::
    This prerequisites only applies for users that prefer to run its own XMPP server.
    The integrated server in SPADE supports this feature without extra configuration.

Sending a File
~~~~~~~~~~~~~~
To send a file, you need to use the ``upload_and_send_file`` method within your agent's behavior to share the file
and communicate its location. On the receiving end, the agent listens for the message containing the file metadata by using
the ``performative`` metadata with the value ``0363``. When a message is received, a ``url`` metadata will be present. It is
the parameter required in the ``download_file`` to obtain the shared file.

The following example demonstrates how to implement both the sender and the receiver behaviors:

.. code-block:: python

    class SharerBehaviour(OneShotBehaviour):
        async def run(self):
            with open("text.txt", "rb") as file:
                url = await self.upload_and_send_file(
                    to="receiver@localhost",
                    filename="test.txt",
                    input_file=file
                )

    class ReceiveFileBehaviour(CyclicBehaviour):
        async def run(self):
        msg = self.receive(5)
        if msg:
            url = msg.get_metadata("url")
            if url:
                await self.download_file(url, "path/to/download")

    receive_template = Template()
    receive_template.set_metadata("performative", "0363")

    sharer = Agent("uploader@localhost", "1234")
    sharer.add_behaviour(SharerBehaviour())

    receiver = Agent("receiver@localhost", "1234")
    receiver.add_behaviour(ReceiveFileBehaviour(), receive_template)

The ``upload_and_send_file`` returns the url of the file, and can be reused with other agents during the same session
(i.e., the server didn't restart since the file was uploaded)

It is possible to upload and send the file in separated methods, to achieve more customized behaviours:

.. code-block:: python

    class UploadAndSendBehaviour(OneShotBehaviour):
        async def run(self):
            with open("text.txt", "rb") as file:
                url = await self.upload_file(filename="test.txt", input_file=file)
                await self.send_file(to="receiver@localhost", url=url)

    class ReceiveFileBehaviour(CyclicBehaviour):
        async def run(self):
        msg = self.receive(5)
        if msg:
            url = msg.get_metadata("url")
            if url:
                await self.download_file(url, "path/to/download")

    receive_template = Template()
    receive_template.set_metadata("performative", "0363")

    sharer = Agent("uploader@localhost", "1234")
    sharer.add_behaviour(UploadAndSendBehaviour())

    receiver = Agent("receiver@localhost", "1234")
    receiver.add_behaviour(ReceiveFileBehaviour(), receive_template)

