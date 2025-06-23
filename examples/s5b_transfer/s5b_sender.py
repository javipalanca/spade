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
from slixmpp.exceptions import IqError, IqTimeout


class S5BSender(slixmpp.ClientXMPP):

    """
    A basic example of creating and using a SOCKS5 bytestream.
    """

    def __init__(self, jid, password, receiver, filename):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.receiver = receiver

        self.file = open(filename, 'rb')

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use.
        self.add_event_handler("session_start", self.start)

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

        try:
            # Open the S5B stream in which to write to.
            proxy = await self['xep_0065'].handshake(self.receiver)

            # Send the entire file.
            while True:
                data = self.file.read(1048576)
                if not data:
                    break
                await proxy.write(data)

            # And finally close the stream.
            proxy.transport.write_eof()
        except (IqError, IqTimeout):
            print('File transfer errored')
        else:
            print('File transfer finished')
        finally:
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
    parser.add_argument("-r", "--receiver", dest="receiver",
                        help="JID of the receiver")
    parser.add_argument("-f", "--file", dest="filename",
                        help="file to send")
    parser.add_argument("-m", "--use-messages", action="store_true",
                        help="use messages instead of iqs for file transfer")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.receiver is None:
        args.receiver = input("Receiver: ")
    if args.filename is None:
        args.filename = input("File path: ")

    # Setup the S5BSender and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = S5BSender(args.jid, args.password, args.receiver, args.filename)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0065') # SOCKS5 Bytestreams

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
