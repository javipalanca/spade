"""TLS Lite + httplib."""

import socket
import httplib
from tlslite.Checker import Checker
from tlslite.TLSConnection import TLSConnection


class HTTPBaseTLSConnection(httplib.HTTPConnection):
    """This abstract class provides a framework for adding TLS support
    to httplib."""

    default_port = 443

    def __init__(self, host, port=None, strict=None):
        httplib.HTTPConnection.__init__(self, host, port, strict)
        self.tlsSession = None

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(sock, 'settimeout'):
            sock.settimeout(10)
        sock.connect((self.host, self.port))

        #Use a TLSConnection to emulate a socket
        self.sock = TLSConnection(sock)

        #When httplib closes this, close the socket
        self.sock.closeSocket = True
        self._handshake(self.sock, self.tlsSession)
        self.tlsSession = self.sock.session

    def _handshake(self, tlsConnection, tlsSession):
        """Called to perform some sort of handshake.

        This method must be overridden in a subclass to do some type of
        handshake.  This method will be called after the socket has
        been connected but before any data has been sent.  If this
        method does not raise an exception, the TLS connection will be
        considered valid.

        This method may (or may not) be called every time an HTTP
        request is performed, depending on whether the underlying HTTP
        connection is persistent.  The first time this method is
        called, tlsSession will be None, but on subsequent requests it
        will contain the session from the previous connection.  This
        session should be passed to the handshake function to enable
        session resumption.

        @type tlsConnection: L{tlslite.TLSConnection.TLSConnection}
        @param tlsConnection: The connection to perform the handshake
        on.

        @type tlsSession: L{tlslite.Session.Session}
        @param tlsSession: A Session instance or None.  This should be
        passed to the handshake function to enable session resumption.
        """
        raise NotImplementedError()


class HTTPTLSConnection(HTTPBaseTLSConnection):
    """This class extends L{HTTPBaseTLSConnection} to support the
    common types of handshaking."""

    def __init__(self, host, port=None,
                 username=None, password=None, sharedKey=None,
                 certChain=None, privateKey=None,
                 cryptoID=None, protocol=None,
                 x509Fingerprint=None,
                 x509TrustList=None, x509CommonName=None,
                 settings = None):
        """Create a new HTTPTLSConnection.

        For client authentication, use one of these argument
        combinations:
         - username, password (SRP)
         - username, sharedKey (shared-key)
         - certChain, privateKey (certificate)

        For server authentication, you can either rely on the
        implicit mutual authentication performed by SRP or
        shared-keys, or you can do certificate-based server
        authentication with one of these argument combinations:
         - cryptoID[, protocol] (requires cryptoIDlib)
         - x509Fingerprint
         - x509TrustList[, x509CommonName] (requires cryptlib_py)

        Certificate-based server authentication is compatible with
        SRP or certificate-based client authentication.  It is
        not compatible with shared-keys.

        The constructor does not perform the TLS handshake itself, but
        simply stores these arguments for later.  The handshake is
        performed only when this class needs to connect with the
        server.  Thus you should be prepared to handle TLS-specific
        exceptions when calling methods inherited from
        L{httplib.HTTPConnection} such as request(), connect(), and
        send().  See the client handshake functions in
        L{tlslite.TLSConnection.TLSConnection} for details on which
        exceptions might be raised.

        @type host: str
        @param host: Server to connect to.

        @type port: int
        @param port: Port to connect to.

        @type username: str
        @param username: SRP or shared-key username.  Requires the
        'password' or 'sharedKey' argument.

        @type password: str
        @param password: SRP password for mutual authentication.
        Requires the 'username' argument.

        @type sharedKey: str
        @param sharedKey: Shared key for mutual authentication.
        Requires the 'username' argument.

        @type certChain: L{tlslite.X509CertChain.X509CertChain} or
        L{cryptoIDlib.CertChain.CertChain}
        @param certChain: Certificate chain for client authentication.
        Requires the 'privateKey' argument.  Excludes the SRP or
        shared-key related arguments.

        @type privateKey: L{tlslite.utils.RSAKey.RSAKey}
        @param privateKey: Private key for client authentication.
        Requires the 'certChain' argument.  Excludes the SRP or
        shared-key related arguments.

        @type cryptoID: str
        @param cryptoID: cryptoID for server authentication.  Mutually
        exclusive with the 'x509...' arguments.

        @type protocol: str
        @param protocol: cryptoID protocol URI for server
        authentication.  Requires the 'cryptoID' argument.

        @type x509Fingerprint: str
        @param x509Fingerprint: Hex-encoded X.509 fingerprint for
        server authentication.  Mutually exclusive with the 'cryptoID'
        and 'x509TrustList' arguments.

        @type x509TrustList: list of L{tlslite.X509.X509}
        @param x509TrustList: A list of trusted root certificates.  The
        other party must present a certificate chain which extends to
        one of these root certificates.  The cryptlib_py module must be
        installed to use this parameter.  Mutually exclusive with the
        'cryptoID' and 'x509Fingerprint' arguments.

        @type x509CommonName: str
        @param x509CommonName: The end-entity certificate's 'CN' field
        must match this value.  For a web server, this is typically a
        server name such as 'www.amazon.com'.  Mutually exclusive with
        the 'cryptoID' and 'x509Fingerprint' arguments.  Requires the
        'x509TrustList' argument.

        @type settings: L{tlslite.HandshakeSettings.HandshakeSettings}
        @param settings: Various settings which can be used to control
        the ciphersuites, certificate types, and SSL/TLS versions
        offered by the client.
        """
        HTTPBaseTLSConnection.__init__(self, host, port)

        self.username = None
        self.password = None
        self.sharedKey = None
        self.certChain = None
        self.privateKey = None
        self.checker = None

        #SRP Authentication
        if username and password and not \
                (sharedKey or certChain or privateKey):
            self.username = username
            self.password = password

        #Shared Key Authentication
        elif username and sharedKey and not \
                (password or certChain or privateKey):
            self.username = username
            self.sharedKey = sharedKey

        #Certificate Chain Authentication
        elif certChain and privateKey and not \
                (username or password or sharedKey):
            self.certChain = certChain
            self.privateKey = privateKey

        #No Authentication
        elif not password and not username and not \
                sharedKey and not certChain and not privateKey:
            pass

        else:
            raise ValueError("Bad parameters")

        #Authenticate the server based on its cryptoID or fingerprint
        if sharedKey and (cryptoID or protocol or x509Fingerprint):
            raise ValueError("Can't use shared keys with other forms of"\
                             "authentication")

        self.checker = Checker(cryptoID, protocol, x509Fingerprint,
                               x509TrustList, x509CommonName)
        self.settings = settings

    def _handshake(self, tlsConnection, tlsSession):
        if self.username and self.password:
            tlsConnection.handshakeClientSRP(username=self.username,
                                             password=self.password,
                                             checker=self.checker,
                                             settings=self.settings,
                                             session=tlsSession)
        elif self.username and self.sharedKey:
            tlsConnection.handshakeClientSharedKey(username=self.username,
                                                   sharedKey=self.sharedKey,
                                                   settings=self.settings)
        else:
            tlsConnection.handshakeClientCert(certChain=self.certChain,
                                              privateKey=self.privateKey,
                                              checker=self.checker,
                                              settings=self.settings,
                                              session=tlsSession)