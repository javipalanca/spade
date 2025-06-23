#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp


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
parser.add_argument("--oldjid", dest="old_jid",
                    help="JID of the old account")
parser.add_argument("--oldpassword", dest="old_password",
                    help="password of the old account")

parser.add_argument("--newjid", dest="new_jid",
                    help="JID of the old account")
parser.add_argument("--newpassword", dest="new_password",
                    help="password of the old account")


args = parser.parse_args()

# Setup logging.
logging.basicConfig(level=args.loglevel,
                    format='%(levelname)-8s %(message)s')

if args.old_jid is None:
    args.old_jid = input("Old JID: ")
if args.old_password is None:
    args.old_password = getpass("Old Password: ")

if args.new_jid is None:
    args.new_jid = input("New JID: ")
if args.new_password is None:
    args.new_password = getpass("New Password: ")


old_xmpp = slixmpp.ClientXMPP(args.old_jid, args.old_password)

# If you are connecting to Facebook and wish to use the
# X-FACEBOOK-PLATFORM authentication mechanism, you will need
# your API key and an access token. Then you'll set:
# xmpp.credentials['api_key'] = 'THE_API_KEY'
# xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

# If you are connecting to MSN, then you will need an
# access token, and it does not matter what JID you
# specify other than that the domain is 'messenger.live.com',
# so '_@messenger.live.com' will work. You can specify
# the access token as so:
# xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

# If you are working with an OpenFire server, you may need
# to adjust the SSL version used:
# xmpp.ssl_version = ssl.PROTOCOL_SSLv3

# If you want to verify the SSL certificates offered by a server:
# xmpp.ca_certs = "path/to/ca/cert"

roster = []

async def on_session(event):
    roster.append(await old_xmpp.get_roster())
    old_xmpp.disconnect()
old_xmpp.add_event_handler('session_start', on_session)

if old_xmpp.connect():
    asyncio.get_event_loop().run_until_complete(old_xmpp.disconnected)

if not roster:
    print('No roster to migrate')
    sys.exit()

new_xmpp = slixmpp.ClientXMPP(args.new_jid, args.new_password)
async def on_session2(event):
    await new_xmpp.get_roster()
    new_xmpp.send_presence()

    logging.info(roster[0])
    data = roster[0]['roster']['items']
    logging.info(data)

    for jid, item in data.items():
        if item['subscription'] != 'none':
            new_xmpp.send_presence(ptype='subscribe', pto=jid)
        await new_xmpp.update_roster(
            jid,
            name=item['name'],
            groups=item['groups']
        )
    new_xmpp.disconnect()
new_xmpp.add_event_handler('session_start', on_session2)

new_xmpp.connect()
asyncio.get_event_loop().run_until_complete(new_xmpp.disconnected)
