# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz,
# Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
import hashlib

from asyncio import Future
from typing import Optional

from slixmpp import JID
from slixmpp.exceptions import XMPPError
from slixmpp.stanza import Iq, Message, Presence
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0231 import BitsOfBinary


log = logging.getLogger(__name__)


class XEP_0231(BasePlugin):

    """
    XEP-0231 Bits of Binary
    """

    name = 'xep_0231'
    description = 'XEP-0231: Bits of Binary'
    dependencies = {'xep_0030'}

    def plugin_init(self):
        self._cids = {}

        register_stanza_plugin(Iq, BitsOfBinary)
        register_stanza_plugin(Message, BitsOfBinary)
        register_stanza_plugin(Presence, BitsOfBinary)

        self.xmpp.register_handler(
            CoroutineCallback('Bits of Binary - Iq',
                StanzaPath('iq/bob'),
                self._handle_bob_iq))

        self.xmpp.register_handler(
            CoroutineCallback('Bits of Binary - Message',
                StanzaPath('message/bob'),
                self._handle_bob))

        self.xmpp.register_handler(
            CoroutineCallback('Bits of Binary - Presence',
                StanzaPath('presence/bob'),
                self._handle_bob))

        self.api.register(self._get_bob, 'get_bob', default=True)
        self.api.register(self._set_bob, 'set_bob', default=True)
        self.api.register(self._del_bob, 'del_bob', default=True)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature='urn:xmpp:bob')
        self.xmpp.remove_handler('Bits of Binary - Iq')
        self.xmpp.remove_handler('Bits of Binary - Message')
        self.xmpp.remove_handler('Bits of Binary - Presence')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature('urn:xmpp:bob')

    async def set_bob(self, data: bytes, mtype: str, cid: Optional[str] = None,
                      max_age: Optional[int] = None) -> str:
        """Register a blob of binary data as a BOB.

        .. versionchanged:: 1.8.0
            If ``max_age`` is specified, the registered data will be destroyed
            after that time.
            This function is now a coroutine.

        :param data: Data to register.
        :param mtype: Mime Type of the data (e.g. ``image/jpeg``).
        :param cid: Content-ID (will be auto-generated if left out).
        :param max_age: Duration of content availability.
        :returns: The cid value.
        """
        if cid is None:
            cid = 'sha1+%s@bob.xmpp.org' % hashlib.sha1(data).hexdigest()

        bob = BitsOfBinary()
        bob['data'] = data
        bob['type'] = mtype
        bob['cid'] = cid
        if max_age is not None:
            bob['max_age'] = max_age

        await self.api['set_bob'](args=bob)
        # Schedule destruction of the data
        if max_age is not None and max_age > 0:
            self.xmpp.loop.call_later(max_age, self.del_bob,  cid)
        return cid

    async def get_bob(self, jid: Optional[JID] = None, cid: Optional[str] = None,
                      cached: bool = True, ifrom: Optional[JID] = None,
                      **iqkwargs) -> Iq:
        """Get a BOB.

        .. versionchanged:: 1.8.0
            Results not in cache do not raise an error when ``cached`` is True.
            This function is now a coroutine.

        :param jid: JID to fetch the BOB from.
        :param cid: Content ID (actually required).
        :param cached: To fetch the BOB from the local cache first (from CID only)
        """
        if cached:
            data = await self.api['get_bob'](None, None, ifrom, args=cid)
            if data is not None:
                if not isinstance(data, Iq):
                    iq = self.xmpp.Iq()
                    iq.append(data)
                    return iq
                return data

        iq = self.xmpp.make_iq_get(ito=jid, ifrom=ifrom)
        iq['bob']['cid'] = cid
        return await iq.send(**iqkwargs)

    def del_bob(self, cid: str) -> Future:
        """Delete a stored BoB.

        .. versionchanged:: 1.8.0
            This function now returns a Future.
        """
        return self.api['del_bob'](args=cid)

    async def _handle_bob_iq(self, iq: Iq):
        cid = iq['bob']['cid']

        if iq['type'] == 'result':
            await self.api['set_bob'](iq['from'], None, iq['to'], args=iq['bob'])
            self.xmpp.event('bob', iq)
        elif iq['type'] == 'get':
            data = await self.api['get_bob'](iq['to'], None, iq['from'], args=cid)

            if data is None:
                raise XMPPError(
                    "item-not-found",
                    f"Bits of binary '{cid}' is not available",
                )

            if isinstance(data, Iq):
                data['id'] = iq['id']
                data.send()
                return

            iq = iq.reply()
            iq.append(data)
            iq.send()

    async def _handle_bob(self, stanza):
        await self.api['set_bob'](
            stanza['from'], None,
            stanza['to'], args=stanza['bob']
        )
        self.xmpp.event('bob', stanza)

    # =================================================================

    def _set_bob(self, jid, node, ifrom, bob):
        self._cids[bob['cid']] = bob

    def _get_bob(self, jid, node, ifrom, cid):
        if cid in self._cids:
            return self._cids[cid]

    def _del_bob(self, jid, node, ifrom, cid):
        if cid in self._cids:
            del self._cids[cid]
