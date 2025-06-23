Sign in, Send a Message, and Disconnect
=======================================

.. note::

    If you have any issues working through this quickstart guide
    join the chat room at `slixmpp@muc.poez.io
    <xmpp:slixmpp@muc.poez.io?join>`_.

A common use case for Slixmpp is to send one-off messages from
time to time. For example, one use case could be sending out a notice when
a shell script finishes a task.

We will create our one-shot bot based on the pattern explained in :ref:`echobot`. To
start, we create a client class based on :class:`ClientXMPP <slixmpp.clientxmpp.ClientXMPP>` and
register a handler for the :term:`session_start` event. We will also accept parameters
for the JID that will receive our message, and the string content of the message.

.. code-block:: python

    import slixmpp


    class SendMsgBot(slixmpp.ClientXMPP):

        def __init__(self, jid, password, recipient, msg):
            super().__init__(jid, password)

            self.recipient = recipient
            self.msg = msg

            self.add_event_handler('session_start', self.start)

        async def start(self, event):
            self.send_presence()
            await self.get_roster()

Note that as in :ref:`echobot`, we need to include send an initial presence and request
the roster. Next, we want to send our message, and to do that we will use :meth:`send_message <slixmpp.basexmpp.BaseXMPP.send_message>`.

.. code-block:: python

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient, mbody=self.msg)

Finally, we need to disconnect the client using :meth:`disconnect <slixmpp.xmlstream.XMLStream.disconnect>`.
Now, sent stanzas are placed in a queue to pass them to the send routine.
:meth:`disconnect <slixmpp.xmlstream.XMLStream.disconnect>` by default will wait for an
acknowledgement from the server for at least `2.0` seconds. This time is configurable with
the `wait` parameter. If `0.0` is passed for `wait`, :meth:`disconnect
<slixmpp.xmlstream.XMLStream.disconnect>` will not close the connection gracefully.

.. code-block:: python

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient, mbody=self.msg)

        self.disconnect()

.. warning::

    If you happen to be adding stanzas to the send queue faster than the send thread
    can process them, then :meth:`disconnect() <slixmpp.xmlstream.XMLStream.disconnect>`
    will block and not disconnect.

Final Product
-------------

.. compound::

    The final step is to create a small runner script for initialising our ``SendMsgBot`` class and adding some
    basic configuration options. By following the basic boilerplate pattern in :ref:`echobot`, we arrive
    at the code below. To experiment with this example, you can use:

    .. code-block:: sh

            python send_client.py -d -j oneshot@example.com -t someone@example.net -m "This is a message"

    which will prompt for the password and then log in, send your message, and then disconnect. To test, open
    your regular IM client with the account you wish to send messages to. When you run the ``send_client.py``
    example and instruct it to send your IM client account a message, you should receive the message you
    gave. If the two JIDs you use also have a mutual presence subscription (they're on each other's buddy lists)
    then you will also see the ``SendMsgBot`` client come online and then go offline.

.. include:: ../../examples/send_client.py
    :literal:
