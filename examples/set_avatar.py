#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import os
import imghdr
import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp.exceptions import XMPPError

class AvatarSetter(slixmpp.ClientXMPP):

    """
    A basic script for downloading the avatars for a user's contacts.
    """

    def __init__(self, jid, password, filepath):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)

        self.filepath = filepath

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

        avatar_file = None
        try:
            avatar_file = open(os.path.expanduser(self.filepath), 'rb')
        except IOError:
            print('Could not find file: %s' % self.filepath)
            return self.disconnect()

        avatar = avatar_file.read()

        avatar_type = 'image/%s' % imghdr.what('', avatar)
        avatar_id = self['xep_0084'].generate_id(avatar)
        avatar_bytes = len(avatar)

        avatar_file.close()

        used_xep84 = False

        print('Publish XEP-0084 avatar data')
        result = await self['xep_0084'].publish_avatar(avatar)
        if isinstance(result, XMPPError):
            print('Could not publish XEP-0084 avatar')
        else:
            used_xep84 = True

        print('Update vCard with avatar')
        result = await self['xep_0153'].set_avatar(avatar=avatar, mtype=avatar_type)
        if isinstance(result, XMPPError):
            print('Could not set vCard avatar')

        if used_xep84:
            print('Advertise XEP-0084 avatar metadata')
            result = await self['xep_0084'].publish_avatar_metadata([
                {'id': avatar_id,
                 'type': avatar_type,
                 'bytes': avatar_bytes}
                # We could advertise multiple avatars to provide
                # options in image type, source (HTTP vs pubsub),
                # size, etc.
                # {'id': ....}
            ])
            if isinstance(result, XMPPError):
                print('Could not publish XEP-0084 metadata')

        print('Wait for presence updates to propagate...')
        self.schedule('end', 5, self.disconnect, kwargs={'wait': True})


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
    parser.add_argument("-f", "--file", dest="filepath",
                        help="path to the avatar file")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.filepath is None:
        args.filepath = input("Avatar file location: ")

    xmpp = AvatarSetter(args.jid, args.password, args.filepath)
    xmpp.register_plugin('xep_0054')
    xmpp.register_plugin('xep_0153')
    xmpp.register_plugin('xep_0084')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
