# Slixmpp: The Slick XMPP Library
# This file is part of Slixmpp
# See the file LICENSE for copying permission
import asyncio
import socket
import logging

from typing import (
    Optional,
    IO,
    Union,
)

from slixmpp import JID
from slixmpp.stanza import Iq, Message
from slixmpp.exceptions import XMPPError, IqTimeout


log = logging.getLogger(__name__)


class IBBytestream(object):
    """XEP-0047 Stream abstraction. Created by the ibb plugin automatically.

    Provides send methods and triggers :term:`ibb_stream_data` events.
    """

    def __init__(self, xmpp, sid: str, block_size: int, jid: JID, peer: JID,
                 use_messages: bool = False):
        self.xmpp = xmpp
        self.sid = sid
        self.block_size = block_size
        self.use_messages = use_messages

        if jid is None:
            jid = xmpp.boundjid
        self.self_jid = jid
        self.peer_jid = peer

        self.send_seq = -1
        self.recv_seq = -1

        self.stream_started = False
        self.stream_in_closed = False
        self.stream_out_closed = False

        self.recv_queue = asyncio.Queue()

    async def send(self, data: bytes, timeout: Optional[int] = None) -> int:
        """Send a single block of data.

        :param data: Data to send (will be truncated if above block size).
        :returns: Number of bytes sent.
        """
        if not self.stream_started or self.stream_out_closed:
            raise socket.error
        if len(data) > self.block_size:
            data = data[:self.block_size]
        self.send_seq = (self.send_seq + 1) % 65536
        seq = self.send_seq
        if self.use_messages:
            msg = self.xmpp.Message()
            msg['to'] = self.peer_jid
            msg['from'] = self.self_jid
            msg['id'] = self.xmpp.new_id()
            msg['ibb_data']['sid'] = self.sid
            msg['ibb_data']['seq'] = seq
            msg['ibb_data']['data'] = data
            msg.send()
        else:
            iq = self.xmpp.Iq()
            iq['type'] = 'set'
            iq['to'] = self.peer_jid
            iq['from'] = self.self_jid
            iq['ibb_data']['sid'] = self.sid
            iq['ibb_data']['seq'] = seq
            iq['ibb_data']['data'] = data
            await iq.send(timeout=timeout)
        return len(data)

    async def sendall(self, data: bytes, timeout: Optional[int] = None):
        """Send all the contents of ``data`` in chunks.

        :param data: Raw data to send.
        """
        sent_len = 0
        while sent_len < len(data):
            sent_len += await self.send(data[sent_len:sent_len+self.block_size], timeout=timeout)

    async def gather(self, max_data: Optional[int] = None, timeout: int = 3600) -> bytes:
        """Gather all data sent on a stream until it is closed, and return it.

        .. versionadded:: 1.8.0

        :param max_data: Max number of bytes to receive. (received data may be
                         over this limit depending on block_size)
        :param timeout: Timeout after which an error will be raised.
        :raises .IqTimeout: If the timeout is reached.
        :returns: All bytes accumulated in the stream.
        """
        result = b''
        while not self.recv_queue.empty():
            result += self.recv_queue.get_nowait()
            if max_data and len(result) > max_data:
                return result
        if self.stream_in_closed:
            return result

        end_future = asyncio.Future()

        def on_close(stream):
            if stream is self:
                end_future.set_result(True)

        def on_data(stream):
            nonlocal result
            if stream is self:
                result += stream.read()
                if max_data and len(result) > max_data:
                    end_future.set_result(True)

        self.xmpp.add_event_handler('ibb_stream_end', on_close)
        self.xmpp.add_event_handler('ibb_stream_data', on_data)
        try:
            await asyncio.wait_for(end_future, timeout)
        except asyncio.TimeoutError:
            raise IqTimeout(result)
        finally:
            self.xmpp.del_event_handler('ibb_stream_end', on_close)
            self.xmpp.del_event_handler('ibb_stream_data', on_data)
        return result

    async def sendfile(self, file: IO[bytes], timeout: Optional[int] = None):
        """Send the contents of a file over the wire, in chunks.

        :param file: The opened file (or file-like) object, in bytes mode."""
        while True:
            data = file.read(self.block_size)
            if not data:
                break
            await self.send(data, timeout=timeout)

    def _recv_data(self, stanza: Union[Message, Iq]):
        new_seq = stanza['ibb_data']['seq']
        if new_seq != (self.recv_seq + 1) % 65536:
            self.close()
            raise XMPPError('unexpected-request')
        self.recv_seq = new_seq

        data = stanza['ibb_data']['data']
        if len(data) > self.block_size:
            self.close()
            raise XMPPError('not-acceptable')

        self.recv_queue.put_nowait(data)
        self.xmpp.event('ibb_stream_data', self)

        if isinstance(stanza, Iq):
            stanza.reply().send()

    def recv(self, *args, **kwargs):
        return self.read()

    def read(self):
        if not self.stream_started or self.stream_in_closed:
            raise socket.error
        return self.recv_queue.get_nowait()

    def close(self, timeout: Optional[int] = None) -> asyncio.Future:
        """Close the stream."""
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = self.peer_jid
        iq['from'] = self.self_jid
        iq['ibb_close']['sid'] = self.sid
        self.stream_out_closed = True
        def _close_stream(_):
            self.stream_in_closed = True
        future = iq.send(timeout=timeout, callback=_close_stream)
        self.xmpp.event('ibb_stream_end', self)
        return future

    def _closed(self, iq: Iq):
        self.stream_in_closed = True
        self.stream_out_closed = True
        iq.reply().send()
        self.xmpp.event('ibb_stream_end', self)

    def makefile(self, *args, **kwargs):
        return self

    def connect(self, *args, **kwargs):
        return None

    def shutdown(self, *args, **kwargs):
        return None
