# Slixmpp: The Slick XMPP Library
# This file is part of Slixmpp
# See the file LICENSE for copying permission
import uuid
import logging

from typing import (
    Optional,
    Union,
)

from slixmpp import JID
from slixmpp.stanza import Message, Iq
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0047 import stanza, Open, Close, Data, IBBytestream


log = logging.getLogger(__name__)


class XEP_0047(BasePlugin):
    """
    XEP-0047: In-Band Bytestreams

    Events registered by this plugin:

    - :term:`ibb_stream_start`
    - :term:`ibb_stream_end`
    - :term:`ibb_stream_data`
    - :term:`stream:[stream id]:[peer jid]`

    Plugin Parameters:

    - ``block_size`` (default: ``4096``): default block size to negociate
    - ``max_block_size`` (default: ``8192``): max block size to accept
    - ``auto_accept`` (default: ``False``): if incoming streams should be
        accepted automatically.

    - :term:`authorized (0047 version)`
    - :term:`authorized_sid (0047 version)`
    - :term:`preauthorize_sid (0047 version)`
    - :term:`get_stream`
    - :term:`set_stream`
    - :term:`del_stream`
    """

    name = 'xep_0047'
    description = 'XEP-0047: In-Band Bytestreams'
    dependencies = {'xep_0030'}
    stanza = stanza
    default_config = {
        'block_size': 4096,
        'max_block_size': 8192,
        'auto_accept': False,
    }

    def plugin_init(self):
        self._streams = {}
        self._preauthed_sids = {}

        register_stanza_plugin(Iq, Open)
        register_stanza_plugin(Iq, Close)
        register_stanza_plugin(Iq, Data)
        register_stanza_plugin(Message, Data)

        self.xmpp.register_handler(CoroutineCallback(
            'IBB Open',
            StanzaPath('iq@type=set/ibb_open'),
            self._handle_open_request))

        self.xmpp.register_handler(CoroutineCallback(
            'IBB Close',
            StanzaPath('iq@type=set/ibb_close'),
            self._handle_close))

        self.xmpp.register_handler(CoroutineCallback(
            'IBB Data',
            StanzaPath('iq@type=set/ibb_data'),
            self._handle_data))

        self.xmpp.register_handler(CoroutineCallback(
            'IBB Message Data',
            StanzaPath('message/ibb_data'),
            self._handle_data))

        self.api.register(self._authorized, 'authorized', default=True)
        self.api.register(self._authorized_sid, 'authorized_sid', default=True)
        self.api.register(self._preauthorize_sid, 'preauthorize_sid', default=True)
        self.api.register(self._get_stream, 'get_stream', default=True)
        self.api.register(self._set_stream, 'set_stream', default=True)
        self.api.register(self._del_stream, 'del_stream', default=True)

    def plugin_end(self):
        self.xmpp.remove_handler('IBB Open')
        self.xmpp.remove_handler('IBB Close')
        self.xmpp.remove_handler('IBB Data')
        self.xmpp.remove_handler('IBB Message Data')
        self.xmpp['xep_0030'].del_feature(feature='http://jabber.org/protocol/ibb')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature('http://jabber.org/protocol/ibb')

    def _get_stream(self, jid, sid, peer_jid, data):
        return self._streams.get((jid, sid, peer_jid), None)

    def _set_stream(self, jid, sid, peer_jid, stream):
        self._streams[(jid, sid, peer_jid)] = stream

    def _del_stream(self, jid, sid, peer_jid, data):
        if (jid, sid, peer_jid) in self._streams:
            del self._streams[(jid, sid, peer_jid)]

    async def _accept_stream(self, iq):
        receiver = iq['to']
        sender = iq['from']
        sid = iq['ibb_open']['sid']

        if await self.api['authorized_sid'](receiver, sid, sender, iq):
            return True
        return await self.api['authorized'](receiver, sid, sender, iq)

    def _authorized(self, jid, sid, ifrom, iq):
        if self.auto_accept:
            return True
        return False

    def _authorized_sid(self, jid, sid, ifrom, iq):
        if (jid, sid, ifrom) in self._preauthed_sids:
            del self._preauthed_sids[(jid, sid, ifrom)]
            return True
        return False

    def _preauthorize_sid(self, jid, sid, ifrom, data):
        self._preauthed_sids[(jid, sid, ifrom)] = True

    async def open_stream(self, jid: JID, *, block_size: Optional[int] = None,
                          sid: Optional[str] = None, use_messages: bool = False,
                          ifrom: Optional[JID] = None,
                          **iqkwargs) -> IBBytestream:
        """Open an IBB stream with a peer JID.

        .. versionchanged:: 1.8.0
            This function is now a coroutine and must be awaited.
            All parameters except ``jid`` are keyword-args only.

        :param jid: The remote JID to initiate the stream with.
        :param block_size: The block size to advertise.
        :param sid: The IBB stream id (if not provided, will be auto-generated).
        :param use_messages: If the stream should use message stanzas instead of iqs.
        :returns: The opened byte stream with the remote JID
        :raises .IqError: When the remote entity denied the stream.
        """
        if sid is None:
            sid = str(uuid.uuid4())
        if block_size is None:
            block_size = self.block_size

        iq = self.xmpp.make_iq_set(ito=jid, ifrom=ifrom)
        iq['ibb_open']['block_size'] = block_size
        iq['ibb_open']['sid'] = sid
        iq['ibb_open']['stanza'] = 'message' if use_messages else 'iq'

        stream = IBBytestream(self.xmpp, sid, block_size,
                              iq['from'], iq['to'], use_messages)

        callback = iqkwargs.pop('callback', None)
        result = await iq.send(**iqkwargs)

        log.debug('IBB stream (%s) accepted by %s', stream.sid, result['from'])
        stream.self_jid = result['to']
        stream.peer_jid = result['from']
        stream.stream_started = True
        await self.api['set_stream'](stream.self_jid, stream.sid, stream.peer_jid, stream)
        if callback is not None:
            self.xmpp.add_event_handler('ibb_stream_start', callback, disposable=True)
        self.xmpp.event('ibb_stream_start', stream)
        self.xmpp.event('stream:%s:%s' % (stream.sid, stream.peer_jid), stream)
        return stream

    async def _handle_open_request(self, iq: Iq):
        sid = iq['ibb_open']['sid']
        size = iq['ibb_open']['block_size'] or self.block_size

        log.debug('Received IBB stream request from %s', iq['from'])

        if not sid:
            raise XMPPError(etype='modify', condition='bad-request')

        if not await self._accept_stream(iq):
            raise XMPPError(etype='cancel', condition='not-acceptable')

        if size > self.max_block_size:
            raise XMPPError('resource-constraint')

        stream = IBBytestream(self.xmpp, sid, size,
                              iq['to'], iq['from'])
        stream.stream_started = True
        await self.api['set_stream'](stream.self_jid, stream.sid, stream.peer_jid, stream)
        iq.reply().send()

        self.xmpp.event('ibb_stream_start', stream)
        self.xmpp.event('stream:%s:%s' % (sid, stream.peer_jid), stream)

    async def _handle_data(self, stanza: Union[Iq, Message]):
        sid = stanza['ibb_data']['sid']
        stream = await self.api['get_stream'](stanza['to'], sid, stanza['from'])
        if stream is not None and stanza['from'] == stream.peer_jid:
            stream._recv_data(stanza)
        else:
            raise XMPPError('item-not-found')

    async def _handle_close(self, iq: Iq):
        sid = iq['ibb_close']['sid']
        stream = await self.api['get_stream'](iq['to'], sid, iq['from'])
        if stream is not None and iq['from'] == stream.peer_jid:
            stream._closed(iq)
            await self.api['del_stream'](stream.self_jid, stream.sid, stream.peer_jid)
        else:
            raise XMPPError('item-not-found')
