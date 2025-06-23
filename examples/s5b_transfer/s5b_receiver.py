#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2015  Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp


class S5BReceiver(slixmpp.ClientXMPP):

    """
    A basic example of creating and using a SOCKS5 bytestream.
    """

    def __init__(self, jid, password, filename):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.file = open(filename, 'wb')

        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)

    def stream_opened(self, sid):
        logging.info('Stream opened. %s', sid)

    def stream_data(self, data):
        self.file.write(data)

    def stream_closed(self, exception):
        logging.info('Stream closed. %s', exception)
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

    # Setup the S5BReceiver and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = S5BReceiver(args.jid, args.password, args.filename)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0065', {
        'auto_accept': True
    }) # SOCKS5 Bytestreams

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
