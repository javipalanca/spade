from slixmpp.xmlstream.matcher import MatchXPath
from slixmpp.xmlstream.handler import Callback
from slixmpp.exceptions import XMPPError
import unittest
from slixmpp.test import SlixTest


class TestStreamExceptions(SlixTest):
    """
    Test handling roster updates.
    """

    def testExceptionContinueWorking(self):
        """Test that Slixmpp continues to respond after an XMPPError is raised."""

        def message(msg):
            raise XMPPError(clear=True)

        self.stream_start()
        self.xmpp.add_event_handler('message', message)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="500">
              <undefined-condition
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
            </error>
          </message>
        """)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="500">
              <undefined-condition
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
            </error>
          </message>
        """)

    def testXMPPErrorException(self):
        """Test raising an XMPPError exception."""

        def message(msg):
            raise XMPPError(condition='feature-not-implemented',
                            text="We don't do things that way here.",
                            etype='cancel',
                            extension='foo',
                            extension_ns='foo:error',
                            extension_args={'test': 'true'})

        self.stream_start()
        self.xmpp.add_event_handler('message', message)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="501">
              <feature-not-implemented
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
              <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">
                We don&apos;t do things that way here.
              </text>
              <foo xmlns="foo:error" test="true" />
            </error>
          </message>
        """, use_values=False)

    def testIqErrorException(self):
        """Test using error exceptions with Iq stanzas."""

        def handle_iq(iq):
            raise XMPPError(condition='feature-not-implemented',
                            text="We don't do things that way here.",
                            etype='cancel',
                            clear=False)

        self.stream_start()
        self.xmpp.register_handler(
                Callback(
                    'Test Iq',
                     MatchXPath('{%s}iq/{test}query' % self.xmpp.default_ns),
                     handle_iq))

        self.recv("""
          <iq type="get" id="0">
            <query xmlns="test" />
          </iq>
        """)

        self.send("""
          <iq type="error" id="0">
            <query xmlns="test" />
            <error type="cancel" code="501">
              <feature-not-implemented
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
              <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">
                We don&apos;t do things that way here.
              </text>
            </error>
          </iq>
        """, use_values=False)

    def testUnknownException(self):
        """Test raising an generic exception in a handler."""

        raised_errors = []

        def message(msg):
            raise ValueError("Did something wrong")

        def catch_error(*args, **kwargs):
            raised_errors.append(True)

        self.stream_start()
        self.xmpp.exception = catch_error
        self.xmpp.add_event_handler('message', message)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="500">
              <undefined-condition
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
              <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">
                Slixmpp got into trouble.
              </text>
            </error>
          </message>
        """)

        self.assertEqual(raised_errors, [True], "Exception was not raised: %s" % raised_errors)

    def testUnknownException(self):
        """Test Slixmpp continues to respond after an unknown exception."""

        raised_errors = []

        def message(msg):
            raise ValueError("Did something wrong")

        def catch_error(*args, **kwargs):
            raised_errors.append(True)

        self.stream_start()
        self.xmpp.exception = catch_error
        self.xmpp.add_event_handler('message', message)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="500">
              <undefined-condition
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
              <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">
                Slixmpp got into trouble.
              </text>
            </error>
          </message>
        """)

        self.recv("""
          <message>
            <body>This is going to cause an error.</body>
          </message>
        """)

        self.send("""
          <message type="error">
            <error type="cancel" code="500">
              <undefined-condition
                  xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
              <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">
                Slixmpp got into trouble.
              </text>
            </error>
          </message>
        """)

        self.assertEqual(raised_errors, [True, True], "Exceptions were not raised: %s" % raised_errors)


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamExceptions)
