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

from slixmpp import ClientXMPP, Iq
from slixmpp.exceptions import IqError, IqTimeout, XMPPError
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from stanza import Action


class ActionBot(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that receives a custom stanza
    from another client.
    """

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        self.register_handler(
          Callback('Some custom iq',
            StanzaPath('iq@type=set/action'),
            self._handle_action))

        self.add_event_handler('custom_action',
                self._handle_action_event)

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
        self.get_roster()

    def _handle_action(self, iq):
        """
        Raise an event for the stanza so that it can be processed in its
        own thread without blocking the main stanza processing loop.
        """
        self.event('custom_action', iq)

    async def _handle_action_event(self, iq):
        """
        Respond to the custom action event.
        """
        method = iq['action']['method']
        param = iq['action']['param']

        if method == 'is_prime' and param == '2':
            print("got message: %s" % iq)
            rep = iq.reply()
            rep['action']['status'] = 'done'
            await rep.send()
        elif method == 'bye':
            print("got message: %s" % iq)
            rep = iq.reply()
            rep['action']['status'] = 'done'
            await rep.send()
            self.disconnect()
        else:
            print("got message: %s" % iq)
            rep = iq.reply()
            rep['action']['status'] = 'error'
            await rep.send()

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

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")

    # Setup the CommandBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = ActionBot(args.jid, args.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0050') # Adhoc Commands
    xmpp.register_plugin('xep_0199', {'keepalive': True, 'frequency':15})

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
