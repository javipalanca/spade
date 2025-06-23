import asyncio
import logging
import socket

from hashlib import sha1
from uuid import uuid4

from slixmpp.stanza import Iq
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.base import BasePlugin

from slixmpp.plugins.xep_0065 import stanza, Socks5, Socks5Protocol


log = logging.getLogger(__name__)


class XEP_0065(BasePlugin):

    name = 'xep_0065'
    description = "XEP-0065: SOCKS5 Bytestreams"
    dependencies = {'xep_0030'}
    default_config = {
        'auto_accept': False
    }

    def plugin_init(self):
        register_stanza_plugin(Iq, Socks5)

        self._proxies = {}
        self._sessions = {}
        self._preauthed_sids = {}

        self.xmpp.register_handler(CoroutineCallback(
            'Socks5 Bytestreams',
             StanzaPath('iq@type=set/socks/streamhost'),
             self._handle_streamhost
        ))

        self.api.register(self._authorized, 'authorized', default=True)
        self.api.register(self._authorized_sid, 'authorized_sid', default=True)
        self.api.register(self._preauthorize_sid, 'preauthorize_sid', default=True)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Socks5.namespace)

    def plugin_end(self):
        self.xmpp.remove_handler('Socks5 Bytestreams')
        self.xmpp.remove_handler('Socks5 Streamhost Used')
        self.xmpp['xep_0030'].del_feature(feature=Socks5.namespace)

    def get_socket(self, sid):
        """Returns the socket associated to the SID."""
        return self._sessions.get(sid, None)

    async def handshake(self, to, ifrom=None, sid=None, timeout=None):
        """ Starts the handshake to establish the socks5 bytestreams
        connection.
        """
        if not self._proxies:
            self._proxies = await self.discover_proxies()

        if sid is None:
            sid = uuid4().hex

        used = await self.request_stream(to, sid=sid, ifrom=ifrom, timeout=timeout)
        proxy = used['socks']['streamhost_used']['jid']

        if proxy not in self._proxies:
            log.warning('Received unknown SOCKS5 proxy: %s', proxy)
            return

        try:
            self._sessions[sid] = (await self._connect_proxy(
                    self._get_dest_sha1(sid, self.xmpp.boundjid, to),
                    self._proxies[proxy][0],
                    self._proxies[proxy][1]))[1]
        except socket.error:
            return None
        addr, port = await self._sessions[sid].connected

        # Request that the proxy activate the session with the target.
        await self.activate(proxy, sid, to, timeout=timeout)
        sock = self.get_socket(sid)
        self.xmpp.event('stream:%s:%s' % (sid, to), sock)
        return sock

    def request_stream(self, to, sid=None, ifrom=None, timeout=None, callback=None):
        if sid is None:
            sid = uuid4().hex

        # Requester initiates S5B negotiation with Target by sending
        # IQ-set that includes the JabberID and network address of
        # StreamHost as well as the StreamID (SID) of the proposed
        # bytestream.
        iq = self.xmpp.Iq()
        iq['to'] = to
        iq['from'] = ifrom
        iq['type'] = 'set'
        iq['socks']['sid'] = sid
        for proxy, (host, port) in self._proxies.items():
            iq['socks'].add_streamhost(proxy, host, port)
        return iq.send(timeout=timeout, callback=callback)

    async def discover_proxies(self, jid=None, ifrom=None, timeout=None):
        """Auto-discover the JIDs of SOCKS5 proxies on an XMPP server."""
        if jid is None:
            if self.xmpp.is_component:
                jid = self.xmpp.server
            else:
                jid = self.xmpp.boundjid.server

        discovered = set()

        disco_items = await self.xmpp['xep_0030'].get_items(jid, timeout=timeout)
        disco_items = {item[0] for item in disco_items['disco_items']['items']}

        disco_info_futures = {}
        for item in disco_items:
            disco_info_futures[item] = self.xmpp['xep_0030'].get_info(item, timeout=timeout)

        for item in disco_items:
            try:
                disco_info = await disco_info_futures[item]
            except XMPPError:
                continue
            else:
                # Verify that the identity is a bytestream proxy.
                identities = disco_info['disco_info']['identities']
                for identity in identities:
                    if identity[0] == 'proxy' and identity[1] == 'bytestreams':
                        discovered.add(disco_info['from'])

        for jid in discovered:
            try:
                addr = await self.get_network_address(jid, ifrom=ifrom, timeout=timeout)
                self._proxies[jid] = (addr['socks']['streamhost']['host'],
                                      addr['socks']['streamhost']['port'])
            except XMPPError:
                continue

        return self._proxies

    def get_network_address(self, proxy, ifrom=None, timeout=None, callback=None):
        """Get the network information of a proxy."""
        iq = self.xmpp.Iq(sto=proxy, stype='get', sfrom=ifrom)
        iq.enable('socks')
        return iq.send(timeout=timeout, callback=callback)

    def _get_dest_sha1(self, sid, requester, target):
        # The hostname MUST be SHA1(SID + Requester JID + Target JID)
        # where the output is hexadecimal-encoded (not binary).
        digest = sha1()
        digest.update(sid.encode('utf8'))
        digest.update(str(requester).encode('utf8'))
        digest.update(str(target).encode('utf8'))
        return digest.hexdigest()

    async def _handle_streamhost(self, iq):
        """Handle incoming SOCKS5 session request."""
        sid = iq['socks']['sid']
        if not sid:
            raise XMPPError(etype='modify', condition='bad-request')

        if not await self._accept_stream(iq):
            raise XMPPError(etype='modify', condition='not-acceptable')

        streamhosts = iq['socks']['streamhosts']
        requester = iq['from']
        target = iq['to']

        dest = self._get_dest_sha1(sid, requester, target)

        proxy_futures = []
        for streamhost in streamhosts:
            proxy_futures.append(self._connect_proxy(
                    dest,
                    streamhost['host'],
                    streamhost['port']))

        proxies = await asyncio.gather(*proxy_futures, return_exceptions=True)
        for streamhost, proxy in zip(streamhosts, proxies):
            if isinstance(proxy, ValueError):
                continue
            elif isinstance(proxy, socket.error):
                log.error('Socket error while connecting to the proxy.')
                continue
            proxy = proxy[1]
            # TODO: what if the future never happens?
            try:
                addr, port = await proxy.connected
            except socket.error:
                log.exception('Socket error while connecting to the proxy.')
                continue
            # TODO: make a better choice than just the first working one.
            used_streamhost = streamhost['jid']
            conn = proxy
            break
        else:
            raise XMPPError(etype='cancel', condition='item-not-found')

        # TODO: close properly the connection to the other proxies.

        iq = iq.reply()
        self._sessions[sid] = conn
        iq['socks']['sid'] = sid
        iq['socks']['streamhost_used']['jid'] = used_streamhost
        iq.send()
        self.xmpp.event('socks5_stream', conn)
        self.xmpp.event('stream:%s:%s' % (sid, requester), conn)


    def activate(self, proxy, sid, target, ifrom=None, timeout=None, callback=None):
        """Activate the socks5 session that has been negotiated."""
        iq = self.xmpp.Iq(sto=proxy, stype='set', sfrom=ifrom)
        iq['socks']['sid'] = sid
        iq['socks']['activate'] = target
        return iq.send(timeout=timeout, callback=callback)

    def deactivate(self, sid):
        """Closes the proxy socket associated with this SID."""
        sock = self._sessions.get(sid)
        if sock:
            try:
                # sock.close() will also delete sid from self._sessions (see _connect_proxy)
                sock.close()
            except socket.error:
                pass
            # Though this should not be necessary remove the closed session anyway
            if sid in self._sessions:
                log.warn(('SOCKS5 session with sid = "%s" was not ' +
                          'removed from _sessions by sock.close()') % sid)
                del self._sessions[sid]

    def close(self):
        """Closes all proxy sockets."""
        for sid, sock in self._sessions.items():
            sock.close()
        self._sessions = {}

    def _connect_proxy(self, dest, proxy, proxy_port):
        """ Returns a future to a connection between the client and the server-side
        Socks5 proxy.

        dest : The SHA-1 of (SID + Requester JID + Target JID), in hex. <str>
        host : The hostname or the IP of the proxy. <str>
        port : The port of the proxy. <str> or <int>
        """
        factory = lambda: Socks5Protocol(dest, 0, self.xmpp.event)
        return self.xmpp.loop.create_connection(factory, proxy, proxy_port)

    async def _accept_stream(self, iq):
        receiver = iq['to']
        sender = iq['from']
        sid = iq['socks']['sid']

        if await self.api['authorized_sid'](receiver, sid, sender, iq):
            return True
        return await self.api['authorized'](receiver, sid, sender, iq)

    def _authorized(self, jid, sid, ifrom, iq):
        return self.auto_accept

    def _authorized_sid(self, jid, sid, ifrom, iq):
        log.debug('>>> authed sids: %s', self._preauthed_sids)
        log.debug('>>> lookup: %s %s %s', jid, sid, ifrom)
        if (jid, sid, ifrom) in self._preauthed_sids:
            del self._preauthed_sids[(jid, sid, ifrom)]
            return True
        return False

    def _preauthorize_sid(self, jid, sid, ifrom, data):
        log.debug('>>>> %s %s %s %s', jid, sid, ifrom, data)
        self._preauthed_sids[(jid, sid, ifrom)] = True
