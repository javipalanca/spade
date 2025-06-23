#!/usr/bin/env python3

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp.xmlstream import ET, tostring
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream.handler import Callback


class PubsubEvents(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        self.add_event_handler('session_start', self.start)

        # Some services may require configuration to allow
        # sending delete, configuration, or subscription  events.
        self.add_event_handler('pubsub_publish', self._publish)
        self.add_event_handler('pubsub_retract', self._retract)
        self.add_event_handler('pubsub_purge', self._purge)
        self.add_event_handler('pubsub_delete', self._delete)
        self.add_event_handler('pubsub_config', self._config)
        self.add_event_handler('pubsub_subscription', self._subscription)

        # Want to use nicer, more specific pubsub event names?
        # self['xep_0060'].map_node_event('node_name', 'event_prefix')
        # self.add_event_handler('event_prefix_publish', handler)
        # self.add_event_handler('event_prefix_retract', handler)
        # self.add_event_handler('event_prefix_purge', handler)
        # self.add_event_handler('event_prefix_delete', handler)

    async def start(self, event):
        await self.get_roster()
        self.send_presence()

    def _publish(self, msg):
        """Handle receiving a publish item event."""
        print('Published item %s to %s:' % (
            msg['pubsub_event']['items']['item']['id'],
            msg['pubsub_event']['items']['node']))
        data = msg['pubsub_event']['items']['item']['payload']
        if data is not None:
            print(tostring(data))
        else:
            print('No item content')

    def _retract(self, msg):
        """Handle receiving a retract item event."""
        print('Retracted item %s from %s' % (
            msg['pubsub_event']['items']['retract']['id'],
            msg['pubsub_event']['items']['node']))

    def _purge(self, msg):
        """Handle receiving a node purge event."""
        print('Purged all items from %s' % (
            msg['pubsub_event']['purge']['node']))

    def _delete(self, msg):
        """Handle receiving a node deletion event."""
        print('Deleted node %s' % (
           msg['pubsub_event']['delete']['node']))

    def _config(self, msg):
        """Handle receiving a node configuration event."""
        print('Configured node %s:' % (
            msg['pubsub_event']['configuration']['node']))
        print(msg['pubsub_event']['configuration']['form'])

    def _subscription(self, msg):
        """Handle receiving a node subscription event."""
        print('Subscription change for node %s:' % (
            msg['pubsub_event']['subscription']['node']))
        print(msg['pubsub_event']['subscription'])


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

    logging.info("Run this in conjunction with the pubsub_client.py " + \
                 "example to watch events happen as you give commands.")

    # Setup the PubsubEvents listener
    xmpp = PubsubEvents(args.jid, args.password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
