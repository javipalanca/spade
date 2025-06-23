#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Implementation of HTTP over XMPP transport
# http://xmpp.org/extensions/xep-0332.html
# Copyright (C) 2015 Riptide IO, sangeeth@riptideio.com
# This file is part of slixmpp.
# See the file LICENSE for copying permission.

import asyncio
from slixmpp import ClientXMPP

from argparse import ArgumentParser
import logging
import getpass


class HTTPOverXMPPClient(ClientXMPP):
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.register_plugin('xep_0332')    # HTTP over XMPP Transport
        self.add_event_handler(
            'session_start', self.session_start
        )
        self.add_event_handler('http_request', self.http_request_received)
        self.add_event_handler('http_response', self.http_response_received)

    def http_request_received(self, iq):
        pass

    def http_response_received(self, iq):
        print('HTTP Response Received : %s' % iq)
        print('From    : %s' %  iq['from'])
        print('To      : %s' % iq['to'])
        print('Type    : %s' % iq['type'])
        print('Headers : %s' % iq['resp']['headers'])
        print('Code    : %s' % iq['resp']['code'])
        print('Message : %s' % iq['resp']['message'])
        print('Data    : %s' % iq['resp']['data'])

    def session_start(self, event):
        # TODO: Fill in the blanks
        self['xep_0332'].send_request(
            to='?', method='?', resource='?', headers={}
        )
        self.disconnect()


if __name__ == '__main__':

    #
    # NOTE: To run this example, fill up the blanks in session_start() and
    #       use the following command.
    #
    # ./http_over_xmpp.py -J <jid> -P <pwd> -i <ip> -p <port> [-v]
    #

    parser = ArgumentParser()

    # Output verbosity options.
    parser.add_argument(
        '-v', '--verbose', help='set logging to DEBUG', action='store_const',
        dest='loglevel', const=logging.DEBUG, default=logging.ERROR
    )

    # JID and password options.
    parser.add_argument('-J', '--jid', dest='jid', help='JID')
    parser.add_argument('-P', '--password', dest='password', help='Password')

    # XMPP server ip and port options.
    parser.add_argument(
        '-i', '--ipaddr', dest='ipaddr',
        help='IP Address of the XMPP server', default=None
    )
    parser.add_argument(
        '-p', '--port', dest='port',
        help='Port of the XMPP server', default=None
    )

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = input('Username: ')
    if args.password is None:
        args.password = getpass.getpass('Password: ')

    xmpp = HTTPOverXMPPClient(args.jid, args.password)
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
