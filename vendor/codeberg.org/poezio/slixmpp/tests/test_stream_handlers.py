import time
import threading

import unittest
from slixmpp.test import SlixTest
from slixmpp.exceptions import IqTimeout
from slixmpp import Callback, MatchXPath


class TestHandlers(SlixTest):
    """
    Test using handlers and waiters.
    """

    def setUp(self):
        self.stream_start()

    def testCallback(self):
        """Test using stream callback handlers."""

        def callback_handler(stanza):
            self.xmpp.send_raw("""
              <message>
                <body>Success!</body>
              </message>
            """)

        callback = Callback('Test Callback',
                            MatchXPath('{test}tester'),
                            callback_handler)

        self.xmpp.register_handler(callback)

        self.recv("""<tester xmlns="test" />""")

        msg = self.Message()
        msg['body'] = 'Success!'
        self.send(msg)

    def testWaiter(self):
        """Test using stream waiter handler."""

        def waiter_handler(stanza):
            iq = self.xmpp.Iq()
            iq['id'] = 'test'
            iq['type'] = 'set'
            iq['query'] = 'test'
            def callback_waiter(result):
                self.xmpp.send_raw("""
                  <message>
                    <body>Successful: %s</body>
                  </message>
                """ % result['query'])
            iq.send(callback=callback_waiter)

        self.xmpp.add_event_handler('message', waiter_handler)

        # Send message to trigger waiter_handler
        self.recv("""
          <message>
            <body>Testing</body>
          </message>
        """)

        # Check that Iq was sent by waiter_handler
        iq = self.Iq()
        iq['id'] = 'test'
        iq['type'] = 'set'
        iq['query'] = 'test'
        self.send(iq)

        # Send the reply Iq
        self.recv("""
          <iq id="test" type="result">
            <query xmlns="test" />
          </iq>
        """)

        # Check that waiter_handler received the reply
        msg = self.Message()
        msg['body'] = 'Successful: test'
        self.send(msg)

    def testWaiterTimeout(self):
        """Test that waiter handler is removed after timeout."""

        def waiter_handler(stanza):
            iq = self.xmpp.Iq()
            iq['id'] = 'test2'
            iq['type'] = 'set'
            iq['query'] = 'test2'
            try:
                reply = iq.send(timeout=0)
            except IqTimeout:
                pass

        self.xmpp.add_event_handler('message', waiter_handler)

        # Start test by triggerig waiter_handler
        self.recv("""<message><body>Start Test</body></message>""")

        # Check that Iq was sent to trigger start of timeout period
        iq = self.Iq()
        iq['id'] = 'test2'
        iq['type'] = 'set'
        iq['query'] = 'test2'
        self.send(iq)

        # Check that the waiter is no longer registered
        waiter_exists = self.xmpp.remove_handler('IqWait_test2')

        self.assertTrue(waiter_exists == False,
            "Waiter handler was not removed.")

    def testIqCallback(self):
        """Test that iq.send(callback=handle_foo) works."""
        events = []

        def handle_foo(iq):
            events.append('foo')

        iq = self.Iq()
        iq['type'] = 'get'
        iq['id'] = 'test-foo'
        iq['to'] = 'user@localhost'
        iq['query'] = 'foo'
        iq.send(callback=handle_foo)

        self.send("""
          <iq type="get" id="test-foo" to="user@localhost">
            <query xmlns="foo" />
          </iq>
        """)

        self.recv("""
          <iq type="result" id="test-foo"
              to="test@localhost"
              from="user@localhost">
            <query xmlns="foo">
              <data />
            </query>
          </iq>
        """)

        self.assertTrue(events == ['foo'],
                "Iq callback was not executed: %s" % events)

    def testMultipleHandlersForStanza(self):
        """
        Test that multiple handlers for a single stanza work
        without clobbering each other.
        """

        def handler_1(msg):
            msg.reply("Handler 1: %s" % msg['body']).send()

        def handler_2(msg):
            msg.reply("Handler 2: %s" % msg['body']).send()

        def handler_3(msg):
            msg.reply("Handler 3: %s" % msg['body']).send()

        self.xmpp.add_event_handler('message', handler_1)
        self.xmpp.add_event_handler('message', handler_2)
        self.xmpp.add_event_handler('message', handler_3)

        self.recv("""
          <message to="tester@localhost" from="user@example.com">
            <body>Testing</body>
          </message>
        """)


        # This test is brittle, depending on the fact that handlers
        # will be checked in the order they are registered.
        self.send("""
          <message to="user@example.com">
            <body>Handler 1: Testing</body>
          </message>
        """)
        self.send("""
          <message to="user@example.com">
            <body>Handler 2: Testing</body>
          </message>
        """)
        self.send("""
          <message to="user@example.com">
            <body>Handler 3: Testing</body>
          </message>
        """)

    def testWrongSender(self):
      """
      Test that using the wrong sender JID in a IQ result
      doesn't trigger handlers.
      """

      events = []

      def callback(result):
          events.append(result['from'].full)

      iq = self.Iq()
      iq['id'] = 'test'
      iq['to'] = 'tester@slixmpp.com/test'
      iq['type'] = 'set'
      iq['query'] = 'test'
      iq.send(callback=callback)

      self.recv("""
        <iq id="test" from="evil@slixmpp.com/bad" type="result">
          <query xmlns="test" />
        </iq>
      """)
      self.recv("""
        <iq id="test" from="evil2@slixmpp.com" type="result">
          <query xmlns="test" />
        </iq>
      """)
      self.recv("""
        <iq id="test" from="evil.com" type="result">
          <query xmlns="test" />
        </iq>
      """)

      # Now for a good one
      self.recv("""
        <iq id="test" from="tester@slixmpp.com/test" type="result">
          <query xmlns="test" />
        </iq>
      """)

      self.assertEqual(events, ['tester@slixmpp.com/test'], "Did not timeout on bad sender")


suite = unittest.TestLoader().loadTestsFromTestCase(TestHandlers)
