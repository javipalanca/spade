
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import socket
from queue import Queue


class TestSocket(object):

    """
    A dummy socket that reads and writes to queues instead
    of an actual networking socket.

    Methods:
        next_sent -- Return the next sent stanza.
        recv_data -- Make a stanza available to read next.
        recv      -- Read the next stanza from the socket.
        send      -- Write a stanza to the socket.
        makefile  -- Dummy call, returns self.
        read      -- Read the next stanza from the socket.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new test socket.

        Arguments:
            Same as arguments for socket.socket
        """
        self.socket = socket.socket(*args, **kwargs)
        self.recv_queue = Queue()
        self.send_queue = Queue()
        self.is_live = False
        self.disconnected = False

    def __getattr__(self, name):
        """
        Return attribute values of internal, dummy socket.

        Some attributes and methods are disabled to prevent the
        socket from connecting to the network.

        Arguments:
            name -- Name of the attribute requested.
        """

        def dummy(*args):
            """Method to do nothing and prevent actual socket connections."""
            return None

        overrides = {'connect': dummy,
                     'close': dummy,
                     'shutdown': dummy}

        return overrides.get(name, getattr(self.socket, name))

    # ------------------------------------------------------------------
    # Testing Interface

    def next_sent(self, timeout=None):
        """
        Get the next stanza that has been 'sent'.

        Arguments:
            timeout -- Optional timeout for waiting for a new value.
        """
        args = {'block': False}
        if timeout is not None:
            args = {'block': True, 'timeout': timeout}
        try:
            return self.send_queue.get(**args)
        except:
            return None

    def recv_data(self, data):
        """
        Add data to the receiving queue.

        Arguments:
            data -- String data to 'write' to the socket to be received
                    by the XMPP client.
        """
        self.recv_queue.put(data)

    def disconnect_error(self):
        """
        Simulate a disconnect error by raising a socket.error exception
        for any current or further socket operations.
        """
        self.disconnected = True

    # ------------------------------------------------------------------
    # Socket Interface

    def recv(self, *args, **kwargs):
        """
        Read a value from the received queue.

        Arguments:
            Placeholders. Same as for socket.Socket.recv.
        """
        if self.disconnected:
            raise socket.error
        return self.read(block=True)

    def send(self, data):
        """
        Send data by placing it in the send queue.

        Arguments:
            data -- String value to write.
        """
        if self.disconnected:
            raise socket.error
        self.send_queue.put(data)
        return len(data)

    # ------------------------------------------------------------------
    # File Socket

    def makefile(self, *args, **kwargs):
        """
        File socket version to use with ElementTree.

        Arguments:
            Placeholders, same as socket.Socket.makefile()
        """
        return self

    def read(self, block=True, timeout=None, **kwargs):
        """
        Implement the file socket interface.

        Arguments:
            block   -- Indicate if the read should block until a
                       value is ready.
            timeout -- Time in seconds a block should last before
                       returning None.
        """
        if self.disconnected:
            raise socket.error
        if timeout is not None:
            block = True
        try:
            return self.recv_queue.get(block, timeout)
        except:
            return None

class TestTransport(object):

    """
    A transport socket that reads and writes to queues instead
    of an actual networking socket.

    Methods:
        next_sent -- Return the next sent stanza.
        recv_data -- Make a stanza available to read next.
        recv      -- Read the next stanza from the socket.
        send      -- Write a stanza to the socket.
        makefile  -- Dummy call, returns self.
        read      -- Read the next stanza from the socket.
    """

    def __init__(self, xmpp):
        self.xmpp = xmpp
        self.socket = TestSocket()
    # ------------------------------------------------------------------
    # Testing Interface

    def next_sent(self, timeout=None):
        """
        Get the next stanza that has been 'sent'.

        Arguments:
            timeout -- Optional timeout for waiting for a new value.
        """
        return self.socket.next_sent()

    def disconnect_error(self):
        """
        Simulate a disconnect error by raising a socket.error exception
        for any current or further socket operations.
        """
        self.socket.disconnect_error()

    # ------------------------------------------------------------------
    # Socket Interface

    def recv(self, *args, **kwargs):
        """
        Read a value from the received queue.

        Arguments:
            Placeholders. Same as for socket.Socket.recv.
        """
        return 

    def write(self, data):
        """
        Send data by placing it in the send queue.

        Arguments:
            data -- String value to write.
        """
        self.socket.send(data)
        return len(data)

    # ------------------------------------------------------------------
    # File Socket

    def makefile(self, *args, **kwargs):
        """
        File socket version to use with ElementTree.

        Arguments:
            Placeholders, same as socket.Socket.makefile()
        """
        return self

    def read(self, block=True, timeout=None, **kwargs):
        """
        Implement the file socket interface.

        Arguments:
            block   -- Indicate if the read should block until a
                       value is ready.
            timeout -- Time in seconds a block should last before
                       returning None.
        """
        return self.socket.recv(block, timeout, **kwargs)

    def get_extra_info(self, name, *args, default=None, **kwargs):
        info = {
            'socket': self.socket
        }
        return info.get(name, default)

    def abort(self, *args, **kwargs):
        return

    def close(self, *args, **kwargs):
        return

