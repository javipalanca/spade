#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp.exceptions import XMPPError

log = logging.getLogger(__name__)


class MAM(slixmpp.ClientXMPP):

    """
    A basic client fetching mam archive messages
    """

    def __init__(self, jid, password, remote_jid, start):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.remote_jid = remote_jid
        self.start_date = start

        self.add_event_handler("session_start", self.start)

    async def start(self, *args):
        """
        Fetch mam results for the specified JID.
        Use RSM to paginate the results.
        """
        results = self.plugin['xep_0313'].retrieve(jid=self.remote_jid, iterator=True, rsm={'max': 10}, start=self.start_date)
        page = 1
        async for rsm in results:
            print('Page %d' % page)
            for msg in rsm['mam']['results']:
                forwarded = msg['mam_result']['forwarded']
                timestamp = forwarded['delay']['stamp']
                message = forwarded['stanza']
                print('[%s] %s: %s' % (timestamp, message['from'], message['body']))
            page += 1
        self.disconnect()

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

    # Other options
    parser.add_argument("-r", "--remote-jid", dest="remote_jid",
                        help="Remote JID")
    parser.add_argument("--start", help="Start date", default='2017-09-20T12:00:00Z')

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.remote_jid is None:
        args.remote_jid = input("Remote JID: ")
    if args.start is None:
        args.start = input("Start time: ")

    xmpp = MAM(args.jid, args.password, args.remote_jid, args.start)
    xmpp.register_plugin('xep_0313')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
