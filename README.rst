Slixmpp
#########

Slixmpp is an MIT licensed XMPP library for Python 3.7+. It is a fork of
SleekXMPP.

Slixmpp's goals is to only rewrite the core of the library (the low level
socket handling, the timers, the events dispatching) in order to remove all
threads.

Building
--------

Slixmpp uses rust to improve performance on critical modules.
Binaries may already be available for your platform in the form of
`wheels <https://peps.python.org/pep-0491/>`_ provided on PyPI or packages
for your linux distribution. If that is not the case,
`cargo <https://doc.rust-lang.org/cargo>`_
must be available in your path to build the
`extension module <https://docs.python.org/3/extending/extending.html>`_.

Documentation and Testing
-------------------------
Documentation can be found both inline in the code, and as a Sphinx project in ``/docs``.
To generate the Sphinx documentation, follow the commands below. The HTML output will
be in ``docs/_build/html``::

    cd docs
    make html
    open _build/html/index.html

To run the test suite for Slixmpp::

    python run_tests.py

Integration tests require the following environment variables to be set:::

    $CI_ACCOUNT1
    $CI_ACCOUNT1_PASSWORD
    $CI_ACCOUNT2
    $CI_ACCOUNT2_PASSWORD
    $CI_MUC_SERVER

where the account variables are JIDs of valid, existing accounts, and
the passwords are the account passwords. The MUC server must allow room
creation from those JIDs.

To run the integration test suite for Slixmpp::

    python run_integration_tests.py

The Slixmpp Boilerplate
-------------------------
Projects using Slixmpp tend to follow a basic pattern for setting up client/component
connections and configuration. Here is the gist of the boilerplate needed for a Slixmpp
based project. See the documentation or examples directory for more detailed archetypes for
Slixmpp projects::

    import asyncio
    import logging

    from slixmpp import ClientXMPP
    from slixmpp.exceptions import IqError, IqTimeout


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

            # If you are working with an OpenFire server, you will
            # need to use a different SSL version:
            # import ssl
            # self.ssl_version = ssl.PROTOCOL_SSLv3

        def session_start(self, event):
            self.send_presence()
            self.get_roster()

            # Most get_*/set_* methods from plugins use Iq stanzas, which
            # can generate IqError and IqTimeout exceptions
            #
            # try:
            #     self.get_roster()
            # except IqError as err:
            #     logging.error('There was an error getting the roster')
            #     logging.error(err.iq['error']['condition'])
            #     self.disconnect()
            # except IqTimeout:
            #     logging.error('Server is taking too long to respond')
            #     self.disconnect()

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


Slixmpp Credits
---------------

**Maintainers:**
    - Florent Le Coz (`louiz@louiz.org <xmpp:louiz@louiz.org?message>`_),
    - Mathieu Pasquet (`mathieui@mathieui.net <xmpp:mathieui@mathieui.net?message>`_),

**Contributors:**
    - Emmanuel Gil Peyrot (`Link mauve <xmpp:linkmauve@linkmauve.fr?message>`_)
    - Sam Whited (`Sam Whited <mailto:sam@samwhited.com>`_)
    - Dan Sully (`Dan Sully <mailto:daniel@electricalrain.com>`_)
    - Gasper Zejn (`Gasper Zejn <mailto:zejn@kiberpipa.org>`_)
    - Krzysztof Kotlenga (`Krzysztof Kotlenga <mailto:pocek@users.sf.net>`_)
    - Tsukasa Hiiragi (`Tsukasa Hiiragi <mailto:bakalolka@gmail.com>`_)
    - Maxime Buquet (`pep <xmpp:pep@bouah.net?message>`_)

Credits (SleekXMPP)
-------------------

**Main Author:** Nathan Fritz
    `fritzy@netflint.net <xmpp:fritzy@netflint.net?message>`_,
    `@fritzy <http://twitter.com/fritzy>`_

    Nathan is also the author of XMPPHP and `Seesmic-AS3-XMPP
    <http://code.google.com/p/seesmic-as3-xmpp/>`_, and a former member of
    the XMPP Council.

**Co-Author:** Lance Stout
    `lancestout@gmail.com <xmpp:lancestout@gmail.com?message>`_,
    `@lancestout <http://twitter.com/lancestout>`_

**Contributors:**
    - Brian Beggs (`macdiesel <http://github.com/macdiesel>`_)
    - Dann Martens (`dannmartens <http://github.com/dannmartens>`_)
    - Florent Le Coz (`louiz <http://github.com/louiz>`_)
    - Kevin Smith (`Kev <http://github.com/Kev>`_, http://kismith.co.uk)
    - Remko Tronçon (`remko <http://github.com/remko>`_, http://el-tramo.be)
    - Te-jé Rogers (`te-je <http://github.com/te-je>`_)
    - Thom Nichols (`tomstrummer <http://github.com/tomstrummer>`_)
