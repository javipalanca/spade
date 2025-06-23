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
from slixmpp.exceptions import IqError, IqTimeout


class Disco(slixmpp.ClientXMPP):

    """
    A demonstration for using basic service discovery.

    Send a disco#info and disco#items request to a JID/node combination,
    and print out the results.

    May also request only particular info categories such as just features,
    or just items.
    """

    def __init__(self, jid, password, target_jid, target_node='', get=''):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # Using service discovery requires the XEP-0030 plugin.
        self.register_plugin('xep_0030')

        self.get = get
        self.target_jid = target_jid
        self.target_node = target_node

        # Values to control which disco entities are reported
        self.info_types = ['', 'all', 'info', 'identities', 'features']
        self.identity_types = ['', 'all', 'info', 'identities']
        self.feature_types = ['', 'all', 'info', 'features']
        self.items_types = ['', 'all', 'items']


        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        In this case, we send disco#info and disco#items
        stanzas to the requested JID and print the results.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        await self.get_roster()
        self.send_presence()

        try:
            if self.get in self.info_types:
                # function using the callback parameter.
                info = await self['xep_0030'].get_info(jid=self.target_jid,
                                                            node=self.target_node)
            if self.get in self.items_types:
                # The same applies from above. Listen for the
                # disco_items event or pass a callback function
                # if you need to process a non-blocking request.
                items = await self['xep_0030'].get_items(jid=self.target_jid,
                                                              node=self.target_node)
            if self.get not in self.info_types and self.get not in self.items_types:
                logging.error("Invalid disco request type.")
                return
        except IqError as e:
            logging.error("Entity returned an error: %s" % e.iq['error']['condition'])
        except IqTimeout:
            logging.error("No response received.")
        else:
            header = 'XMPP Service Discovery: %s' % self.target_jid
            print(header)
            print('-' * len(header))
            if self.target_node != '':
                print('Node: %s' % self.target_node)
                print('-' * len(header))

            if self.get in self.identity_types:
                print('Identities:')
                for identity in info['disco_info']['identities']:
                    print('  - %s' % str(identity))

            if self.get in self.feature_types:
                print('Features:')
                for feature in info['disco_info']['features']:
                    print('  - %s' % feature)

            if self.get in self.items_types:
                print('Items:')
                for item in items['disco_items']['items']:
                    print('  - %s' % str(item))
        finally:
            self.disconnect()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser(description=Disco.__doc__)

    parser.add_argument("-q","--quiet", help="set logging to ERROR",
                        action="store_const",
                        dest="loglevel",
                        const=logging.ERROR,
                        default=logging.ERROR)
    parser.add_argument("-d","--debug", help="set logging to DEBUG",
                        action="store_const",
                        dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.ERROR)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")
    parser.add_argument("query", choices=["all", "info", "items", "identities", "features"])
    parser.add_argument("target_jid")
    parser.add_argument("node", nargs='?')

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")

    # Setup the Disco browser.
    xmpp = Disco(args.jid, args.password, args.target_jid, args.node, args.query)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
