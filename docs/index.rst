Slixmpp
#########

.. sidebar:: Get the Code

    The latest source code for Slixmpp may be found on the `Git repo
    <https://codeberg.org/poezio/slixmpp>`_. ::

        git clone https://codeberg.org/poezio/slixmpp

    An XMPP chat room is available for discussing and getting help with slixmpp.

    **Chat**
        `slixmpp@muc.poez.io <xmpp:slixmpp@muc.poez.io?join>`_

    **Reporting bugs**
        You can report bugs at http://codeberg.org/poezio/slixmpp/issues.

Slixmpp is an :ref:`MIT licensed <license>` XMPP library for Python 3.7+,

Slixmpp's design goals and philosphy are:

**Low number of dependencies**
    Installing and using Slixmpp should be as simple as possible, without
    having to deal with long dependency chains.

    As part of reducing the number of dependencies, some third party
    modules are included with Slixmpp in the ``thirdparty`` directory.
    Imports from this module first try to import an existing installed
    version before loading the packaged version, when possible.

**Every XEP as a plugin**
    Following Python's "batteries included" approach, the goal is to
    provide support for all currently active XEPs (final and draft). Since
    adding XEP support is done through easy to create plugins, the hope is
    to also provide a solid base for implementing and creating experimental
    XEPs.

**Rewarding to work with**
    As much as possible, Slixmpp should allow things to "just work" using
    sensible defaults and appropriate abstractions. XML can be ugly to work
    with, but it doesn't have to be that way.


Here's your first Slixmpp Bot:
--------------------------------

.. code-block:: python

    import asyncio
    import logging

    from slixmpp import ClientXMPP


    class EchoBot(ClientXMPP):

        def __init__(self, jid, password):
            ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.session_start)
            self.add_event_handler("message", self.message)

            # If you wanted more functionality, here's how to register plugins:
            # self.register_plugin('xep_0030') # Service Discovery
            # self.register_plugin('xep_0199') # XMPP Ping

            # Here's how to access plugins once you've registered them:
            # self['xep_0030'].add_feature('echo_demo')

        def session_start(self, event):
            self.send_presence()
            self.get_roster()

            # Most get_*/set_* methods from plugins use Iq stanzas, which
            # are sent asynchronously. You can almost always provide a
            # callback that will be executed when the reply is received.

        def message(self, msg):
            if msg['type'] in ('chat', 'normal'):
                msg.reply("Thanks for sending\n%(body)s" % msg).send()


    if __name__ == '__main__':
        # Ideally use optparse or argparse to get JID,
        # password, and log level.

        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)-8s %(message)s')

        xmpp = EchoBot('somejid@example.com', 'use_getpass')
        xmpp.connect()
        asyncio.get_event_loop().run_forever()


Documentation Index
-------------------

.. toctree::
    :maxdepth: 2

    getting_started/index
    howto/index
    api/index
    api/stanza/index
    event_index
    sleekxmpp
    architecture

Plugins
~~~~~~~
.. toctree::
    :maxdepth: 1

    api/plugins/index

Additional Info
---------------
.. toctree::
    :hidden:

    glossary
    license

* :ref:`license`
* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Slixmpp Credits
---------------

**Maintainers:**
    - Florent Le Coz (`louiz@louiz.org <xmpp:louiz@louiz.org?message>`_),
    - Mathieu Pasquet (`mathieui@mathieui.net <xmpp:mathieui@mathieui.net?message>`_),
    - Emmanuel Gil Peyrot (`Link mauve <xmpp:linkmauve@linkmauve.fr?message>`_)
    - Maxime Buquet (`pep <xmpp:pep@bouah.net?message>`_)

**Contributors:**
    - Sam Whited (`Sam Whited <mailto:sam@samwhited.com>`_)
    - Dan Sully (`Dan Sully <mailto:daniel@electricalrain.com>`_)
    - Gasper Zejn (`Gasper Zejn <mailto:zejn@kiberpipa.org>`_)
    - Krzysztof Kotlenga (`Krzysztof Kotlenga <mailto:pocek@users.sf.net>`_)
    - Tsukasa Hiiragi (`Tsukasa Hiiragi <mailto:bakalolka@gmail.com>`_)

SleekXMPP Credits
-----------------

Slixmpp is a friendly fork of `SleekXMPP <https://github.com/fritzy/SleekXMPP>`_
which goal is to use asyncio instead of threads to handle networking. See
:ref:`differences`. We are crediting SleekXMPP Authors here.

.. note::
    Those people made SleekXMPP, so you should not bother them if
    you have an issue with slixmpp. But it’s still fair to credit
    them for their work.


**Main Author:** `Nathan Fritz <http://andyet.net/team/fritzy>`_
     `fritzy@netflint.net <xmpp:fritzy@netflint.net?message>`_,
     `@fritzy <http://twitter.com/fritzy>`_

     Nathan is also the author of XMPPHP and `Seesmic-AS3-XMPP
     <http://code.google.com/p/seesmic-as3-xmpp/>`_, and a former member of the XMPP
     Council.

**Co-Author:** `Lance Stout <http://andyet.net/team/lance>`_
     `lancestout@gmail.com <xmpp:lancestout@gmail.com?message>`_,
     `@lancestout <http://twitter.com/lancestout>`_

Both Fritzy and Lance work for `&yet <http://andyet.net>`_, which specializes in
realtime web and XMPP applications.

    - `contact@andyet.net <mailto:contact@andyet.net>`_
    - `XMPP Consulting <http://xmppconsulting.com>`_

**Contributors:**
    - Brian Beggs (`macdiesel <http://github.com/macdiesel>`_)
    - Dann Martens (`dannmartens <http://github.com/dannmartens>`_)
    - Florent Le Coz (`louiz <http://github.com/louiz>`_)
    - Kevin Smith (`Kev <http://github.com/Kev>`_, http://kismith.co.uk)
    - Remko Tronçon (`remko <http://github.com/remko>`_, http://el-tramo.be)
    - Te-jé Rogers (`te-je <http://github.com/te-je>`_)
    - Thom Nichols (`tomstrummer <http://github.com/tomstrummer>`_)

