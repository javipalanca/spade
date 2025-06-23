.. _echobot:

===============================
Slixmpp Quickstart - Echo Bot
===============================

.. note::

    If you have any issues working through this quickstart guide
    join the chat room at `slixmpp@muc.poez.io
    <xmpp:slixmpp@muc.poez.io?join>`_.

If you have not yet installed Slixmpp, do so now by either checking out a version
with `Git <https://codeberg.org/poezio/slixmpp>`_.

As a basic starting project, we will create an echo bot which will reply to any
messages sent to it. We will also go through adding some basic command line configuration
for enabling or disabling debug log outputs and setting the username and password
for the bot.

For the command line options processing, we will use the built-in ``argparse``
module and the ``getpass`` module for reading in passwords.

TL;DR Just Give Me the Code
---------------------------
As you wish: :ref:`the completed example <echobot_complete>`.

Overview
--------

To get started, here is a brief outline of the structure that the final project will have:

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    import logging
    from getpass import getpass
    from argparse import ArgumentParser

    import asyncio
    import slixmpp

    '''Here we will create out echo bot class'''

    if __name__ == '__main__':
        '''Here we will configure and read command line options'''

        '''Here we will instantiate our echo bot'''

        '''Finally, we connect the bot and start listening for messages'''

Creating the EchoBot Class
--------------------------

There are three main types of entities within XMPP — servers, components, and
clients. Since our echo bot will only be responding to a few people, and won't need
to remember thousands of users, we will use a client connection. A client connection
is the same type that you use with your standard IM client such as Pidgin or Psi.

Slixmpp comes with a :class:`ClientXMPP <slixmpp.clientxmpp.ClientXMPP>` class
which we can extend to add our message echoing feature. :class:`ClientXMPP <slixmpp.clientxmpp.ClientXMPP>`
requires the parameters ``jid`` and ``password``, so we will let our ``EchoBot`` class accept those
as well.

.. code-block:: python

    class EchoBot(slixmpp.ClientXMPP):

        def __init__(self, jid, password):
            super().__init__(jid, password)

Handling Session Start
~~~~~~~~~~~~~~~~~~~~~~
The XMPP spec requires clients to broadcast its presence and retrieve its roster (buddy list) once
it connects and establishes a session with the XMPP server. Until these two tasks are completed,
some servers may not deliver or send messages or presence notifications to the client. So we now
need to be sure that we retrieve our roster and send an initial presence once the session has
started. To do that, we will register an event handler for the :term:`session_start` event.

.. code-block:: python

     def __init__(self, jid, password):
        super().__init__(jid, password)

        self.add_event_handler('session_start', self.start)


Since we want the method ``self.start`` to execute when the :term:`session_start` event is triggered,
we also need to define the ``self.start`` handler.

.. code-block:: python

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

.. warning::

    Not sending an initial presence and retrieving the roster when using a client instance can
    prevent your program from receiving presence notifications or messages depending on the
    XMPP server you have chosen.

Our event handler, like every event handler, accepts a single parameter which typically is the stanza
that was received that caused the event. In this case, ``event`` will just be an empty dictionary since
there is no associated data.

Our first task of sending an initial presence is done using :meth:`send_presence <slixmpp.basexmpp.BaseXMPP.send_presence>`.
Calling :meth:`send_presence <slixmpp.basexmpp.BaseXMPP.send_presence>` without any arguments will send the simplest
stanza allowed in XMPP:

.. code-block:: xml

    <presence />


The second requirement is fulfilled using :meth:`get_roster <slixmpp.clientxmpp.ClientXMPP.get_roster>`, which
will send an IQ stanza requesting the roster to the server and then wait for the response. You may be wondering
what :meth:`get_roster <slixmpp.clientxmpp.ClientXMPP.get_roster>` returns since we are not saving any return
value. The roster data is saved by an internal handler to ``self.roster``, and in the case of a :class:`ClientXMPP
<slixmpp.clientxmpp.ClientXMPP>` instance to ``self.client_roster``. (The difference between ``self.roster`` and
``self.client_roster`` is that ``self.roster`` supports storing roster information for multiple JIDs, which is useful
for components, whereas ``self.client_roster`` stores roster data for just the client's JID.)

It is possible for a timeout to occur while waiting for the server to respond, which can happen if the
network is excessively slow or the server is no longer responding. In that case, an :class:`IQTimeout
<slixmpp.exceptions.IQTimeout>` is raised. Similarly, an :class:`IQError <slixmpp.exceptions.IQError>` exception can
be raised if the request contained bad data or requested the roster for the wrong user. In either case, you can wrap the
``get_roster()`` call in a ``try``/``except`` block to retry the roster retrieval process.

The XMPP stanzas from the roster retrieval process could look like this:

.. code-block:: xml

    <iq type="get">
      <query xmlns="jabber:iq:roster" />
    </iq>

    <iq type="result" to="echobot@example.com" from="example.com">
      <query xmlns="jabber:iq:roster">
        <item jid="friend@example.com" subscription="both" />
      </query>
    </iq>

Additionally, since :meth:`get_roster <slixmpp.clientxmpp.ClientXMPP.get_roster>` is using
``<iq/>`` stanzas, which will always receive an answer, it should be awaited on, to keep
a synchronous flow.


Responding to Messages
~~~~~~~~~~~~~~~~~~~~~~
Now that an ``EchoBot`` instance handles :term:`session_start`, we can begin receiving and
responding to messages. Now we can register a handler for the :term:`message` event that is raised
whenever a messsage is received.

.. code-block:: python

     def __init__(self, jid, password):
        super().__init__(jid, password)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)


The :term:`message` event is fired whenever a ``<message />`` stanza is received, including for
group chat messages, errors, etc. Properly responding to messages thus requires checking the
``'type'`` interface of the message :term:`stanza object`. For responding to only messages
addressed to our bot (and not from a chat room), we check that the type is either ``normal``
or ``chat``. (Other potential types are ``error``, ``headline``, and ``groupchat``.)

.. code-block:: python

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            msg.reply("Thanks for sending:\n%s" % msg['body']).send()

Let's take a closer look at the ``.reply()`` method used above. For message stanzas,
``.reply()`` accepts the parameter ``body`` (also as the first positional argument),
which is then used as the value of the ``<body />`` element of the message.
Setting the appropriate ``to`` JID is also handled by ``.reply()``.

Another way to have sent the reply message would be to use :meth:`send_message <slixmpp.basexmpp.BaseXMPP.send_message>`,
which is a convenience method for generating and sending a message based on the values passed to it. If we were to use
this method, the above code would look as so:

.. code-block:: python

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            self.send_message(mto=msg['from'],
                              mbody='Thanks for sending:\n%s' % msg['body'])

Whichever method you choose to use, the results in action will look like this:

.. code-block:: xml

    <message to="echobot@example.com" from="someuser@example.net" type="chat">
      <body>Hej!</body>
    </message>

    <message to="someuser@example.net" type="chat">
      <body>Thanks for sending:
      Hej!</body>
    </message>

.. note::
    XMPP does not require stanzas sent by a client to include a ``from`` attribute, and
    leaves that responsibility to the XMPP server. However, if a sent stanza does
    include a ``from`` attribute, it must match the full JID of the client or some
    servers will reject it. Slixmpp thus leaves out the ``from`` attribute when replying
    using a client connection.

Command Line Arguments and Logging
----------------------------------

While this isn't part of Slixmpp itself, we do want our echo bot program to be able
to accept a JID and password from the command line instead of hard coding them. We will
use the ``argparse`` module for this.

We want to accept three parameters: the JID for the echo bot, its password, and a flag for
displaying the debugging logs. We also want these to be optional parameters, since passing
a password directly through the command line can be a security risk.

.. code-block:: python

    if __name__ == '__main__':
        # Setup the command line arguments.
        parser = ArgumentParser(description=EchoBot.__doc__)

        # Output verbosity options.
        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        # JID and password options.
        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")

        args = parser.parse_args()

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

Since we included a flag for enabling debugging logs, we need to configure the
``logging`` module to behave accordingly.

.. code-block:: python

    if __name__ == '__main__':

        # .. option parsing from above ..

        logging.basicConfig(level=args.loglevel,
                            format='%(levelname)-8s %(message)s')


Connecting to the Server and Processing
---------------------------------------
There are three steps remaining until our echo bot is complete:
    1. We need to instantiate the bot.
    2. The bot needs to connect to an XMPP server.
    3. We have to instruct the bot to start running and processing messages.

Creating the bot is straightforward, but we can also perform some configuration
at this stage. For example, let's say we want our bot to support `service discovery
<http://xmpp.org/extensions/xep-0030.html>`_ and `pings <http://xmpp.org/extensions/xep-0199.html>`_:

.. code-block:: python

    if __name__ == '__main__':

        # .. option parsing and logging steps from above

        xmpp = EchoBot(opts.jid, opts.password)
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0199') # Ping

If the ``EchoBot`` class had a hard dependency on a plugin, we could register that plugin in
the ``EchoBot.__init__`` method instead.

Now we're ready to connect and begin echoing messages. If you have the package
``aiodns`` installed, then the :meth:`slixmpp.clientxmpp.ClientXMPP.connect` method
will perform a DNS query to find the appropriate server to connect to for the
given JID. If you do not have ``aiodns``, then Slixmpp will attempt to
connect to the hostname used by the JID, unless an address tuple is supplied
to :meth:`slixmpp.clientxmpp.ClientXMPP.connect`.

.. code-block:: python

    if __name__ == '__main__':

        # .. option parsing & echo bot configuration
        xmpp.connect():
        asyncio.get_event_loop().run_forever()


The :meth:`slixmpp.basexmpp.BaseXMPP.connect` will only schedule a connection
asynchronously. To actually connect, you need to let the event loop take over.
This is done the normal asyncio way, which you can learn about in the `official
Python documentation <https://docs.python.org/3/library/asyncio-eventloop.html#event-loop-methods>`_.
Here we are making it run forever, but you can use any asyncio handling you
want, for instance to integrate slixmpp into an existing event loop.

Another common usecase is to make it run only until it gets disconnected, with
``asyncio.get_event_loop().run_until_complete(xmpp.disconnected)``.

.. note::

    In previous versions of slixmpp, there was a ``process()`` method which
    handled the event loop for you, but it was a very common source of
    confusion for people unfamiliar with asyncio.

.. _echobot_complete:

The Final Product
-----------------

Here then is what the final result should look like after working through the guide above. The code
can also be found in the Slixmpp `examples directory <https://codeberg.org/poezio/slixmpp/src/branch/master/examples>`_.

.. compound::

    You can run the code using:

    .. code-block:: sh

        python echobot.py -d -j echobot@example.com

    which will prompt for the password and then begin echoing messages. To test, open
    your regular IM client and start a chat with the echo bot. Messages you send to it should
    be mirrored back to you. Be careful if you are using the same JID for the echo bot that
    you also have logged in with another IM client. Messages could be routed to your IM client instead
    of the bot.

.. include:: ../../examples/echo_client.py
    :literal:
