
# slixmpp.clientxmpp
# ~~~~~~~~~~~~~~~~~~~~
# This module provides XMPP functionality that
# is specific to external server component connections.
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
import logging
import hashlib

from asyncio import Future
from typing import Optional

from slixmpp import Message, Iq, Presence
from slixmpp.basexmpp import BaseXMPP
from slixmpp.stanza import Handshake
from slixmpp.stanza.error import Error
from slixmpp.xmlstream import XMLStream
from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.stanzabase import register_stanza_plugin

log = logging.getLogger(__name__)


class ComponentXMPP(BaseXMPP):

    """
    Slixmpp's basic XMPP server component.

    Use only for good, not for evil.

    :param jid: The JID of the component.
    :param secret: The secret or password for the component.
    :param host: The server accepting the component.
    :param port: The port used to connect to the server.
    :param plugin_config: A dictionary of plugin configurations.
    :param plugin_whitelist: A list of approved plugins that
                    will be loaded when calling
                    :meth:`~slixmpp.basexmpp.BaseXMPP.register_plugins()`.
    :param use_jc_ns: Indicates if the ``'jabber:client'`` namespace
                      should be used instead of the standard
                      ``'jabber:component:accept'`` namespace.
                      Defaults to ``False``.
    :param fix_error_ns: Fix the namespace of error stanzas.
        If you use ``use_jc_ns`` namespace, you probably want that, but
        it can be a problem if you use both a ClientXMPP and a ComponentXMPP
        in the same interpreter. This is ``False`` by default for backwards
        compatibility.
    """

    def __init__(self, jid, secret,
                 host=None, port=None, plugin_config=None,
                 plugin_whitelist=None, use_jc_ns=False,
                 fix_error_ns=False):

        if not plugin_whitelist:
            plugin_whitelist = []
        if not plugin_config:
            plugin_config = {}

        if use_jc_ns:
            default_ns = 'jabber:client'
        else:
            default_ns = 'jabber:component:accept'
        BaseXMPP.__init__(self, jid, default_ns)
        if fix_error_ns:
            self._fix_error_ns()

        self.enable_starttls = False
        self.enable_plaintext = True
        self.auto_authorize = None
        self.stream_header = '<stream:stream %s %s to="%s">' % (
                'xmlns="jabber:component:accept"',
                'xmlns:stream="%s"' % self.stream_ns,
                jid)
        self.stream_footer = "</stream:stream>"
        self.server_host = host
        self.default_domain = host
        self.server_port = port
        self.secret = secret

        self.plugin_config = plugin_config
        self.plugin_whitelist = plugin_whitelist
        self.is_component = True

        self.sessionstarted = False

        self.register_handler(
                Callback('Handshake',
                         MatchXPath('{jabber:component:accept}handshake'),
                         self._handle_handshake))
        self.add_event_handler('presence_probe',
                               self._handle_probe)

    def _fix_error_ns(self):
        Error.namespace = self.default_ns
        for st in Message, Iq, Presence:
            register_stanza_plugin(st, Error)

    def connect(self, host: Optional[str] = None, port: Optional[int] = None) -> Future:
        """Connect to the server.


        :param host: The name of the desired server for the connection.
                     Defaults to :attr:`server_host`.
        :param port: Port to connect to on the server.
                     Defauts to :attr:`server_port`.
        """
        if host is not None:
            self.server_host = host
        if port is not None:
            self.server_port = port

        self.server_name = self.boundjid.host

        self.init_plugins()

        log.debug("Connecting to %s:%s", self.server_host, self.server_port)
        return XMLStream.connect(self, host=self.server_host, port=self.server_port)

    def incoming_filter(self, xml):
        """
        Pre-process incoming XML stanzas by converting any
        ``'jabber:client'`` namespaced elements to the component's
        default namespace.

        :param xml: The XML stanza to pre-process.
        """
        if xml.tag.startswith('{jabber:client}'):
            xml.tag = xml.tag.replace('jabber:client', self.default_ns)
        return xml

    def start_stream_handler(self, xml):
        """
        Once the streams are established, attempt to handshake
        with the server to be accepted as a component.

        :param xml: The incoming stream's root element.
        """
        BaseXMPP.start_stream_handler(self, xml)

        # Construct a hash of the stream ID and the component secret.
        sid = xml.get('id', '')
        pre_hash = bytes('%s%s' % (sid, self.secret), 'utf-8')

        handshake = Handshake()
        handshake['value'] = hashlib.sha1(pre_hash).hexdigest().lower()

        self.send(handshake)

    def _handle_handshake(self, xml):
        """The handshake has been accepted.

        :param xml: The reply handshake stanza.
        """
        self.session_bind_event.set()
        self.sessionstarted = True
        self.event('session_bind', self.boundjid)
        self.event('session_start')

    def _handle_probe(self, pres):
        self.roster[pres['to']][pres['from']].handle_probe(pres)
