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
from slixmpp.plugins.xep_0009.remote import Endpoint, remote, Remote

class Thermostat(Endpoint):

    def FQN(self):
        return 'thermostat'

    def __init__(self, initial_temperature):
        pass

    @remote
    def set_temperature(self, temperature):
        return NotImplemented

    @remote
    def get_temperature(self):
        return NotImplemented

    @remote(False)
    def release(self):
        return NotImplemented


async def main(jid: JID, password: str, target_jid: JID):

    session = await Remote.new_session(jid, password)
    thermostat = session.new_proxy(target_jid, Thermostat)

    print("Current temperature is %s" % await thermostat.get_temperature())

    await thermostat.set_temperature(20)

    print("Current temperature is %s" % await thermostat.get_temperature())

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
    parser.add_argument("-t", "--target-jid", dest="target_jid",
                        help="target JID to use")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.target_jid is None:
        args.target_jid = input("Target jid: ")

    asyncio.run(main(JID(args.jid), args.password, args.target_jid))
