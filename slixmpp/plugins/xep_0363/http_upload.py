# slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.

import logging
import os.path

from aiohttp import ClientSession
from asyncio import Future
from mimetypes import guess_type
from typing import (
    Optional,
    IO,
)

from pathlib import Path

from slixmpp import JID, __version__
from slixmpp.stanza import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.xep_0363 import stanza, Request, Slot, Put, Get, Header

log = logging.getLogger(__name__)

class FileUploadError(Exception):
    pass

class UploadServiceNotFound(FileUploadError):
    """
    Raised if no upload service can be found.
    """

class FileTooBig(FileUploadError):
    """
    Raised if the file size is above advertised server limits.

    args:

    - size of the file
    - max file size allowed
    """
    def __str__(self):
        return 'File size too large: {} (max: {} bytes)' \
            .format(self.args[0], self.args[1])

class HTTPError(FileUploadError):
    """
    Raised when we receive an HTTP error response during upload.

    args:

    - HTTP Error code
    - Content of the HTTP response
    """
    def __str__(self):
        return 'Could not upload file: %d (%s)' % (self.args[0], self.args[1])

class XEP_0363(BasePlugin):
    """
    XEP-0363: HTTP File Upload
    """

    name = 'xep_0363'
    description = 'XEP-0363: HTTP File Upload'
    dependencies = {'xep_0030', 'xep_0128'}
    stanza = stanza
    default_config = {
        'upload_service': None,
        'max_file_size': float('+inf'),
        'default_content_type': 'application/octet-stream',
    }

    def plugin_init(self):
        register_stanza_plugin(Iq, Request)
        register_stanza_plugin(Iq, Slot)
        register_stanza_plugin(Slot, Put)
        register_stanza_plugin(Slot, Get)
        register_stanza_plugin(Put, Header, iterable=True)

        self.xmpp.register_handler(
                Callback('HTTP Upload Request',
                         StanzaPath('iq@type=get/http_upload_request'),
                         self._handle_request))

    def plugin_end(self):
        self.xmpp.remove_handler('HTTP Upload Request')
        self.xmpp['xep_0030'].del_feature(feature=Request.namespace)

    def session_bind(self, jid):
        self.xmpp.plugin['xep_0030'].add_feature(Request.namespace)

    def _handle_request(self, iq):
        self.xmpp.event('http_upload_request', iq)

    async def find_upload_service(self, domain: Optional[JID] = None, **iqkwargs) -> Optional[Iq]:
        """Find an upload service on a domain (our own by default).

        :param domain: Domain to disco to find a service.
        """
        if domain is None and self.xmpp.is_component:
            domain = self.xmpp.server_host

        results = await self.xmpp['xep_0030'].get_info_from_domain(
            domain=domain, **iqkwargs
        )

        candidates = []
        for info in results:
            if not info['disco_info']:
                continue
            for identity in info['disco_info']['identities']:
                if identity[0] == 'store' and identity[1] == 'file':
                    candidates.append(info)
        for info in candidates:
            for feature in info['disco_info']['features']:
                if feature == Request.namespace:
                    return info

    def request_slot(self, jid: JID, filename: Path, size: int,
                    content_type: Optional[str] = None, *,
                    ifrom: Optional[JID] = None, **iqkwargs) -> Future:
        """Request an HTTP upload slot from a service.

        :param jid: Service to request the slot from.
        :param filename: Name of the file that will be uploaded.
        :param size: size of the file in bytes.
        :param content_type: Type of the file that will be uploaded.
        """
        iq = self.xmpp.make_iq_get(ito=jid, ifrom=ifrom)
        request = iq['http_upload_request']
        request['filename'] = str(filename)
        request['size'] = str(size)
        request['content-type'] = content_type or self.default_content_type
        return iq.send(**iqkwargs)

    async def upload_file(self, filename: Path, size: Optional[int] = None,
                          content_type: Optional[str] = None, *,
                          input_file: Optional[IO[bytes]]=None,
                          domain: Optional[JID] = None,
                          **iqkwargs) -> str:
        '''Helper function which does all of the uploading discovery and
        process.

        :param filename: Path to the file to upload (or only the name if
                         ``input_file`` is provided.
        :param size: size of the file in bytes.
        :param content_type: Type of the file that will be uploaded.
        :param input_file: Binary file stream on the file.
        :param domain: Domain to query to find an HTTP upload service.
        :raises .UploadServiceNotFound: If slixmpp is unable to find an
                                        an available upload service.
        :raises .FileTooBig: If the filesize is above what is accepted by
                             the service.
        :raises .HTTPError: If there is an error in the HTTP operation.
        :returns: The URL of the uploaded file.
        '''
        timeout = iqkwargs.get('timeout', None)
        if self.upload_service is None:
            info_iq = await self.find_upload_service(
                domain=domain, **iqkwargs
            )
            if info_iq is None:
                raise UploadServiceNotFound()
            self.upload_service = info_iq['from']
            for form in info_iq['disco_info'].iterables:
                values = form['values']
                if values['FORM_TYPE'] == ['urn:xmpp:http:upload:0']:
                    try:
                        self.max_file_size = int(values['max-file-size'])
                    except (TypeError, ValueError):
                        log.error('Invalid max size received from HTTP File Upload service')
                        self.max_file_size = float('+inf')
                    break

        if input_file is None:
            input_file = open(filename, 'rb')

        if size is None:
            size = input_file.seek(0, 2)
            input_file.seek(0)

        if size > self.max_file_size:
            raise FileTooBig(size, self.max_file_size)

        if content_type is None:
            content_type = guess_type(filename)[0]
            if content_type is None:
                content_type = self.default_content_type

        basename = os.path.basename(filename)
        slot_iq = await self.request_slot(self.upload_service, basename, size,
                                          content_type, **iqkwargs)
        slot = slot_iq['http_upload_slot']

        headers = {
            'Content-Length': str(size),
            'Content-Type': content_type or self.default_content_type,
            **{header['name']: header['value'] for header in slot['put']['headers']}
        }

        # Do the actual upload here.
        async with ClientSession(headers={'User-Agent': 'slixmpp ' + __version__}) as session:
            response = await session.put(
                    slot['put']['url'],
                    data=input_file,
                    headers=headers,
                    timeout=timeout)
            if response.status >= 400:
                raise HTTPError(response.status, await response.text())
            log.info('Response code: %d (%s)', response.status, await response.text())
            response.close()
            return slot['get']['url']
