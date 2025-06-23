#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp


class CommandUserBot(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that uses the adhoc command
    provided by the adhoc_provider.py example.
    """

    def __init__(self, jid, password, other, greeting):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.command_provider = other
        self.greeting = greeting

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()

        # We first create a session dictionary containing:
        #   'next'  -- the handler to execute on a successful response
        #   'error' -- the handler to execute if an error occurs

        # The session may also contain custom data.

        session = {'greeting': self.greeting,
                   'next': self._command_start,
                   'error': self._command_error}

        self['xep_0050'].start_command(jid=self.command_provider,
                                       node='greeting',
                                       session=session)

    def message(self, msg):
        """
        Process incoming message stanzas.

        Arguments:
            msg -- The received message stanza.
        """
        logging.info(msg['body'])

    def _command_start(self, iq, session):
        """
        Process the initial command result.

        Arguments:
            iq      -- The iq stanza containing the command result.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """

        # The greeting command provides a form with a single field:
        # <x xmlns="jabber:x:data" type="form">
        #   <field var="greeting"
        #          type="text-single"
        #          label="Your greeting" />
        # </x>

        form = self['xep_0004'].make_form(ftype='submit')
        form.addField(var='greeting',
                      value=session['greeting'])

        session['payload'] = form

        # We don't need to process the next result.
        session['next'] = None

        # Other options include using:
        # continue_command() -- Continue to the next step in the workflow
        # cancel_command()   -- Stop command execution.

        self['xep_0050'].complete_command(session)

    def _command_error(self, iq, session):
        """
        Process an error that occurs during command execution.

        Arguments:
            iq      -- The iq stanza containing the error.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        logging.error("COMMAND: %s %s" % (iq['error']['condition'],
                                          iq['error']['text']))

        # Terminate the command's execution and clear its session.
        # The session will automatically be cleared if no error
        # handler is provided.
        self['xep_0050'].terminate_command(session)
        self.disconnect()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser()

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
    parser.add_argument("-o", "--other", dest="other",
                        help="JID providing commands")
    parser.add_argument("-g", "--greeting", dest="greeting",
                        help="Greeting")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.other is None:
        args.other = input("JID Providing Commands: ")
    if args.greeting is None:
        args.greeting = input("Greeting: ")

    # Setup the CommandBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = CommandUserBot(args.jid, args.password, args.other, args.greeting)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0050') # Adhoc Commands

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
