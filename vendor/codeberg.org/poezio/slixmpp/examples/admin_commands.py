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


class AdminCommands(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that uses admin commands to
    add a new user to a server.
    """

    def __init__(self, jid, password, command):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.command = command

        self.add_event_handler("session_start", self.start)

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

        def command_success(iq, session):
            print('Command completed')
            if iq['command']['form']:
                for var, field in iq['command']['form']['fields'].items():
                    print('%s: %s' % (var, field['value']))
            if iq['command']['notes']:
                print('Command Notes:')
                for note in iq['command']['notes']:
                    print('%s: %s' % note)
            self.disconnect()

        def command_error(iq, session):
            print('Error completing command')
            print('%s: %s' % (iq['error']['condition'],
                              iq['error']['text']))
            self['xep_0050'].terminate_command(session)
            self.disconnect()

        def process_form(iq, session):
            form = iq['command']['form']
            answers = {}
            for var, field in form['fields'].items():
                if var != 'FORM_TYPE':
                    if field['type'] == 'boolean':
                        answers[var] = input('%s (y/n): ' % field['label'])
                        if answers[var].lower() in ('1', 'true', 'y', 'yes'):
                            answers[var] = '1'
                        else:
                            answers[var] = '0'
                    else:
                        answers[var] = input('%s: ' % field['label'])
                else:
                    answers['FORM_TYPE'] = field['value']
            form['type'] = 'submit'
            form['values'] = answers

            session['next'] = command_success
            session['payload'] = form

            self['xep_0050'].complete_command(session)

        session = {'next': process_form,
                   'error': command_error}

        command = self.command.replace('-', '_')
        handler = getattr(self['xep_0133'], command, None)

        if handler:
            handler(session={
                'next': process_form,
                'error': command_error
            })
        else:
            print('Invalid command name: %s' % self.command)
            self.disconnect()


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
    parser.add_argument("-c", "--command", dest="command",
                        help="admin command to use")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    if args.command is None:
        args.command = input("Admin command: ")

    # Setup the CommandBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = AdminCommands(args.jid, args.password, args.command)
    xmpp.register_plugin('xep_0133') # Service Administration

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
