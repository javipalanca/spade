'''Pure asyncio implementation of RFC 1928 - SOCKS Protocol Version 5.'''

import asyncio
import enum
import logging
import socket
import struct

from slixmpp.stringprep import punycode, StringprepError


log = logging.getLogger(__name__)


class ProtocolMismatch(Exception):
    '''We only implement SOCKS5, no other version or protocol.'''


class ProtocolError(Exception):
    '''Some protocol error.'''


class MethodMismatch(Exception):
    '''The server answered with a method we didn’t ask for.'''


class MethodUnacceptable(Exception):
    '''None of our methods is supported by the server.'''


class AddressTypeUnacceptable(Exception):
    '''The address type (ATYP) field isn’t one of IPv4, IPv6 or domain name.'''


class ReplyError(Exception):
    '''The server answered with an error.'''

    possible_values = (
        "succeeded",
        "general SOCKS server failure",
        "connection not allowed by ruleset",
        "Network unreachable",
        "Host unreachable",
        "Connection refused",
        "TTL expired",
        "Command not supported",
        "Address type not supported",
        "Unknown error")

    def __init__(self, result):
        if result < 9:
            Exception.__init__(self, self.possible_values[result])
        else:
            Exception.__init__(self, self.possible_values[9])


class Method(enum.IntEnum):
    '''Known methods for a SOCKS5 session.'''
    none = 0
    gssapi = 1
    password = 2
    # Methods 3 to 127 are reserved by IANA.
    # Methods 128 to 254 are reserved for private use.
    unacceptable = 255
    not_yet_selected = -1


class Command(enum.IntEnum):
    '''Existing commands for requests.'''
    connect = 1
    bind = 2
    udp_associate = 3


class AddressType(enum.IntEnum):
    '''Existing address types.'''
    ipv4 = 1
    domain = 3
    ipv6 = 4


class Socks5Protocol(asyncio.Protocol):
    '''This implements SOCKS5 as an asyncio protocol.'''

    def __init__(self, dest_addr, dest_port, event):
        self.methods = {Method.none}
        self.selected_method = Method.not_yet_selected
        self.transport = None
        self.dest = (dest_addr, dest_port)
        self.connected = asyncio.Future()
        self.event = event
        self.paused = asyncio.Future()
        self.paused.set_result(None)

    def register_method(self, method):
        '''Register a SOCKS5 method.'''
        self.methods.add(method)

    def unregister_method(self, method):
        '''Unregister a SOCKS5 method.'''
        self.methods.remove(method)

    def connection_made(self, transport):
        '''Called when the connection to the SOCKS5 server is established.'''

        log.debug('SOCKS5 connection established.')

        self.transport = transport
        self._send_methods()

    def data_received(self, data):
        '''Called when we received some data from the SOCKS5 server.'''

        log.debug('SOCKS5 message received.')

        # If we are already connected, this is a data packet.
        if self.connected.done():
            return self.event('socks5_data', data)

        # Every SOCKS5 message starts with the protocol version.
        if data[0] != 5:
            raise ProtocolMismatch()

        # Then select the correct handler for the data we just received.
        if self.selected_method == Method.not_yet_selected:
            self._handle_method(data)
        else:
            self._handle_connect(data)

    def connection_lost(self, exc):
        log.debug('SOCKS5 connection closed.')
        self.event('socks5_closed', exc)

    def pause_writing(self):
        self.paused = asyncio.Future()

    def resume_writing(self):
        self.paused.set_result(None)

    async def write(self, data):
        await self.paused
        self.transport.write(data)

    def _send_methods(self):
        '''Send the methods request, first thing a client should do.'''

        # Create the buffer for our request.
        request = bytearray(len(self.methods) + 2)

        # Protocol version.
        request[0] = 5

        # Number of methods to send.
        request[1] = len(self.methods)

        # List every method we support.
        for i, method in enumerate(self.methods):
            request[i + 2] = method

        # Send the request.
        self.transport.write(request)

    def _send_request(self, command):
        '''Send a request, should be done after having negociated a method.'''

        # Encode the destination address to embed it in our request.
        # We need to do that first because its length is variable.
        address, port = self.dest
        addr = self._encode_addr(address)

        # Create the buffer for our request.
        request = bytearray(5 + len(addr))

        # Protocol version.
        request[0] = 5

        # Specify the command we want to use.
        request[1] = command

        # request[2] is reserved, keeping it at 0.

        # Add our destination address and port.
        request[3:3+len(addr)] = addr
        request[-2:] = struct.pack('>H', port)

        # Send the request.
        log.debug('SOCKS5 message sent.')
        self.transport.write(request)

    def _handle_method(self, data):
        '''Handle a method reply from the server.'''

        if len(data) != 2:
            raise ProtocolError()
        selected_method = data[1]
        if selected_method not in self.methods:
            raise MethodMismatch()
        if selected_method == Method.unacceptable:
            raise MethodUnacceptable()
        self.selected_method = selected_method
        self._send_request(Command.connect)

    def _handle_connect(self, data):
        '''Handle a connect reply from the server.'''

        try:
            addr, port = self._parse_result(data)
        except ReplyError as exception:
            self.connected.set_exception(exception)
        self.connected.set_result((addr, port))
        self.event('socks5_connected', (addr, port))

    def _parse_result(self, data):
        '''Parse a reply from the server.'''

        result = data[1]
        if result != 0:
            raise ReplyError(result)
        addr = self._parse_addr(data[3:-2])
        port = struct.unpack('>H', data[-2:])[0]
        return (addr, port)

    @staticmethod
    def _parse_addr(addr):
        '''Parse an address (IP or domain) from a bytestream.'''

        addr_type = addr[0]
        if addr_type == AddressType.ipv6:
            try:
                return socket.inet_ntop(socket.AF_INET6, addr[1:])
            except ValueError as e:
                raise AddressTypeUnacceptable(e)
        if addr_type == AddressType.ipv4:
            try:
                return socket.inet_ntop(socket.AF_INET, addr[1:])
            except ValueError as e:
                raise AddressTypeUnacceptable(e)
        if addr_type == AddressType.domain:
            length = addr[1]
            address = addr[2:]
            if length != len(address):
                raise Exception('Size mismatch')
            return address.decode()
        raise AddressTypeUnacceptable(addr_type)

    @staticmethod
    def _encode_addr(addr):
        '''Encode an address (IP or domain) into a bytestream.'''

        try:
            ipv6 = socket.inet_pton(socket.AF_INET6, addr)
            return b'\x04' + ipv6
        except OSError:
            pass
        try:
            ipv4 = socket.inet_aton(addr)
            return b'\x01' + ipv4
        except OSError:
            pass
        try:
            domain = punycode(addr)
            return b'\x03' + bytes([len(domain)]) + domain
        except StringprepError:
            pass
        raise Exception('Err…')
