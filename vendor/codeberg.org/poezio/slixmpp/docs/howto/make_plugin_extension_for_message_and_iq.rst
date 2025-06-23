How to make a slixmpp plugins for Messages and IQ extensions
====================================================================

Introduction and requirements
------------------------------

* `'python3'`

Code used in the following tutorial is written in python  3.6 or newer.
For backward compatibility, replace the f-strings functionality with older string formatting: `'"{}".format("content")'` or `'%s, "content"'`.

Ubuntu linux installation steps:

.. code-block:: bash

    sudo apt-get install python3.6

* `'slixmpp'`
* `'argparse'`
* `'logging'`
* `'subprocess'`

Check if these libraries and the proper python version are available at your environment. Every one of these, except the slixmpp, is a standard python library. However, it may happen that some of them may not be installed.

.. code-block:: python

    python3 --version
    python3 -c "import slixmpp; print(slixmpp.__version__)"
    python3 -c "import argparse; print(argparse.__version__)"
    python3 -c "import logging; print(logging.__version__)"
    python3 -m subprocess

Example output:

.. code-block:: bash

    ~ $ python3 --version
    Python 3.8.0
    ~ $ python3 -c "import slixmpp; print(slixmpp.__version__)"
    1.4.2
    ~ $ python3 -c "import argparse; print(argparse.__version__)"
    1.1
    ~ $ python3 -c "import logging; print(logging.__version__)"
    0.5.1.2
    ~ $ python3 -m subprocess #Should return nothing

If some of the libraries throw `'ImportError'` or `'no module named ...'` error, install them with:

On Ubuntu linux:

.. code-block:: bash

    pip3 install slixmpp
    #or
    easy_install slixmpp

If some of the libraries throws NameError, reinstall the whole package once again.

* `Jabber accounts`

For the testing purposes, two private jabber accounts are required. They can be created on one of many available sites:
https://www.google.com/search?q=jabber+server+list

Client launch script
-----------------------------

The client launch script should be created outside of the main project location. This allows to easily obtain the results when needed and prevents accidental leakage of credential details to the git platform.

As the example, a file `'test_slixmpp'` can be created in `'/usr/bin'` directory, with executive permission:

.. code-block:: bash

    /usr/bin $ chmod 711 test_slixmpp

This file contains a simple structure for logging credentials:

.. code-block:: python

    #!/usr/bin/python3
    #File: /usr/bin/test_slixmpp & permissions rwx--x--x (711)

    import subprocess
    import time

    if __name__ == "__main__":
        #~ prefix = ["x-terminal-emulator", "-e"] # Separate terminal for every client; can be replaced with other terminal
        #~ prefix = ["xterm", "-e"]
        prefix = []
        #~ suffix = ["-d"] # Debug
        #~ suffix = ["-q"] # Quiet
        suffix = []

        sender_path = "./example/sender.py"
        sender_jid = "SENDER_JID"
        sender_password = "SENDER_PASSWORD"

        example_file = "./test_example_tag.xml"

        responder_path = "./example/responder.py"
        responder_jid = "RESPONDER_JID"
        responder_password = "RESPONDER_PASSWORD"

        # Remember about the executable permission. (`chmod +x ./file.py`)
        SENDER_TEST = prefix + [sender_path, "-j", sender_jid, "-p", sender_password, "-t", responder_jid, "--path", example_file] + suffix
        RESPON_TEST = prefix + [responder_path, "-j", responder_jid, "-p", responder_password] + suffix

        try:
            responder = subprocess.Popen(RESPON_TEST)
            sender = subprocess.Popen(SENDER_TEST)
            responder.wait()
            sender.wait()
        except:
            try:
                responder.terminate()
            except NameError:
                pass
            try:
                sender.terminate()
            except NameError:
                pass
            raise

The launch script should be convenient in use and easy to reconfigure again. The proper preparation of it now, can help saving time in the future. Logging credentials, the project paths (from `'sys.argv[...]'` or `'os.getcwd()'`), set the parameters for the debugging purposes, mock the testing xml file and many more things can be defined inside. Whichever parameters are used, the script testing itself should be fast and effortless. The proper preparation of it now, can help saving time in the future.

In case of manually testing the larger applications, it would be a good practice to introduce the unique names (consequently, different commands) for each client. In case of any errors, it will be easier to find the client that caused it.

Creating the client and the plugin
-----------------------------------

Two slixmpp clients should be created in order to check if everything works correctly (here: the `'sender'` and the `'responder'`). The minimal amount of code needed for effective building and testing of the plugin is the following:

.. code-block:: python

    #File: $WORKDIR/example/sender.py
    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Two, not required methods, but allows another users to see if the client is online.
            self.send_presence()
            self.get_roster()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        #xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is the example_plugin class name.

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

.. code-block:: python

    #File: $WORKDIR/example/responder.py
    import logging
    from argparse import ArgumentParser
    from getpass import getpass

    import asyncio
    import slixmpp
    import example_plugin

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)

        def start(self, event):
        # Two, not required methods, but allows another users to see if the client is online.
            self.send_presence()
            self.get_roster()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Responder.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message to")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Responder(args.jid, args.password)
        #xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is the example_plugin class name.

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

Next file to create is `'example_plugin.py'`. It can be placed in the same folder as the clients, so the problems with unknown paths can be avoided.

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py
    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ String data readable by humans and to find plugin by another plugin.
            self.xep = "ope"                                        ##~ String data readable by humans and to find plugin by another plugin by adding it into `slixmpp/plugins/__init__.py` to the `__all__` field, with 'xep_OPE' prefix.

            namespace = ExampleTag.namespace


    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element for that extension.
        namespace = "<https://example.net/our_extension>"             ##~ The namespace of the object, like <example_tag xmlns={namespace} (...)</example_tag>. Should be changed to your namespace.

        plugin_attrib = "example_tag"                               ##~ The name under which the data in plugin can be accessed. In particular, this object is reachable from the outside with: stanza_object['example_tag']. The `'example_tag'` is name of ElementBase extension and should be that same as the name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ElementBase extension.

If the plugin is not in the same directory as the clients, then the symbolic link to the localisation reachable by the clients should be established:

.. code-block:: bash

    ln -s $Path_to_example_plugin_py $Path_to_clients_destinations

The other solution is to relative import it (with dots '.') to get the proper path.

First run and the event handlers
-------------------------------------------------

To check if everything is okay, the `'start'` method can be used(which triggers the `'session_start'` event). Right after the client is ready, the signal will be sent.

In the `'__init__'` method, the handler for event call `'session_start'` is created. When it is called,  the `'def start(self, event):'` method will be executed. During the first run, add the line: `'logging.info("I'm running")'` to both the sender and the responder, and use `'test_slixmpp'` command.

The `'def start(self, event):'` method should look like this:

.. code-block:: python

    def start(self, event):
        # Two, not required methods, but allows another users to see us available, and receive that information.
        self.send_presence()
        self.get_roster()

        #>>>>>>>>>>>>
        logging.info("I'm running")
        #<<<<<<<<<<<<

If everything works fine, this line can be commented out.

Building the message object
------------------------------

The example sender class should get a recipient name and address (jid of responder) from command line arguments, stored in test_slixmpp. An access to this argument is stored in the `'self.to'` attribute.

Code example:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()
            #>>>>>>>>>>>>
            self.send_example_message(self.to, "example_message")

        def send_example_message(self, to, body):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Default mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            msg.send()
            #<<<<<<<<<<<<

In the example below, the build-in method `'make_message'` is used. It creates a string "example_message" and sends it at the end of `'start'` method. The message will be sent once, after the script launch.

To receive this message, the responder should have a proper handler to the signal with the message object and the method to decide what to do with this message. As it is shown in the example below:

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)

            #>>>>>>>>>>>>
            self.add_event_handler("message", self.message)
            #<<<<<<<<<<<<

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

        #>>>>>>>>>>>>
        def message(self, msg):
            #Show all inside msg
            logging.info(msg)
            #Show only body attribute
            logging.info(msg['body'])
        #<<<<<<<<<<<<

Expanding the Message with a new tag
-------------------------------------

To expand the Message object with a tag, the plugin should be registered as the extension for the Message object:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ String data readable by humans and to find plugin by another plugin.
            self.xep = "ope"                 ##~ String data readable by humans and to find plugin by another plugin by adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'.

            namespace = ExampleTag.namespace
            #>>>>>>>>>>>>
            register_stanza_plugin(Message, ExampleTag)             ##~ Register the tag extension for Message object, otherwise message['example_tag'] will be string field instead container and managing fields and create sub elements would be impossible.
            #<<<<<<<<<<<<

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The namespace for stanza object, like <example_tag xmlns={namespace} (...)</example_tag>.

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'] now `'example_tag'` is name of ElementBase extension. And this should be that same as 'name' above.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ours ElementBase extension.

        #>>>>>>>>>>>>
        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string
        #<<<<<<<<<<<<

Now, with the registered object, the message can be extended.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()
            self.send_example_message(self.to, "example_message")

        def send_example_message(self, to, body):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Default mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            #>>>>>>>>>>>>
            msg['example_tag']['some_string'] = "Work!"
            logging.info(msg)
            #<<<<<<<<<<<<
            msg.send()

After running, the logging should print the Message with tag `'example_tag'` stored inside <message><example_tag/></message>, string `'Work'` and given namespace.

Giving the extended message the separate signal
------------------------------------------------

If the separate event is not defined, then both normal and extended message will be cached by signal `'message'`. In order to have the special event, the handler for the namespace and tag should be created. Then, make a unique name combination, which allows the handler can catch only the wanted messages (or Iq object).

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ String data readable by humans and to find the plugin by another plugin.
            self.xep = "ope"                 ##~ String data readable by humans and to find the plugin by another plugin by adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'.

            namespace = ExampleTag.namespace

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Name of this Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Handles only the Message with good example_tag and namespace.
                        self.__handle_message))                     ##~ Method catches the proper Message, should raise event for the client.
            register_stanza_plugin(Message, ExampleTag)             ##~ Register the tags extension for Message object, otherwise message['example_tag'] will be string field instead container and managing the fields and create sub elements would not be possible.

        def __handle_message(self, msg):
            # Here something can be done with received message before it reaches the client.
            self.xmpp.event('example_tag_message', msg)          ##~ Call event which can be handled by the client with desired object as an argument.

StanzaPath objects should be initialised in a specific way, such as:
`'OBJECT_NAME[@type=TYPE_OF_OBJECT][/{NAMESPACE}[TAG]]'`

* OBJECT_NAME can be `'message'` or `'iq'`.
* For TYPE_OF_OBJECT, when iq is specified, `'get, set, error or result'` can be used. When object is a message, then the message type can be used, like `'chat'`.
* NAMESPACE should always be a namespace from tag extension class.
* TAG should contain the tag, in this case:`'example_tag'`.

Now every message containing the defined namespace inside `'example_tag'` is cached. It is possible to check the content of it. Then, the message is send to the client with the `'example_tag_message'` event.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()
            #>>>>>>>>>>>>
            self.send_example_message(self.to, "example_message", "example_string")

        def send_example_message(self, to, body, some_string=""):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Default mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            if some_string:
                msg['example_tag'].set_some_string(some_string)
            msg.send()
            #<<<<<<<<<<<<

Now, remember the line: `'self.xmpp.event('example_tag_message', msg)'`. The name of an event to catch inside the "responder.py" file was defined here. Here it is: `'example_tag_message'`.

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_message", self.example_tag_message) #Registration of the handler
            #<<<<<<<<<<<<

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

        #>>>>>>>>>>>>
        def example_tag_message(self, msg):
            logging.info(msg) # Message is standalone object, it can be replied, but no error is returned if not.
        #<<<<<<<<<<<<

The messages can be replied, but nothing will happen otherwise.
The Iq object, on the other hand, should always be replied. Otherwise, the error occurs on the client side due to the target timeout if the cell Iq won't reply with Iq with the same Id.

Useful methods and misc.
-------------------------

Modifying the example `Message` object to the `Iq` object
----------------------------------------------------------

To allow our custom element into Iq payloads, a new handler for Iq can be registered, in the same manner as in the `,,Extend message with tags''` part. The following example contains several types of Iq different types to catch. It can be used to check the difference between the Iq request and Iq response or to verify the correctness of the objects. All of the Iq messages should be passed to the sender with the same ID parameter, otherwise the sender will receive an error message.

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ String data readable by humans and to find the plugin by another plugin.
            self.xep = "ope"                 ##~ String data readable by humans and to find the plugin by another plugin by adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'.

            namespace = ExampleTag.namespace
            #>>>>>>>>>>>>
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Name of this Callback
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Handle only Iq with type 'get' and example_tag
                        self.__handle_get_iq))                      ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleResult Event:example_tag', ##~ Name of this Callback
                        StanzaPath(f"iq@type=result/{{{namespace}}}example_tag"),   ##~ Handle only Iq with type 'result' and example_tag
                        self.__handle_result_iq))                   ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleError Event:example_tag',  ##~ Name of this Callback
                        StanzaPath(f"iq@type=error/{{{namespace}}}example_tag"),    ##~ Handle only Iq with type 'error' and example_tag
                        self.__handle_error_iq))                    ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Name of this Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Handle only Message with example_tag
                        self.__handle_message))                     ##~ Method which catch proper Message, should raise proper event for client.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Register tags extension for Iq object. Otherwise the iq['example_tag'] will be string field instead of container and it would not be possible to manage the fields and sub elements.
            #<<<<<<<<<<<<
            register_stanza_plugin(Message, ExampleTag)             ##~ Register tags extension for Message object, otherwise message['example_tag'] will be string field instead container, where it is impossible to manage fields and create sub elements.

            #>>>>>>>>>>>>
        # All iq types are: get, set, error, result
        def __handle_get_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Calls the event which can be handled by clients.

        def __handle_result_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_result_iq', iq)        ##~ Calls the event which can be handled by clients.

        def __handle_error_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_error_iq', iq)         ##~ Calls the event which can be handled by clients.

        def __handle_message(self, msg):
            # Do something with received message
            self.xmpp.event('example_tag_message', msg)          ##~ Calls the event which can be handled by clients.

The events called by the example handlers can be caught like in the`'example_tag_message'` part.

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_message", self.example_tag_message)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_get_iq", self.example_tag_get_iq)
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def example_tag_get_iq(self, iq): # Iq stanza always should have a respond. If user is offline, it calls an error.
            logging.info(str(iq))
            reply = iq.reply(clear=False)
            reply.send()
            #<<<<<<<<<<<<

By default, the parameter `'clear'` in the `'Iq.reply'` is set to True. In that case, the content of the Iq should be set again. After using the reply method, only the Id and the Jid parameters will still be set.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)
            #<<<<<<<<<<<<

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            #>>>>>>>>>>>>
            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag']['boolean'] = "True"
            iq['example_tag']['some_string'] = "Another_string"
            iq['example_tag'].text = "Info_inside_tag"
            iq.send()
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def example_tag_result_iq(self, iq):
            logging.info(str(iq))

        def example_tag_error_iq(self, iq):
            logging.info(str(iq))
            #<<<<<<<<<<<<

Different ways to access the elements
--------------------------------------

There are several ways to access the elements inside the Message or Iq stanza. The first one: the client can access them like a dictionary:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        #...
        def example_tag_result_iq(self, iq):
            logging.info(str(iq))
            #>>>>>>>>>>>>
            logging.info(iq['id'])
            logging.info(iq.get('id'))
            logging.info(iq['example_tag']['boolean'])
            logging.info(iq['example_tag'].get('boolean'))
            logging.info(iq.get('example_tag').get('boolean'))
            #<<<<<<<<<<<<

The access to the elements from extended ExampleTag is similar. However, defining the types is not required and the access can be diversified (like for the `'text'` field below). For the ExampleTag extension, there is a 'getter' and 'setter' method for specific fields:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The namespace for stanza object, like <example_tag xmlns={namespace} (...)</example_tag>. Should be changed to own namespace.

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'], the `'example_tag'` is the name of ElementBase extension. And this should be the same as name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ElementBase extension.

            #>>>>>>>>>>>>
        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text
            #<<<<<<<<<<<<

The attribute `'self.xml'` is inherited from the ElementBase and is exactly the same as the `'Iq['example_tag']'` from the client namespace.

When the proper setters and getters are used, it is easy to check whether some argument is proper for the plugin or is convertible to another type. The code itself can be cleaner and more object-oriented, like in the example below:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag']['boolean'] = "True"  #Direct assignment
            #>>>>>>>>>>>>
            iq['example_tag'].set_some_string("Another_string") #Assignment by setter
            iq['example_tag'].set_text("Info_inside_tag")
            #<<<<<<<<<<<<
            iq.send()

Message setup from the XML files, strings and other objects
------------------------------------------------------------

There are many ways to set up a xml from a string, xml-containing file or lxml (ElementTree) file. One of them is parsing the strings to lxml object, passing the attributes and other information, which may look like this:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    #...
    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin
    #...

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The stanza object namespace, like <example_tag xmlns={namespace} (...)</example_tag>. Should be changed to your own namespace

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'] now `'example_tag'` is name of ElementBase extension. And this should be that same as name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ElementBase extension.

            #>>>>>>>>>>>>
        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)
            #<<<<<<<<<<<<

To test this, an example file with xml, example xml string and example lxml (ET) object is needed:

.. code-block:: xml

    #File: $WORKDIR/test_example_tag.xml

    <example_tag xmlns="https://example.net/our_extension" some_string="StringFromFile">Info_inside_tag<inside_tag first_field="3" second_field="4" /></example_tag>

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    #...
    from slixmpp.xmlstream import ET
    #...

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            #>>>>>>>>>>>>
            self.disconnect_counter = 3 # Disconnects when all replies from Iq are received.

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>

        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after receiving the maximum number of responses.

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()
            #<<<<<<<<<<<<

If the Responder returns the proper `'Iq'` and the Sender disconnects after three answers, then everything works okay.

Dev friendly methods for plugin usage
--------------------------------------

Any plugin should have some sort of object-like methods, that was setup for elements: reading the data, getters, setters and signals, to make them easy to use.
During handling, the correctness of the data should be checked and the eventual errors returned back to the sender. In order to avoid the situation where the answer message is never send, the sender gets the timeout error.

The following code presents exactly this:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ String data to read by humans and to find the plugin by another plugin.
            self.xep = "ope"                 ##~ String data to read by humans and to find the plugin by another plugin by adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'.

            namespace = ExampleTag.namespace
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Name of this Callback
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Handle only Iq with type 'get' and example_tag
                        self.__handle_get_iq))                      ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleResult Event:example_tag', ##~ Name of this Callback
                        StanzaPath(f"iq@type=result/{{{namespace}}}example_tag"),   ##~ Handle only Iq with type 'result' and example_tag
                     self.__handle_result_iq))                   ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleError Event:example_tag',  ##~ Name of this Callback
                        StanzaPath(f"iq@type=error/{{{namespace}}}example_tag"),   ##~ Handle only Iq with type 'error' and example_tag
                        self.__handle_error_iq))                    ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Name of this Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),         ##~ Handle only Message with example_tag
                        self.__handle_message))                     ##~ Method which catch proper Message, should raise proper event for client.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Register tags extension for Iq object. Otherwise the iq['example_tag'] will be string field instead of container and it would not be possible to manage the fields and sub elements.
            register_stanza_plugin(Message, ExampleTag)                  ##~ Register tags extension for Iq object. Otherwise the iq['example_tag'] will be string field instead of container and it would not be possible to manage the fields and sub elements.

        # All iq types are: get, set, error, result
        def __handle_get_iq(self, iq):
            if iq.get_some_string is None:
                error = iq.reply(clear=False)
                error["type"] = "error"
                error["error"]["condition"] = "missing-data"
                error["error"]["text"] = "Without some_string value returns error."
                error.send()
            # Do something with received iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Call event which can be handled by clients to send or something else.

        def __handle_result_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_result_iq', iq)        ##~ Call event which can be handled by clients to send or something else.

        def __handle_error_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_error_iq', iq)         ##~ Call event which can be handled by clients to send or something else.

        def __handle_message(self, msg):
            # Do something with received message
            self.xmpp.event('example_tag_message', msg)          ##~ Call event which can be handled by clients to send or something else.

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The namespace stanza object lives in, like <example_tag xmlns={namespace} (...)</example_tag>. You should change it for your own namespace.

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'] now `'example_tag'` is name of ElementBase extension. And this should be that same as name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ElementBase extension.

        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)

        def setup_from_dict(self, data):
            #There keys from dict should be also validated
            self.xml.attrib.update(data)

        def get_boolean(self):
            return self.xml.attrib.get("boolean", None)

        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text

        def fill_interfaces(self, boolean, some_string):
            #Some validation, if necessary
            self.set_boolean(boolean)
            self.set_some_string(some_string)

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass

    import asyncio
    import slixmpp
    import example_plugin

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_get_iq", self.example_tag_get_iq)
            self.add_event_handler("example_tag_message", self.example_tag_message)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

        def example_tag_get_iq(self, iq): # Iq stanza always should have a respond. If user is offline, it call an error.
            logging.info(iq)
            reply = iq.reply()
            reply["example_tag"].fill_interfaces(True, "Reply_string")
            reply.send()

        def example_tag_message(self, msg):
            logging.info(msg) # Message is standalone object, it can be replied, but no error arrives if not.


    if __name__ == '__main__':
        parser = ArgumentParser(description=Responder.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message to")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Responder(args.jid, args.password)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 5 #  # Disconnect after receiving the maximum number of responses.

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after receiving the maximum number of responses.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after receiving the maximum number of responses.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # For example, the condition to receive the error respond is the example_tag without the boolean value.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin.

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

Tags and strings nested inside the tag
---------------------------------------------------------

To create the nested element inside IQ tag, `self.xml` field  can be considered as an Element from ET (ElementTree). Therefore adding the nested Elements is appending the Element.

As shown in the previous examples, it is possible to create a new element as main (ExampleTag). However, when the additional methods or validation is not needed and the result will be parsed to xml anyway, it may be better to nest the Element from ElementTree with method 'append'. In order to not use the 'setup' method again, the code below shows way of the manual addition of the nested tag and creation of ET Element.

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py

    #(...)

    class ExampleTag(ElementBase):

    #(...)

        def add_inside_tag(self, tag, attributes, text=""):
            #If more tags is needed inside the element, they can be added like that:
            itemXML = ET.Element("{{{0:s}}}{1:s}".format(self.namespace, tag)) #~ Initialise ET with tag, for example: <example_tag (...)> <inside_tag namespace="<https://example.net/our_extension>"/></example_tag>
            itemXML.attrib.update(attributes) #~ Here we add some fields inside tag, for example: <inside_tag namespace=(...) inner_data="some"/>
            itemXML.text = text #~ Fill field inside tag, for example: <inside_tag (...)>our_text</inside_tag>
            self.xml.append(itemXML) #~ Add that is all, what needs to be set as an inner tag inside the `example_tag` tag.

There is a way to do this with a dictionary and name for the nested element tag. In that case, the insides of the function fields should be transferred to the ET element.

Complete code from tutorial
----------------------------

.. code-block:: python

    #!/usr/bin/python3
    #File: /usr/bin/test_slixmpp & permissions rwx--x--x (711)

    import subprocess
    import time

    if __name__ == "__main__":
        #~ prefix = ["x-terminal-emulator", "-e"] # Separate terminal for every client; can be replaced with other terminal
        #~ prefix = ["xterm", "-e"]
        prefix = []
        #~ suffix = ["-d"] # Debug
        #~ suffix = ["-q"] # Quiet
        suffix = []

        sender_path = "./example/sender.py"
        sender_jid = "SENDER_JID"
        sender_password = "SENDER_PASSWORD"

        example_file = "./test_example_tag.xml"

        responder_path = "./example/responder.py"
        responder_jid = "RESPONDER_JID"
        responder_password = "RESPONDER_PASSWORD"

        # Remember about the executable permission. (`chmod +x ./file.py`)
        SENDER_TEST = prefix + [sender_path, "-j", sender_jid, "-p", sender_password, "-t", responder_jid, "--path", example_file] + suffix
        RESPON_TEST = prefix + [responder_path, "-j", responder_jid, "-p", responder_password] + suffix

        try:
            responder = subprocess.Popen(RESPON_TEST)
            sender = subprocess.Popen(SENDER_TEST)
            responder.wait()
            sender.wait()
        except:
            try:
                responder.terminate()
            except NameError:
                pass
            try:
                sender.terminate()
            except NameError:
                pass
            raise

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py

    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"   ##~ String data for Human readable and find plugin by another plugin with method.
            self.xep = "ope"                          ##~ String data for Human readable and find plugin by another plugin with adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'. Otherwise it's just human readable annotation.

            namespace = ExampleTag.namespace
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Name of this Callback
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Handle only Iq with type get and example_tag
                        self.__handle_get_iq))                      ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleResult Event:example_tag', ##~ Name of this Callback
                        StanzaPath(f"iq@type=result/{{{namespace}}}example_tag"),   ##~ Handle only Iq with type result and example_tag
                        self.__handle_result_iq))                   ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleError Event:example_tag',  ##~ Name of this Callback
                        StanzaPath(f"iq@type=error/{{{namespace}}}example_tag"),    ##~ Handle only Iq with type error and example_tag
                        self.__handle_error_iq))                    ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Name of this Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Handle only Message with example_tag
                        self.__handle_message))                     ##~ Method which catch proper Message, should raise proper event for client.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Register tags extension for Iq object. Otherwise the iq['example_tag'] will be string field instead of container and it would not be possible to manage the fields and sub elements.
            register_stanza_plugin(Message, ExampleTag)                  ##~ Register tags extension for Iq object. Otherwise the iq['example_tag'] will be string field instead of container and it would not be possible to manage the fields and sub elements.

        # All iq types are: get, set, error, result
        def __handle_get_iq(self, iq):
            if iq.get_some_string is None:
                error = iq.reply(clear=False)
                error["type"] = "error"
                error["error"]["condition"] = "missing-data"
                error["error"]["text"] = "Without some_string value returns error."
                error.send()
            # Do something with received iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_result_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_result_iq', iq)        ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_error_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_error_iq', iq)         ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_message(self, msg):
            # Do something with received message
            self.xmpp.event('example_tag_message', msg)          ##~ Call event which can be handled by clients to send or something other what you want.

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The stanza object namespace, like <example_tag xmlns={namespace} (...)</example_tag>. Should be changed for your namespace.

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'] now `'example_tag'` is name of ours ElementBase extension. And this should be that same as name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ours ElementBase extension.

        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)

        def setup_from_dict(self, data):
            #There should keys should be also validated
            self.xml.attrib.update(data)

        def get_boolean(self):
            return self.xml.attrib.get("boolean", None)

        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text

        def fill_interfaces(self, boolean, some_string):
            #Some validation if it is necessary
            self.set_boolean(boolean)
            self.set_some_string(some_string)

        def add_inside_tag(self, tag, attributes, text=""):
            #If more tags is needed inside the element, they can be added like that:
            itemXML = ET.Element("{{{0:s}}}{1:s}".format(self.namespace, tag)) #~ Initialise ET with tag, for example: <example_tag (...)> <inside_tag namespace="https://example.net/our_extension"/></example_tag>
            itemXML.attrib.update(attributes) #~ There we add some fields inside tag, for example: <inside_tag namespace=(...) inner_data="some"/>
            itemXML.text = text #~ Fill field inside tag, for example: <inside_tag (...)>our_text</inside_tag>
            self.xml.append(itemXML) #~ Add that all what we set, as inner tag inside `example_tag` tag.

~

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 6 # This is only for disconnect when we receive all replies for sent Iq

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_iq_with_inner_tag(self.to)
            # <iq from="SENDER/RESOURCE" to="RESPONDER/RESOURCE" id="1" xml:lang="en" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_iq_with_inner_tag(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=1)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")

            inner_attributes = {"first_field": "1", "second_field": "2"}
            iq['example_tag'].add_inside_tag(tag="inside_tag", attributes=inner_attributes)

            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # For example, the condition to receive error respond is the example_tag without boolean value.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

~

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 6 # This is only for disconnect when we receive all replies for sended Iq

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_iq_with_inner_tag(self.to)
            # <iq from="SENDER/RESOURCE" to="RESPONDER/RESOURCE" id="1" xml:lang="en" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" second_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag second_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_iq_with_inner_tag(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=1)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")

            inner_attributes = {"first_field": "1", "second_field": "2"}
            iq['example_tag'].add_inside_tag(tag="inside_tag", attributes=inner_attributes)

            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # For example, the condition for receivingg error respond is example_tag without boolean value.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

~

.. code-block:: python

    #File: $WORKDIR/test_example_tag.xml

.. code-block:: xml

    <example_tag xmlns="https://example.net/our_extension" some_string="StringFromFile">Info_inside_tag<inside_tag first_field="3" second_field="4" /></example_tag>

Sources and references
-----------------------

The Slixmpp project description:

* https://pypi.org/project/slixmpp/

Official web documentation:

* https://slixmpp.readthedocs.io/

Official PDF documentation:

* https://buildmedia.readthedocs.org/media/pdf/slixmpp/latest/slixmpp.pdf

Note: Web and PDF Documentations have differences and some things are mentioned in only one of them.
