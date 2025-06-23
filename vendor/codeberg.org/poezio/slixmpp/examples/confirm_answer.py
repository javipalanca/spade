#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2015 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp.exceptions import XMPPError

log = logging.getLogger(__name__)


class AnswerConfirm(slixmpp.ClientXMPP):

    """
    A basic client demonstrating how to confirm or deny an HTTP request.
    """

    def __init__(self, jid, password, trusted):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("http_confirm", self.confirm)
        self.add_event_handler("session_start", self.start)

    def start(self, *args):
        self.make_presence().send()

    def prompt(self, stanza):
        confirm = stanza['confirm']
        print('Received confirm request %s from %s to access %s using '
                 'method %s' % (
                     confirm['id'], stanza['from'], confirm['url'],
                     confirm['method'])
                )
        result = input("Do you accept (y/N)? ")
        return 'y' == result.lower()

    def confirm(self, stanza):
        if self.prompt(stanza):
            reply = stanza.reply()
        else:
            reply = stanza.reply()
            reply.enable('error')
            reply['error']['type'] = 'auth'
            reply['error']['code'] = '401'
            reply['error']['condition'] = 'not-authorized'
        reply.append(stanza['confirm'])
        reply.send()

if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser()
    parser.add_argument("-q","--quiet", help="set logging to ERROR",
                        action="store_const",
                        dest="loglevel",
                        const=logging.ERROR,
                        default=logging.INFO)
    parser.add_argument("-d","--debug", help="set logging to DEBUG",
                        action="store_const",
                        dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")

    # Other options.
    parser.add_argument("-t", "--trusted", nargs='*',
                        help="List of trusted JIDs")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")

    xmpp = AnswerConfirm(args.jid, args.password, args.trusted)
    xmpp.register_plugin('xep_0070')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
