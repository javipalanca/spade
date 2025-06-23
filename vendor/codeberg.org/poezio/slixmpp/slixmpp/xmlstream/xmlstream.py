
# slixmpp.xmlstream.xmlstream
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This module provides the module for creating and
# interacting with generic XML streams, along with
# the necessary eventing infrastructure.
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from typing import (
    Any,
    Dict,
    Awaitable,
    Generator,
    Coroutine,
    Callable,
    Iterable,
    List,
    Optional,
    Set,
    Union,
    Tuple,
    TypeVar,
    Type,
    cast,
)

import asyncio
import functools
import logging
import socket as Socket
import ssl
import uuid
import warnings
import weakref
import collections

from contextlib import contextmanager
import xml.etree.ElementTree as ET
from asyncio import (
    AbstractEventLoop,
    BaseTransport,
    Future,
    Task,
    TimerHandle,
    Transport,
    iscoroutinefunction,
    wait,
)
from pathlib import Path

from slixmpp.types import FilterString
from slixmpp.xmlstream.tostring import tostring
from slixmpp.xmlstream.stanzabase import StanzaBase, ElementBase
from slixmpp.xmlstream.resolver import resolve, default_resolver
from slixmpp.xmlstream.handler.base import BaseHandler

T = TypeVar('T')

#: The time in seconds to wait before timing out waiting for response stanzas.
RESPONSE_TIMEOUT = 30

log = logging.getLogger(__name__)


class ContinueQueue(Exception):
    """
    Exception raised in the send queue to "continue" from within an inner loop
    """


class NotConnectedError(Exception):
    """
    Raised when we try to send something over the wire but we are not
    connected.
    """


class InvalidCABundle(Exception):
    """
        Exception raised when the CA Bundle file hasn't been found.
    """

    def __init__(self, path: Optional[Union[Path, Iterable[Path]]]):
        self.path = path


_T = TypeVar('_T', str, ElementBase, StanzaBase)


SyncFilter = Callable[[StanzaBase], Optional[StanzaBase]]
AsyncFilter = Callable[[StanzaBase], Awaitable[Optional[StanzaBase]]]


Filter = Union[
    SyncFilter,
    AsyncFilter,
]

_FiltersDict = Dict[str, List[Filter]]

Handler = Callable[[Any], Union[
    Any,
    Coroutine[Any, Any, Any]
]]


class XMLStream(asyncio.BaseProtocol):
    """
    An XML stream connection manager and event dispatcher.

    The XMLStream class abstracts away the issues of establishing a
    connection with a server and sending and receiving XML "stanzas".
    A stanza is a complete XML element that is a direct child of a root
    document element. Two streams are used, one for each communication
    direction, over the same socket. Once the connection is closed, both
    streams should be complete and valid XML documents.

    Three types of events are provided to manage the stream:
        :Stream: Triggered based on received stanzas, similar in concept
                 to events in a SAX XML parser.
        :Custom: Triggered manually.
        :Scheduled: Triggered based on time delays.

    Typically, stanzas are first processed by a stream event handler which
    will then trigger custom events to continue further processing,
    especially since custom event handlers may run in individual threads.

    :param socket: Use an existing socket for the stream. Defaults to
                   ``None`` to generate a new socket.
    :param string host: The name of the target server.
    :param int port: The port to use for the connection. Defaults to 0.
    """

    transport: Optional[Transport]

    # The socket that is used internally by the transport object
    socket: Optional[ssl.SSLSocket]

    # The backoff of the connect routine (increases exponentially
    # after each failure)
    _connect_loop_wait: float

    parser: Optional[ET.XMLPullParser]
    xml_depth: int
    xml_root: Optional[ET.Element]

    waiting_queue: asyncio.Queue

    # A dict of {name: handle}
    scheduled_events: Dict[str, TimerHandle]

    ssl_context: ssl.SSLContext

    # The event to trigger when the create_connection() succeeds. It can
    # be "connected" or "tls_success" depending on the step we are at.
    event_when_connected: str

    #: The list of accepted ciphers, in OpenSSL Format.
    #: It might be useful to override it for improved security
    #: over the python defaults.
    ciphers: Optional[str]

    #: Path to a file containing certificates for verifying the
    #: server SSL certificate. A non-``None`` value will trigger
    #: certificate checking.
    #:
    #: .. note::
    #:
    #:     On Mac OS X, certificates in the system keyring will
    #:     be consulted, even if they are not in the provided file.
    ca_certs: Optional[Union[Path, Iterable[Path]]]

    #: Path to a file containing a client certificate to use for
    #: authenticating via SASL EXTERNAL. If set, there must also
    #: be a corresponding `:attr:keyfile` value.
    certfile: Optional[str]

    #: Path to a file containing the private key for the selected
    #: client certificate to use for authenticating via SASL EXTERNAL.
    keyfile: Optional[str]

    # The asyncio event loop
    _loop: Optional[AbstractEventLoop]

    #: The default port to return when querying DNS records.
    default_port: int

    #: The domain to try when querying DNS records.
    default_domain: str

    #: The expected name of the server, for validation.
    _expected_server_name: str
    _service_name: str

    #: A custom address to connect to that was provided to connect(). When
    #: using DNS lookups, this is not used. Once set, it will be re-used until
    #: connect() is called with no parameters (or both host and port set to
    #: None).
    custom_address: Optional[Tuple[str, int]]

    #: Enable connecting to the server directly over SSL, in
    #: particular when the service provides two ports: one for
    #: non-SSL traffic and another for SSL traffic.
    enable_direct_tls: bool
    #: Enable connecting to the server using STARTTLS (i.e. upgrading a clear
    #: connection once established).
    enable_starttls: bool
    #: Enable connecting to the server using plaintext
    #: strongly not recommended (unless for localhost components)
    enable_plaintext: bool

    #: If set to ``True``, attempt to use IPv6.
    use_ipv6: bool

    #: If set to ``True``, allow using the ``dnspython`` DNS library
    #: if available. If set to ``False``, the builtin DNS resolver
    #: will be used, even if ``dnspython`` is installed.
    use_aiodns: bool

    #: Use CDATA for escaping instead of XML entities. Defaults
    #: to ``False``.
    use_cdata: bool

    #: The default namespace of the stream content, not of the
    #: stream wrapper it
    default_ns: str

    default_lang: Optional[str]
    peer_default_lang: Optional[str]

    #: The namespace of the enveloping stream element.
    stream_ns: str

    #: The default opening tag for the stream element.
    stream_header: str

    #: The default closing tag for the stream element.
    stream_footer: str

    #: If ``True``, periodically send a whitespace character over the
    #: wire to keep the connection alive. Mainly useful for connections
    #: traversing NAT.
    whitespace_keepalive: bool

    #: The default interval between keepalive signals when
    #: :attr:`whitespace_keepalive` is enabled.
    whitespace_keepalive_interval: int

    #: Flag for controlling if the session can be considered ended
    #: if the connection is terminated.
    end_session_on_disconnect: bool

    #: A mapping of XML namespaces to well-known prefixes.
    namespace_map: dict

    __root_stanza: List[Type[StanzaBase]]
    __handlers: List[BaseHandler]
    __event_handlers: Dict[str, List[Tuple[Handler, bool]]]
    __filters: _FiltersDict

    # Current connection attempt (Future)
    _current_connection_attempt: Optional[Future]

    #: The reason why we are disconnecting from the server
    disconnect_reason: Optional[str]

    #: An asyncio Future being done when the stream is disconnected.
    disconnected: Future

    # If the session has been started or not
    _session_started: bool
    # If we want to bypass the send() check (e.g. unit tests)
    _always_send_everything: bool

    _run_out_filters: Optional[Future]
    __slow_tasks: List[Task]
    __queued_stanzas: List[Tuple[Union[StanzaBase, str], bool]]

    #: List of DNS SRV services records which map to TLS services
    tls_services: Set[str]
    #: List of DNS SRV services records which map to STARTTLS services
    starttls_services: Set[str]


    def __init__(self, host: str = '', port: int = 0,
                 ssl_context: Optional[ssl.SSLContext] = None):
        self.transport = None
        self.socket = None
        self._connect_loop_wait = 0

        self.parser = None
        self.xml_depth = 0
        self.xml_root = None

        self.waiting_queue = asyncio.Queue()

        # A dict of {name: handle}
        self.scheduled_events = {}

        if ssl_context is None:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = True
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context = ssl_context

        self.event_when_connected = "connected"

        self.ciphers = None

        self.ca_certs = None

        self.keyfile = None

        self._loop = None

        self.default_port = int(port)
        self.default_domain = ''

        self._expected_server_name = ''
        self._service_name = ''

        self.custom_address = None

        self.enable_starttls = True
        self.enable_direct_tls = True
        self.enable_plaintext = False

        self.tls_services = set()
        self.starttls_services = set()
        self.use_ipv6 = True

        self.use_aiodns = True
        self.use_cdata = False

        self.default_ns = ''

        self.default_lang = None
        self.peer_default_lang = None

        self.stream_ns = ''
        self.stream_header = "<stream>"
        self.stream_footer = "</stream>"

        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 300

        self.end_session_on_disconnect = True
        self.namespace_map = {StanzaBase.xml_ns: 'xml'}

        self.__root_stanza = []
        self.__handlers = []
        self.__event_handlers = {}
        self.__filters = {
            'in': [], 'out': [], 'out_sync': []
        }

        self._current_connection_attempt = None

        self.disconnect_reason = None
        self.disconnected = Future()
        self._session_started = False
        self._always_send_everything = False

        self.add_event_handler('disconnected', self._remove_schedules)
        self.add_event_handler('disconnected', self._set_disconnected)
        self.add_event_handler('session_start', self._start_keepalive)
        self.add_event_handler('session_start', self._set_session_start)
        self.add_event_handler('session_resumed', self._set_session_start)

        self._run_out_filters = None
        self.__slow_tasks = []
        self.__queued_stanzas = []

    @property
    def loop(self) -> AbstractEventLoop:
        if self._loop is None:
            try:
                # Python < 3.14
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self._loop = asyncio.get_event_loop()
            except RuntimeError:
                try:
                    current = asyncio.get_running_loop()
                except RuntimeError:
                    current = None
                if current is not None:
                    self._loop = current
                else:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self._loop = loop
        return self._loop

    @loop.setter
    def loop(self, value: AbstractEventLoop) -> None:
        self._loop = value

    def new_id(self) -> str:
        """Generate and return a new stream ID in hexadecimal form.

        Many stanzas, handlers, or matchers may require unique
        ID values. Using this method ensures that all new ID values
        are unique in this stream.
        """
        return uuid.uuid4().hex

    def _set_session_start(self, event: Any) -> None:
        """
        On session start, queue all pending stanzas to be sent.
        """
        self._session_started = True
        for stanza in self.__queued_stanzas:
            self.waiting_queue.put_nowait(stanza)
        self.__queued_stanzas = []

    def _set_disconnected(self, event: Any) -> None:
        self._session_started = False

    def _set_disconnected_future(self) -> None:
        """Set the self.disconnected future on disconnect"""
        if not self.disconnected.done():
            self.disconnected.set_result(True)
        self.disconnected = asyncio.Future()

    def connect(self, host: Optional[str] = None, port: Optional[int] = None) -> asyncio.Future:
        """Create a new socket and connect to the server.

        :param host: The name of the desired server for the connection.
        :param port: Port to connect to on the server.
        :returns: A future on the current connection attempt
        """
        if self._run_out_filters is None or self._run_out_filters.done():
            self._run_out_filters = asyncio.ensure_future(
                self.run_filters(),
                loop=self.loop,
            )

        self.disconnect_reason = None
        self.cancel_connection_attempt()
        self._connect_loop_wait = 0
        if host and port:
            self.custom_address = (host, int(port))
        elif (host, port) == (None, None):
            self.custom_address = None

        self.event("connecting")
        self._current_connection_attempt = asyncio.ensure_future(
            self._connect_loop(),
            loop=self.loop,
        )
        return self._current_connection_attempt

    async def _connect_loop(self) -> Optional[asyncio.Future]:
        """
        Loop over the various connection methods. Only wait minimally before
        retries within the same loop. If everything fails, the connection
        is rescheduled for later.
        """
        if self._connect_loop_wait > 0:
            self.event('reconnect_delay', self._connect_loop_wait)
            await asyncio.sleep(self._connect_loop_wait)
        if self.custom_address:
            host, port = self.custom_address
            records = [('', self.default_domain, host, port)]
        else:
            records = await self.get_dns_records(self.default_domain)
        if not records: # No DNS records
            records = [
                ('', self.default_domain, self.default_domain, self.default_port),
            ]
        success = False
        for record in records:
            if success:
                break
            service, host, address, dns_port = record
            tls = service in self.tls_services
            server_hostname = None
            if tls:
                server_hostname = self.default_domain
            try:
                if not service:
                    fake_services = []
                    if self.enable_direct_tls:
                        fake_services.extend(list(self.tls_services))
                    if self.enable_starttls:
                        fake_services.extend(list(self.starttls_services))
                    if self.enable_plaintext:
                        fake_services.extend([''])
                    for service in fake_services:
                        tls, server_hostname = (False, None)
                        if service in self.tls_services:
                            tls, server_hostname = True, self.default_domain
                        success = await self._attempt_connection(
                            address, dns_port, tls, server_hostname,
                        )
                        if success:
                            break
                else:
                    success = await self._attempt_connection(
                        address, dns_port, tls, server_hostname,
                    )
            except Exception as exc:
                log.error('Unhandled exception during connect(): %s',
                          exc, exc_info=True)
        if success:
            return None
        if self._current_connection_attempt is not None:
            return self.reschedule_connection_attempt()
        return None

    async def _attempt_connection(self, host: str, port: int, tls: bool,
                                  server_hostname: Optional[str]) -> bool:
        """Try to connect to a remote server."""
        self.event_when_connected = "connected"
        self._connect_loop_wait += 1
        ssl_context: Optional[ssl.SSLContext] = None
        if tls:
            ssl_context = self.get_ssl_context()

        if self._current_connection_attempt is None:
            return False
        try:
            await self.loop.create_connection(lambda: self,
                                              host, port,
                                              ssl=ssl_context,
                                              server_hostname=server_hostname)
            self._connect_loop_wait = 0
            return True
        except Socket.gaierror:
            self.event('connection_failed',
                       'No DNS record available for %s' % self.default_domain)
            return False
        except OSError as e:
            log.debug('Connection failed: %s', e)
            self.event("connection_failed", e)
            return False

    def init_parser(self) -> None:
        """init the XML parser. The parser must always be reset for each new
        connexion
        """
        self.xml_depth = 0
        self.xml_root = None
        self.parser = ET.XMLPullParser(("start", "end"))

    def connection_made(self, transport: BaseTransport, send_event: bool = True) -> None:
        """Called when the TCP connection has been established with the server
        """
        if send_event:
            self.event(self.event_when_connected)
        self.transport = cast(Transport, transport)
        if self.transport is None:
            raise ValueError("Transport cannot be none")
        self.socket = self.transport.get_extra_info(
            "ssl_object",
            default=self.transport.get_extra_info("socket")
        )
        ssl_object = transport.get_extra_info(
            "ssl_object",
            default=None,
        )
        if ssl_object is not None:
            der_cert = ssl_object.getpeercert(True)
            pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
            self.event('ssl_cert', pem_cert)
            if self._current_connection_attempt is None:
                # Connection attempt aborted
                return
            self.event('tls_success')
        self._current_connection_attempt = None
        self.init_parser()
        self.send_raw(self.stream_header)

    def data_received(self, data: bytes) -> None:
        """Called when incoming data is received on the socket.

        We feed that data to the parser and the see if this produced any XML
        event.  This could trigger one or more event (a stanza is received,
        the stream is opened, etc).
        """
        if self.parser is None:
            log.warning('Received data before the connection is established: %r',
                        data)
            return
        self.parser.feed(data)
        try:
            for event, xml in self.parser.read_events():
                if event == 'start':
                    if self.xml_depth == 0:
                        # We have received the start of the root element.
                        self.xml_root = xml
                        log.debug('RECV: %s', tostring(self.xml_root,
                                                       xmlns=self.default_ns,
                                                       stream=self,
                                                       top_level=True,
                                                       open_only=True))
                        self.start_stream_handler(self.xml_root)  # type:ignore
                    self.xml_depth += 1
                if event == 'end':
                    self.xml_depth -= 1
                    if self.xml_depth == 0:
                        # The stream's root element has closed,
                        # terminating the stream.
                        log.debug("End of stream received")
                        self.disconnect_reason = "End of stream"
                        self.abort()
                        return
                    elif self.xml_depth == 1:
                        # A stanza is an XML element that is a direct child of
                        # the root element, hence the check of depth == 1
                        self._spawn_event(xml)
                        if self.xml_root is not None:
                            # Keep the root element empty of children to
                            # save on memory use.
                            self.xml_root.clear()
        except ET.ParseError:
            log.error('Parse error: %r', data)

            # Due to cyclic dependencies, this can’t be imported at the module
            # level.
            from slixmpp.stanza.stream_error import StreamError
            error = StreamError()
            error['condition'] = 'not-well-formed'
            error['text'] = 'Server sent: %r' % data
            self.send(error)
            self.disconnect()

    def is_connecting(self) -> bool:
        return self._current_connection_attempt is not None

    def is_connected(self) -> bool:
        return self.transport is not None

    def eof_received(self) -> None:
        """When the TCP connection is properly closed by the remote end
        """
        self.event("eof_received")

    def connection_lost(self, exception: Optional[BaseException]) -> None:
        """On any kind of disconnection, initiated by us or not.  This signals the
        closure of the TCP connection
        """
        log.info("connection_lost: %s", (exception,))
        # All these objects are associated with one TCP connection.  Since
        # we are not connected anymore, destroy them
        self.parser = None
        self.transport = None
        self.socket = None
        # Fire the events after cleanup
        if self.end_session_on_disconnect:
            self._reset_sendq()
            self.event('session_end')
        self._set_disconnected_future()
        self.event("disconnected", self.disconnect_reason or exception)

    def reschedule_connection_attempt(self) -> Optional[asyncio.Future]:
        """
        Increase the exponential back-off and initate another background
        _connect_loop call to connect to the server.

        :returns: A future on the next scheduled connection attempt.
        """
        # abort if there is no ongoing connection attempt
        if self._current_connection_attempt is None:
            return None
        self._connect_loop_wait = min(300, self._connect_loop_wait * 2 + 1)
        self._current_connection_attempt = asyncio.ensure_future(
            self._connect_loop(),
            loop=self.loop,
        )
        return self._current_connection_attempt

    def cancel_connection_attempt(self) -> None:
        """
        Immediately cancel the current create_connection() Future.
        This is useful when a client using slixmpp tries to connect
        on flaky networks, where sometimes a connection just gets lost
        and it needs to reconnect while the attempt is still ongoing.
        """
        if self._current_connection_attempt:
            self._current_connection_attempt.cancel()
            self._current_connection_attempt = None

    def disconnect(self, wait: Union[float, int] = 2.0, reason: Optional[str] = None, ignore_send_queue: bool = False) -> Future:
        """Close the XML stream and wait for an acknowldgement from the server for
        at most `wait` seconds.  After the given number of seconds has
        passed without a response from the server, or when the server
        successfully responds with a closure of its own stream, abort() is
        called. If wait is 0.0, this will call abort() directly without closing
        the stream.

        Does nothing but trigger the disconnected event if we are not connected.

        :param wait: Time to wait for a response from the server.
        :param reason: An optional reason for the disconnect.
        :param ignore_send_queue: Boolean to toggle if we want to ignore
                                  the in-flight stanzas and disconnect immediately.
        :return: A future that ends when all code involved in the disconnect has ended
        """
        # Compat: docs/getting_started/sendlogout.rst has been promoting
        # `disconnect(wait=True)` for ages. This doesn't mean anything to the
        # schedule call below. It would fortunately be converted to `1` later
        # down the call chain. Praise the implicit casts lord.
        if wait is True:
            wait = 2.0

        if self.transport:
            self.disconnect_reason = reason
            if self.waiting_queue.empty() or ignore_send_queue:
                self.cancel_connection_attempt()
                return asyncio.ensure_future(
                    self._end_stream_wait(wait, reason=reason),
                    loop=self.loop,
                )
            else:
                return asyncio.ensure_future(
                    self._consume_send_queue_before_disconnecting(reason, wait),
                    loop=self.loop,
                )
        else:
            self._set_disconnected_future()
            self.event("disconnected", reason)
            future: Future = Future()
            future.set_result(None)
            return future

    async def _consume_send_queue_before_disconnecting(self, reason: Optional[str], wait: float) -> None:
        """Wait until the send queue is empty before disconnecting"""
        try:
            await asyncio.wait_for(
                self.waiting_queue.join(),
                wait,
            )
        except asyncio.TimeoutError:
            wait = 0 # we already consumed the timeout
        self.disconnect_reason = reason
        await self._end_stream_wait(wait)

    async def _end_stream_wait(self, wait: Union[int, float] = 2, reason: Optional[str] = None) -> None:
        """
        Run abort() if we do not received the disconnected event
        after a waiting time.

        :param wait: The waiting time (defaults to 2)
        """
        try:
            self.send_raw(self.stream_footer)
            await self.wait_until('disconnected', wait)
        except asyncio.TimeoutError:
            self.abort()
        except NotConnectedError:
            # We are not connected when sending the end of stream
            # that means the disconnect has already been handled
            pass

    def abort(self) -> None:
        """
        Forcibly close the connection
        """
        if self.transport:
            self.cancel_connection_attempt()
            self.transport.close()
            self.transport.abort()
            self.event("killed")

    def reconnect(self, wait: Union[int, float] = 2.0, reason: str = "Reconnecting") -> None:
        """Calls disconnect(), and once we are disconnected (after the timeout, or
        when the server acknowledgement is received), call connect()
        """
        log.debug("reconnecting...")
        async def handler(event: Any) -> None:
            # We yield here to allow synchronous handlers to work first
            await asyncio.sleep(0)
            host, port = None, None
            if self.custom_address:
                host, port = self.custom_address
            self.connect(host=host, port=port)
        self.add_event_handler('disconnected', handler, disposable=True)
        self.disconnect(wait, reason)

    def configure_socket(self) -> None:
        """Set timeout and other options for self.socket.

        Meant to be overridden.
        """
        pass

    def configure_dns(self, resolver: Any, domain: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Configure and set options for a :class:`~dns.resolver.Resolver`
        instance, and other DNS related tasks. For example, you
        can also check :meth:`~socket.socket.getaddrinfo` to see
        if you need to call out to ``libresolv.so.2`` to
        run ``res_init()``.

        Meant to be overridden.

        :param resolver: A :class:`~dns.resolver.Resolver` instance
                         or ``None`` if ``dnspython`` is not installed.
        :param domain: The initial domain under consideration.
        :param port: The initial port under consideration.
        """
        pass

    def get_ssl_context(self) -> ssl.SSLContext:
        """
        Get SSL context.
        """
        if self.ciphers is not None:
            self.ssl_context.set_ciphers(self.ciphers)
        if self.keyfile and self.certfile:
            try:
                self.ssl_context.load_cert_chain(self.certfile, self.keyfile)
            except (ssl.SSLError, OSError):
                log.debug('Error loading the cert chain:', exc_info=True)
            else:
                log.debug('Loaded cert file %s and key file %s',
                          self.certfile, self.keyfile)
        if self.ca_certs is not None:
            ca_cert: Optional[Path] = None
            # XXX: Compat before d733c54518.
            if isinstance(self.ca_certs, str):
                self.ca_certs = Path(self.ca_certs)
            if isinstance(self.ca_certs, Path):
                if self.ca_certs.is_file():
                    ca_cert = self.ca_certs
            else:
                for bundle in self.ca_certs:
                    if bundle.is_file():
                        ca_cert = bundle
                        break
            if ca_cert is None and \
               isinstance(self.ca_certs, (Path, collections.abc.Iterable)):
                raise InvalidCABundle(self.ca_certs)

            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.load_verify_locations(cafile=ca_cert)
        else:
            self.ssl_context.set_default_verify_paths()

        return self.ssl_context

    async def start_tls(self) -> bool:
        """Perform handshakes for TLS.

        If the handshake is successful, the XML stream will need
        to be restarted.
        """
        if self.transport is None:
            raise ValueError("Transport should not be None")
        ssl_context = self.get_ssl_context()
        try:
            self._current_connection_attempt = asyncio.ensure_future(
                self.loop.start_tls(self.transport,
                                    self, ssl_context,
                                    server_hostname=self.default_domain),
                loop=self.loop,
            )
            transp = await self._current_connection_attempt
        except ssl.SSLError as e:
            log.debug('SSL: Unable to connect', exc_info=True)
            log.error('CERT: Invalid certificate trust chain.')
            if not self.event_handled('ssl_invalid_chain'):
                self.disconnect()
            else:
                self.event('ssl_invalid_chain', e)
            return False
        except OSError:
            log.debug("Connection error:", exc_info=True)
            self.disconnect()
            return False
        if transp is None:
            raise Exception("Transport should not be none")
        # If we use the builtin start_tls, the connection_made() protocol
        # method is not called automatically
        if hasattr(self.loop, 'start_tls'):
            self.connection_made(transp, send_event=False)
        return True

    def _start_keepalive(self, event: Any) -> None:
        """Begin sending whitespace periodically to keep the connection alive.

        May be disabled by setting::

            self.whitespace_keepalive = False

        The keepalive interval can be set using::

            self.whitespace_keepalive_interval = 300
        """
        self.schedule('Whitespace Keepalive',
                      self.whitespace_keepalive_interval,
                      self.send_raw,
                      args=(' ',),
                      repeat=True)

    def _remove_schedules(self, event: Any) -> None:
        """Remove some schedules that become pointless when disconnected"""
        self.cancel_schedule('Whitespace Keepalive')

    def start_stream_handler(self, xml: ET.Element) -> None:
        """Perform any initialization actions, such as handshakes,
        once the stream header has been sent.

        Meant to be overridden.
        """
        pass

    def register_stanza(self, stanza_class: Type[StanzaBase]) -> None:
        """Add a stanza object class as a known root stanza.

        A root stanza is one that appears as a direct child of the stream's
        root element.

        Stanzas that appear as substanzas of a root stanza do not need to
        be registered here. That is done using register_stanza_plugin() from
        slixmpp.xmlstream.stanzabase.

        Stanzas that are not registered will not be converted into
        stanza objects, but may still be processed using handlers and
        matchers.

        :param stanza_class: The top-level stanza object's class.
        """
        self.__root_stanza.append(stanza_class)

    def remove_stanza(self, stanza_class: Type[StanzaBase]) -> None:
        """Remove a stanza from being a known root stanza.

        A root stanza is one that appears as a direct child of the stream's
        root element.

        Stanzas that are not registered will not be converted into
        stanza objects, but may still be processed using handlers and
        matchers.
        """
        self.__root_stanza.remove(stanza_class)

    def add_filter(self, mode: FilterString, handler: Callable[[StanzaBase], Optional[StanzaBase]], order: Optional[int] = None) -> None:
        """Add a filter for incoming or outgoing stanzas.

        These filters are applied before incoming stanzas are
        passed to any handlers, and before outgoing stanzas
        are put in the send queue.

        Each filter must accept a single stanza, and return
        either a stanza or ``None``. If the filter returns
        ``None``, then the stanza will be dropped from being
        processed for events or from being sent.

        :param mode: One of ``'in'`` or ``'out'``.
        :param handler: The filter function.
        :param int order: The position to insert the filter in
                          the list of active filters.
        """
        if order:
            self.__filters[mode].insert(order, handler)
        else:
            self.__filters[mode].append(handler)

    def del_filter(self, mode: str, handler: Callable[[StanzaBase], Optional[StanzaBase]]) -> None:
        """Remove an incoming or outgoing filter."""
        self.__filters[mode].remove(handler)

    def register_handler(self, handler: BaseHandler, before: Optional[BaseHandler] = None, after: Optional[BaseHandler] = None) -> None:
        """Add a stream event handler that will be executed when a matching
        stanza is received.

        :param handler:
                The :class:`~slixmpp.xmlstream.handler.base.BaseHandler`
                derived object to execute.
        """
        if handler.stream is None:
            self.__handlers.append(handler)
            handler.stream = weakref.ref(self)

    def remove_handler(self, name: str) -> bool:
        """Remove any stream event handlers with the given name.

        :param name: The name of the handler.
        """
        idx = 0
        for handler in self.__handlers:
            if handler.name == name:
                self.__handlers.pop(idx)
                return True
            idx += 1
        return False

    async def get_dns_records(self, domain: str, port: Optional[int] = None) -> List[Tuple[str, str, str, int]]:
        """Get the DNS records for a domain.

        :param domain: The domain in question.
        :param port: If the results don't include a port, use this one.
        """
        if port is None:
            port = self.default_port

        resolver = default_resolver(loop=self.loop)
        self.configure_dns(resolver, domain=domain, port=port)

        services = []
        if self.enable_direct_tls:
            services.extend(list(self.tls_services))
        if self.enable_starttls:
            services.extend(list(self.starttls_services))
        result = await resolve(domain, port,
                               services=services,
                               resolver=resolver,
                               use_ipv6=self.use_ipv6,
                               use_aiodns=self.use_aiodns,
                               loop=self.loop)
        return result

    def add_event_handler(self, name: str, pointer: Callable[..., Any], disposable: bool = False) -> None:
        """Add a custom event handler that will be executed whenever
        its event is manually triggered.

        :param name: The name of the event that will trigger
                     this handler.
        :param pointer: The function to execute.
        :param disposable: If set to ``True``, the handler will be
                           discarded after one use. Defaults to ``False``.
        """
        if not name in self.__event_handlers:
            self.__event_handlers[name] = []
        self.__event_handlers[name].append((pointer, disposable))

    def del_event_handler(self, name: str, pointer: Callable[..., Any]) -> None:
        """Remove a function as a handler for an event.

        :param name: The name of the event.
        :param pointer: The function to remove as a handler.
        """
        if not name in self.__event_handlers:
            return

        # Need to keep handlers that do not use
        # the given function pointer
        def filter_pointers(handler: Tuple[Callable[..., Any], bool]) -> bool:
            return handler[0] != pointer

        self.__event_handlers[name] = list(filter(
            filter_pointers,
            self.__event_handlers[name]))

    def event_handled(self, name: str) -> int:
        """Returns the number of registered handlers for an event.

        :param name: The name of the event to check.
        """
        return len(self.__event_handlers.get(name, []))

    async def event_async(self, name: str, data: Any = {}) -> None:
        """Manually trigger a custom event, but await coroutines immediately.

        This event generator should only be called in situations when
        in-order processing of events is important, such as features
        handling.

        :param name: The name of the event to trigger.
        :param data: Data that will be passed to each event handler.
                     Defaults to an empty dictionary, but is usually
                     a stanza object.
        """
        handlers = self.__event_handlers.get(name, [])[:]
        for handler in handlers:
            handler_callback, disposable = handler
            if disposable:
                # If the handler is disposable, we will go ahead and
                # remove it now instead of waiting for it to be
                # processed in the queue.
                try:
                    self.__event_handlers[name].remove(handler)
                except ValueError:
                    pass
            # If the callback is a coroutine, schedule it instead of
            # running it directly
            if iscoroutinefunction(handler_callback):
                try:
                    await handler_callback(data)
                except Exception as exc:
                    self.exception(exc)
            else:
                try:
                    handler_callback(data)
                except Exception as e:
                    self.exception(e)

    def event(self, name: str, data: Any = {}) -> None:
        """Manually trigger a custom event.
        Coroutine handlers are wrapped into a future and sent into the
        event loop for their execution, and not awaited.

        :param name: The name of the event to trigger.
        :param data: Data that will be passed to each event handler.
                     Defaults to an empty dictionary, but is usually
                     a stanza object.
        """
        log.debug("Event triggered: %s", name)

        handlers = self.__event_handlers.get(name, [])[:]
        for handler in handlers:
            handler_callback, disposable = handler
            old_exception = getattr(data, 'exception', None)

            # If the callback is a coroutine, schedule it instead of
            # running it directly
            if iscoroutinefunction(handler_callback):
                async def handler_callback_routine(cb: Callable[[ElementBase], Any]) -> None:
                    try:
                        await cb(data)
                    except Exception as e:
                        if old_exception:
                            old_exception(e)
                        else:
                            self.exception(e)
                asyncio.ensure_future(
                    handler_callback_routine(handler_callback),
                    loop=self.loop,
                )
            else:
                try:
                    handler_callback(data)
                except Exception as e:
                    if old_exception:
                        old_exception(e)
                    else:
                        self.exception(e)
            if disposable:
                # If the handler is disposable, we will go ahead and
                # remove it now instead of waiting for it to be
                # processed in the queue.
                try:
                    self.__event_handlers[name].remove(handler)
                except ValueError:
                    pass

    def schedule(self, name: str, seconds: int, callback: Callable[..., None],
            args: Tuple[Any, ...] = tuple(),
            kwargs: Dict[Any, Any] = {}, repeat: bool = False) -> None:
        """Schedule a callback function to execute after a given delay.

        :param name: A unique name for the scheduled callback.
        :param seconds: The time in seconds to wait before executing.
        :param callback: A pointer to the function to execute.
        :param args: A tuple of arguments to pass to the function.
        :param kwargs: A dictionary of keyword arguments to pass to
                       the function.
        :param repeat: Flag indicating if the scheduled event should
                       be reset and repeat after executing.
        """
        if name in self.scheduled_events:
            raise ValueError(
                "There is already a scheduled event of name: %s" % name)
        if seconds is None:
            seconds = RESPONSE_TIMEOUT
        cb = functools.partial(callback, *args, **kwargs)
        if repeat:
            handle = self.loop.call_later(seconds, self._execute_and_reschedule,
                                          name, cb, seconds)
        else:
            handle = self.loop.call_later(seconds, self._execute_and_unschedule,
                                          name, cb)
        # Save that handle, so we can just cancel this scheduled event by
        # canceling scheduled_events[name]
        self.scheduled_events[name] = handle

    def cancel_schedule(self, name: str) -> None:
        try:
            handle = self.scheduled_events.pop(name)
            handle.cancel()
        except KeyError:
            log.debug("Tried to cancel unscheduled event: %s" % (name,))

    def _safe_cb_run(self, name: str, cb: Callable[[], None]) -> None:
        log.debug('Scheduled event: %s', name)
        try:
            cb()
        except Exception as e:
            self.exception(e)

    def _execute_and_reschedule(self, name: str, cb: Callable[[], None], seconds: int) -> None:
        """Simple method that calls the given callback, and then schedule itself to
        be called after the given number of seconds.
        """
        self._safe_cb_run(name, cb)
        handle = self.loop.call_later(seconds, self._execute_and_reschedule,
                                      name, cb, seconds)
        self.scheduled_events[name] = handle

    def _execute_and_unschedule(self, name: str, cb: Callable[[], None]) -> None:
        """
        Execute the callback and remove the handler for it.
        """
        self._safe_cb_run(name, cb)
        # workaround for specific events which unschedule themselves
        if name in self.scheduled_events:
            del self.scheduled_events[name]

    def incoming_filter(self, xml: ET.Element) -> ET.Element:
        """Filter incoming XML objects before they are processed.

        Possible uses include remapping namespaces, or correcting elements
        from sources with incorrect behavior.

        Meant to be overridden.
        """
        return xml

    def _reset_sendq(self) -> None:
        """Clear sending tasks on session end"""
        # Cancel all pending slow send tasks
        log.debug('Cancelling %d slow send tasks', len(self.__slow_tasks))
        for slow_task in self.__slow_tasks:
            slow_task.cancel()
        self.__slow_tasks.clear()
        # Purge pending stanzas
        while not self.waiting_queue.empty():
            discarded = self.waiting_queue.get_nowait()
            log.debug('Discarded stanza: %s', discarded)

    async def _continue_slow_send(
            self,
            task: asyncio.Task,
            already_used: Set[Filter]
    ) -> None:
        """
        Used when an item in the send queue has taken too long to process.

        This is away from the send queue and can take as much time as needed.
        :param asyncio.Task task: the Task wrapping the coroutine
        :param set already_used: Filters already used on this outgoing stanza
        """
        data = await task
        self.__slow_tasks.remove(task)
        if data is None:
            return
        for filter in self.__filters['out'][:]:
            if filter in already_used:
                continue
            if iscoroutinefunction(filter):
                data = await filter(data)  # type: ignore
            else:
                filter = cast(SyncFilter, filter)
                data = filter(data)
            if data is None:
                return

        if isinstance(data, StanzaBase):
            for filter in self.__filters['out_sync']:
                filter = cast(SyncFilter, filter)
                data = filter(data)
                if data is None:
                    return
            str_data = tostring(data.xml, xmlns=self.default_ns,
                                stream=self, top_level=True)
            self.send_raw(str_data)
        else:
            self.send_raw(data)

    async def run_filters(self) -> None:
        """
        Background loop that processes stanzas to send.
        """
        while True:
            data: Optional[Union[StanzaBase, str]]
            (data, use_filters) = await self.waiting_queue.get()
            try:
                if isinstance(data, StanzaBase):
                    if use_filters:
                        already_run_filters = set()
                        for filter in self.__filters['out']:
                            already_run_filters.add(filter)
                            if iscoroutinefunction(filter):
                                filter = cast(AsyncFilter, filter)
                                task = asyncio.create_task(filter(data))  # type:ignore
                                completed, pending = await wait(
                                    {task},
                                    timeout=1,
                                )
                                if pending:
                                    self.__slow_tasks.append(task)
                                    asyncio.ensure_future(
                                        self._continue_slow_send(
                                            task,
                                            already_run_filters
                                        ),
                                        loop=self.loop,
                                    )
                                    raise ContinueQueue(
                                        "Slow coroutine, rescheduling filters"
                                    )
                                data = task.result()
                            elif isinstance(data, StanzaBase):
                                filter = cast(SyncFilter, filter)
                                data = filter(data)
                            if data is None:
                                raise ContinueQueue('Empty stanza')

                if isinstance(data, StanzaBase):
                    if use_filters:
                        for filter in self.__filters['out_sync']:
                            filter = cast(SyncFilter, filter)
                            data = filter(data)
                            if data is None:
                                raise ContinueQueue('Empty stanza')
                    if isinstance(data, StanzaBase):
                        str_data = tostring(data.xml, xmlns=self.default_ns,
                                            stream=self, top_level=True)
                    else:
                        str_data = data
                    self.send_raw(str_data)
                elif isinstance(data, (str, bytes)):
                    self.send_raw(data)
            except ContinueQueue as exc:
                log.debug('Stanza in send queue not sent: %s', exc)
            except asyncio.CancelledError:
                log.debug('Send coroutine received cancel(), stopping')
                return
            except Exception:
                log.error('Exception raised in send queue:', exc_info=True)
            self.waiting_queue.task_done()

    def send(self, data: Union[StanzaBase, str], use_filters: bool = True) -> None:
        """A wrapper for :meth:`send_raw()` for sending stanza objects.

        :param data: The :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
                     stanza to send on the stream.
        :param bool use_filters: Indicates if outgoing filters should be
                                 applied to the given stanza data. Disabling
                                 filters is useful when resending stanzas.
                                 Defaults to ``True``.
        """
        # When not connected, allow features/starttls/etc to go through
        # but not stanzas or arbitrary payloads.
        if not self._always_send_everything and not self._session_started:
            # Avoid circular imports
            from slixmpp.stanza.rootstanza import RootStanza
            from slixmpp.stanza import Iq, Handshake

            passthrough = False
            if isinstance(data, Iq):
                if data.get_plugin('bind', check=True):
                    passthrough = True
                elif data.get_plugin('session', check=True):
                    passthrough = True
                elif data.get_plugin('register', check=True):
                    passthrough = True
            elif isinstance(data, Handshake):
                passthrough = True

            if isinstance(data, (RootStanza, str)) and not passthrough:
                self.__queued_stanzas.append((data, use_filters))
                log.debug('NOT SENT: %s %s', type(data), data)
                self.event('stanza_not_sent', data)
                return
        self.waiting_queue.put_nowait((data, use_filters))

    def send_xml(self, data: ET.Element) -> None:
        """Send an XML object on the stream

        :param data: The :class:`~xml.etree.ElementTree.Element` XML object
                     to send on the stream.
        """
        self.send(tostring(data))

    def send_raw(self, data: Union[str, bytes]) -> None:
        """Send raw data across the stream.

        :param string data: Any bytes or utf-8 string value.
        """
        log.debug("SEND: %s", data)
        if not self.transport:
            raise NotConnectedError()
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.transport.write(data)

    def _build_stanza(self, xml: ET.Element,
                      default_ns: Optional[str] = None) -> StanzaBase:
        """Create a stanza object from a given XML object.

        If a specialized stanza type is not found for the XML, then
        a generic :class:`~slixmpp.xmlstream.stanzabase.StanzaBase`
        stanza will be returned.

        :param xml: The :class:`~xml.etree.ElementTree.Element` XML object
                    to convert into a stanza object.
        :param default_ns: Optional default namespace to use instead of the
                           stream's current default namespace.
        """
        if default_ns is None:
            default_ns = self.default_ns
        stanza_type = StanzaBase
        for stanza_class in self.__root_stanza:
            if xml.tag == "{%s}%s" % (default_ns, stanza_class.name) or \
               xml.tag == stanza_class.tag_name():
                stanza_type = stanza_class
                break
        stanza = stanza_type(self, xml, recv=True)
        if stanza['lang'] is None and self.peer_default_lang:
            stanza['lang'] = self.peer_default_lang
        return stanza

    def _spawn_event(self, xml: ET.Element) -> None:
        """
        Analyze incoming XML stanzas and convert them into stanza
        objects if applicable and queue stream events to be processed
        by matching handlers.

        :param xml: The :class:`~slixmpp.xmlstream.stanzabase.ElementBase`
                    stanza to analyze.
        """
        # Apply any preprocessing filters.
        xml = self.incoming_filter(xml)

        # Convert the raw XML object into a stanza object. If no registered
        # stanza type applies, a generic StanzaBase stanza will be used.
        try:
            stanza: Optional[StanzaBase] = self._build_stanza(xml)
        except Exception as exc:
            log.exception("Unable to parse stanza: %s,\n%s", exc, xml)
            stanza = None
        for filter in self.__filters['in']:
            if stanza is not None:
                filter = cast(SyncFilter, filter)
                stanza = filter(stanza)
        if stanza is None:
            return

        log.debug("RECV: %s", stanza)

        # Match the stanza against registered handlers. Handlers marked
        # to run "in stream" will be executed immediately; the rest will
        # be queued.
        handled = False
        matched_handlers = [h for h in self.__handlers if h.match(stanza)]
        for handler in matched_handlers:
            handler.prerun(stanza)
            try:
                handler.run(stanza)
            except Exception as e:
                stanza.exception(e)
            if handler.check_delete():
                self.__handlers.remove(handler)
            handled = True

        # Some stanzas require responses, such as Iq queries. A default
        # handler will be executed immediately for this case.
        if not handled:
            stanza.unhandled()

    def exception(self, exception: Exception) -> None:
        """Process an unknown exception.

        Meant to be overridden.

        :param exception: An unhandled exception object.
        """
        pass

    async def wait_until(self, event: str, timeout: Union[int, float] = 30) -> Any:
        """Utility method to wake on the next firing of an event.
        (Registers a disposable handler on it)

        :param str event: Event to wait on.
        :param int timeout: Timeout
        :raises: :class:`asyncio.TimeoutError` when the timeout is reached
        """
        fut: Future = asyncio.Future()

        def result_handler(event_data: Any) -> None:
            if not fut.done():
                fut.set_result(event_data)
            else:
                log.debug(
                    "Future registered on event '%s' was alredy done",
                    event
                )

        self.add_event_handler(
            event,
            result_handler,
            disposable=True,
        )
        return await asyncio.wait_for(fut, timeout)

    @contextmanager
    def event_handler(self, event: str, handler: Callable[..., Any]) -> Generator[None, None, None]:
        """
        Context manager that adds then removes an event handler.
        """
        self.add_event_handler(event, handler)
        try:
            yield
        except Exception:
            raise
        finally:
            self.del_event_handler(event, handler)

    def wrap(self, coroutine: Coroutine[None, None, T]) -> Future:
        """Make a Future out of a coroutine with the current loop.

        :param coroutine: The coroutine to wrap.
        """
        return asyncio.ensure_future(
            coroutine,
            loop=self.loop,
        )

    def __del__(self) -> None:
        if self._run_out_filters is not None:
            self._run_out_filters.cancel()
