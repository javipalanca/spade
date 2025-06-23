#!/usr/bin/env python3

import sys
import logging
from getpass import getpass
from argparse import ArgumentParser

try:
    import json
except ImportError:
    import simplejson as json

try:
    import requests
except ImportError:
    print('This demo requires the requests package for using HTTP.')
    sys.exit()

import asyncio
from slixmpp import ClientXMPP


class LocationBot(ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('user_location_publish',
                               self.user_location_publish)

        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0115')
        self.register_plugin('xep_0128')
        self.register_plugin('xep_0163')
        self.register_plugin('xep_0080')

        self.current_tune = None

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self['xep_0115'].update_caps()

        print("Using freegeoip.net to get geolocation.")
        r = requests.get('http://freegeoip.net/json/')
        try:
            data = json.loads(r.text)
        except:
            print("Could not retrieve user location.")
            self.disconnect()
            return

        self['xep_0080'].publish_location(
                lat=data['latitude'],
                lon=data['longitude'],
                locality=data['city'],
                region=data['region_name'],
                country=data['country_name'],
                countrycode=data['country_code'],
                postalcode=data['zipcode'])

    def user_location_publish(self, msg):
        geo = msg['pubsub_event']['items']['item']['geoloc']
        print("%s is at:" % msg['from'])
        for key, val in geo.values.items():
            if val:
                print("  %s: %s" % (key, val))


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

    xmpp = LocationBot(args.jid, args.password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
