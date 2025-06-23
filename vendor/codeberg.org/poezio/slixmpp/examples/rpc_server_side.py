#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Dann Martens
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import asyncio
import logging
from argparse import ArgumentParser
from getpass import getpass
from slixmpp.jid import JID
from slixmpp.plugins.xep_0009.remote import Endpoint, remote, Remote, \
    ANY_ALL

class Thermostat(Endpoint):

    def FQN(self):
        return 'thermostat'

    def __init__(self, initial_temperature):
        self._temperature = initial_temperature
        self._event = asyncio.Event()

    @remote
    def set_temperature(self, temperature):
        print("Setting temperature to %s" % temperature)
        self._temperature = temperature

    @remote
    def get_temperature(self):
        return self._temperature

    @remote(False)
    def release(self):
        self._event.set()

    async def wait_for_release(self):
        await self._event.wait()


async def main(jid: JID, password: str):
    session = await Remote.new_session(jid, password)
    thermostat = session.new_handler(ANY_ALL, Thermostat, 18)
    await thermostat.wait_for_release()
    session.close()

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

    asyncio.run(main(JID(args.jid), args.password))
