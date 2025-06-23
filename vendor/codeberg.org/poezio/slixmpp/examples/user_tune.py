#!/usr/bin/env python3

import sys
import logging
from getpass import getpass
from argparse import ArgumentParser

try:
    from appscript import *
except ImportError:
    print('This demo requires the appscript package to interact with iTunes.')
    sys.exit()

import asyncio
from slixmpp import ClientXMPP


class TuneBot(ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        # Check for the current song every 5 seconds.
        self.schedule('Check Current Tune', 5, self._update_tune, repeat=True)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('user_tune_publish', self.user_tune_publish)

        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0115')
        self.register_plugin('xep_0118')
        self.register_plugin('xep_0128')
        self.register_plugin('xep_0163')

        self.current_tune = None

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self['xep_0115'].update_caps()

    def _update_tune(self):
        itunes_count = app('System Events').processes[its.name == 'iTunes'].count()
        if itunes_count > 0:
            iTunes = app('iTunes')
            if iTunes.player_state.get() == k.playing:
                track = iTunes.current_track.get()
                length = track.time.get()
                if ':' in length:
                    minutes, secs = map(int, length.split(':'))
                    secs += minutes * 60
                else:
                    secs = int(length)

                artist = track.artist.get()
                title = track.name.get()
                source = track.album.get()
                rating = track.rating.get() / 10

                tune = (artist, secs, rating, source, title)
                if tune != self.current_tune:
                    self.current_tune = tune

                    # We have a new song playing, so publish it.
                    self['xep_0118'].publish_tune(
                            artist=artist,
                            length=secs,
                            title=title,
                            rating=rating,
                            source=source)
            else:
                # No song is playing, clear the user tune.
                tune = None
                if tune != self.current_tune:
                    self.current_tune = tune
                    self['xep_0118'].stop()

    def user_tune_publish(self, msg):
        tune = msg['pubsub_event']['items']['item']['tune']
        print("%s is listening to: %s" % (msg['from'], tune['title']))


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

    xmpp = TuneBot(args.jid, args.password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
