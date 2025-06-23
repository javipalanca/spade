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
from slixmpp import Iq
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream import register_stanza_plugin

from stanza import Action


class ActionUserBot(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that sends a custom action stanza
    to another client.
    """

    def __init__(self, jid, password, other):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.action_provider = other

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

        register_stanza_plugin(Iq, Action)

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

        await self.send_custom_iq()

    async def send_custom_iq(self):
        """Create and send two custom actions.

        If the first action was successful, then send
        a shutdown command and then disconnect.
        """
        iq = self.Iq()
        iq['to'] = self.action_provider
        iq['type'] = 'set'
        iq['action']['method'] = 'is_prime'
        iq['action']['param'] = '2'

        try:
            resp = await iq.send()
            if resp['action']['status'] == 'done':
                #sending bye
                iq2 = self.Iq()
                iq2['to'] = self.action_provider
                iq2['type'] = 'set'
                iq2['action']['method'] = 'bye'
                await iq2.send()

                self.disconnect()
        except XMPPError:
            print('There was an error sending the custom action.')

    def message(self, msg):
        """
        Process incoming message stanzas.

        Arguments:
            msg -- The received message stanza.
        """
        logging.info(msg['body'])

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
                        help="JID providing custom stanza")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.other is None:
        args.other = input("JID Providing custom stanza: ")

    # Setup the CommandBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = ActionUserBot(args.jid, args.password, args.other)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0050') # Adhoc Commands

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
