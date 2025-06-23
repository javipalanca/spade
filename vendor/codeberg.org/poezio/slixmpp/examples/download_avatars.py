#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp.exceptions import XMPPError
from slixmpp import asyncio


FILE_TYPES = {
    'image/png': 'png',
    'image/gif': 'gif',
    'image/jpeg': 'jpg'
}


class AvatarDownloader(slixmpp.ClientXMPP):

    """
    A basic script for downloading the avatars for a user's contacts.
    """

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("changed_status", self.wait_for_presences)

        self.add_event_handler('vcard_avatar_update', self.on_vcard_avatar)
        self.add_event_handler('avatar_metadata_publish', self.on_avatar)

        self.received = set()
        self.presences_received = asyncio.Event()
        self.roster_received = asyncio.Event()

    def roster_received_cb(self, event):
        self.roster_received.set()
        self.presences_received.clear()

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
        self.get_roster(callback=self.roster_received_cb)

        print('Waiting for presence updates...\n')
        await self.roster_received.wait()
        print('Roster received')
        await self.presences_received.wait()
        self.disconnect()

    async def on_vcard_avatar(self, pres):
        print("Received vCard avatar update from %s" % pres['from'].bare)
        try:
            result = await self['xep_0054'].get_vcard(pres['from'].bare, cached=True,
                                                           timeout=5)
        except XMPPError:
            print("Error retrieving avatar for %s" % pres['from'])
            return
        avatar = result['vcard_temp']['PHOTO']

        filetype = FILE_TYPES.get(avatar['TYPE'], 'png')
        filename = 'vcard_avatar_%s_%s.%s' % (
                pres['from'].bare,
                pres['vcard_temp_update']['photo'],
                filetype)
        with open(filename, 'wb+') as img:
            img.write(avatar['BINVAL'])

    async def on_avatar(self, msg):
        print("Received avatar update from %s" % msg['from'])
        metadata = msg['pubsub_event']['items']['item']['avatar_metadata']
        for info in metadata['items']:
            if not info['url']:
                try:
                    result = await self['xep_0084'].retrieve_avatar(msg['from'].bare, info['id'],
                                                                         timeout=5)
                except XMPPError:
                    print("Error retrieving avatar for %s" % msg['from'])
                    return

                avatar = result['pubsub']['items']['item']['avatar_data']

                filetype = FILE_TYPES.get(metadata['type'], 'png')
                filename = 'avatar_%s_%s.%s' % (msg['from'].bare, info['id'], filetype)
                with open(filename, 'wb+') as img:
                    img.write(avatar['value'])
            else:
                # We could retrieve the avatar via HTTP, etc here instead.
                pass

    def wait_for_presences(self, pres):
        """
        Wait to receive updates from all roster contacts.
        """
        self.received.add(pres['from'].bare)
        print((len(self.received), len(self.client_roster.keys())))
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser()
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

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")

    xmpp = AvatarDownloader(args.jid, args.password)
    xmpp.register_plugin('xep_0054')
    xmpp.register_plugin('xep_0153')
    xmpp.register_plugin('xep_0084')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
