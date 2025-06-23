#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp


class MIXBot(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password, room, nick):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.rooms = set()
        self.nick = nick

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The mix_message event is triggered whenever a message
        # stanza is received from any chat room.
        self.add_event_handler("mix_message", self.mix_message)

        # The mix_participant_info_publish event is triggered whenever
        # an occupant joins or leaves the channel (not linked to
        # actual presence)
        self.add_event_handler("mix_participant_info_publish",
                               self.mix_joined)


    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        """
        # The goal here is to fetch the already joined MIX channels
        # which are present in the roster.
        _, mix_rooms = await self.plugin['xep_0405'].get_mix_roster()
        for room in mix_rooms:
            self.rooms.add(room['jid'])
        self.send_presence()
        if self.room not in self.rooms:
            # If we are not joined, we need to. This will carry over
            # the next restarts
            await self.plugin['xep_0405'].join_channel(
                self.room,
                self.nick,
            )

    def mix_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['mix']['nick'] != self.nick and self.nick in msg['body']:
            self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mix']['nick'],
                              mtype='groupchat')

    def mix_joined(self, event):
        """
        We receive a publish event whenever someone joins the MIX channel.
        It contains the nickname of the new participant, and the JID when
        the channel is not a "JID Hidden channel".
        """
        participant = event['pubsub_event']['items']['item']['mix_participant']
        if participant['nick'] != self.nick:
            self.send_message(mto=event['from'].bare,
                              mbody="Hello, %s" % participant['nick'],
                              mtype='groupchat')


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
    parser.add_argument("-r", "--room", dest="room",
                        help="MIX channel to join")
    parser.add_argument("-n", "--nick", dest="nick",
                        help="MIX nickname")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.room is None:
        args.room = input("MIX channel: ")
    if args.nick is None:
        args.nick = input("MIX nickname: ")

    # Setup the MIXBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = MIXBot(args.jid, args.password, args.room, args.nick)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0369') # MIX Core
    xmpp.register_plugin('xep_0405') # MIX PAM

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
