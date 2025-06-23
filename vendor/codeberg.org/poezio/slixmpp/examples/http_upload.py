#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from typing import Optional

import sys
import logging
from pathlib import Path
from getpass import getpass
from argparse import ArgumentParser

import asyncio
import slixmpp
from slixmpp import JID
from slixmpp.exceptions import IqTimeout

log = logging.getLogger(__name__)


class HttpUpload(slixmpp.ClientXMPP):

    """
    A basic client asking an entity if they confirm the access to an HTTP URL.
    """

    def __init__(
        self,
        jid: JID,
        password: str,
        recipient: JID,
        filename: Path,
        domain: Optional[JID] = None,
        encrypted: bool = False,
    ):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.filename = filename
        self.domain = domain
        self.encrypted = encrypted

        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        log.info('Uploading file %s...', self.filename)
        try:
            upload_file = self['xep_0363'].upload_file
            if self.encrypted and not self['xep_0454']:
                print(
                    'The xep_0454 module isn\'t available. '
                    'Ensure you have \'cryptography\' '
                    'from extras_require installed.',
                    file=sys.stderr,
                )
                return
            elif self.encrypted:
                upload_file = self['xep_0454'].upload_file
            url = await upload_file(
                self.filename, domain=self.domain, timeout=10,
            )
        except IqTimeout:
            raise TimeoutError('Could not send message in time')
        log.info('Upload success!')

        log.info('Sending file to %s', self.recipient)
        html = (
            f'<body xmlns="http://www.w3.org/1999/xhtml">'
            f'<a href="{url}">{url}</a></body>'
        )
        message = self.make_message(mto=self.recipient, mbody=url, mhtml=html)
        message['oob']['url'] = url
        message.send()
        self.disconnect()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser()
    parser.add_argument("-q","--quiet", help="set logging to ERROR",
                        action="store_const",
                        dest="loglevel",
                        const=logging.ERROR,
                        default=logging.INFO)
    parser.add_argument("-d","--debug", help="set logging to DEBUG",
                        action="store_const",
                        dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")

    # Other options.
    parser.add_argument("-r", "--recipient", required=True,
                        help="Recipient JID")
    parser.add_argument("-f", "--file", required=True,
                        help="File to send")
    parser.add_argument("--domain",
                        help="Domain to use for HTTP File Upload (leave out for your own server’s)")

    parser.add_argument("-e", "--encrypt", dest="encrypted",
                        help="Whether to encrypt", action="store_true",
                        default=False)

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = JID(input("Username: "))
    if args.password is None:
        args.password = getpass("Password: ")

    domain = args.domain
    if domain is not None:
        domain = JID(domain)

    if args.encrypted:
        print(
            'You are using the --encrypt flag. '
            'Be aware that the transport being used is NOT end-to-end '
            'encrypted. The server will be able to decrypt the file.',
            file=sys.stderr,
        )

    xmpp = HttpUpload(
        jid=args.jid,
        password=args.password,
        recipient=JID(args.recipient),
        filename=Path(args.file),
        domain=domain,
        encrypted=args.encrypted,
    )
    xmpp.register_plugin('xep_0066')
    xmpp.register_plugin('xep_0071')
    xmpp.register_plugin('xep_0128')
    xmpp.register_plugin('xep_0363')
    try:
        xmpp.register_plugin('xep_0454')
    except slixmpp.plugins.base.PluginNotFound:
        log.error(
            'Could not load xep_0454. '
            'Ensure you have \'cryptography\' from extras_require installed.'
        )

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
