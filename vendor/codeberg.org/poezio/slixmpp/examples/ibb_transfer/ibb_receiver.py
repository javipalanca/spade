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


class IBBReceiver(slixmpp.ClientXMPP):

    """
    A basic example of creating and using an in-band bytestream.
    """

    def __init__(self, jid, password, filename):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.file = open(filename, 'wb')

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        self.add_event_handler("ibb_stream_start", self.stream_opened)
        self.add_event_handler("ibb_stream_data", self.stream_data)
        self.add_event_handler("ibb_stream_end", self.stream_closed)

    def start(self, event):
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

    def stream_opened(self, stream):
        print('Stream opened: %s from %s' % (stream.sid, stream.peer_jid))

    def stream_data(self, stream):
        self.file.write(stream.read())

    def stream_closed(self, stream):
        print('Stream closed: %s from %s' % (stream.sid, stream.peer_jid))
        self.file.close()
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
    parser.add_argument("-o", "--out", dest="filename",
                        help="file to save to")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.filename is None:
        args.filename = input("File path: ")

    # Setup the IBBReceiver and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = IBBReceiver(args.jid, args.password, args.filename)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0047', {
        'auto_accept': True
    }) # In-band Bytestreams

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
