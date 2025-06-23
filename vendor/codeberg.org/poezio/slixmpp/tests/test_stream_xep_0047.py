import asyncio
import threading
import time

import unittest
from slixmpp.test import SlixTest


class TestInBandByteStreams(SlixTest):

    def setUp(self):
        self.stream_start(plugins=['xep_0047', 'xep_0030'])

    def testOpenStream(self):
        """Test requesting a stream, successfully"""

        events = []

        def on_stream_start(stream):
            events.append('ibb_stream_start')


        self.xmpp.add_event_handler('ibb_stream_start', on_stream_start)

        self.xmpp.wrap(self.xmpp['xep_0047'].open_stream('tester@localhost/receiver',
                                                         sid='testing'))
        self.wait_()

        self.send("""
          <iq type="set" to="tester@localhost/receiver" id="1">
            <open xmlns="http://jabber.org/protocol/ibb"
                  sid="testing"
                  block-size="4096"
                  stanza="iq" />
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1"
              to="tester@localhost"
              from="tester@localhost/receiver" />
        """)

        self.assertEqual(events, ['ibb_stream_start'])

    def testAysncOpenStream(self):
        """Test requesting a stream, aysnc"""

        events = set()

        def on_stream_start(stream):
            events.add('ibb_stream_start')

        def stream_callback(iq):
            events.add('callback')

        self.xmpp.add_event_handler('ibb_stream_start', on_stream_start)

        self.xmpp.wrap(self.xmpp['xep_0047'].open_stream('tester@localhost/receiver',
                                                         sid='testing',
                                                         callback=stream_callback))
        self.wait_()

        self.send("""
          <iq type="set" to="tester@localhost/receiver" id="1">
            <open xmlns="http://jabber.org/protocol/ibb"
                  sid="testing"
                  block-size="4096"
                  stanza="iq" />
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1"
              to="tester@localhost"
              from="tester@localhost/receiver" />
        """)

        self.assertEqual(events, {'ibb_stream_start', 'callback'})

    def testSendData(self):
        """Test sending data over an in-band bytestream."""

        streams = []
        data = []

        def on_stream_start(stream):
            streams.append(stream)

        def on_stream_data(d):
            data.append(d.read())

        self.xmpp.add_event_handler('ibb_stream_start', on_stream_start)
        self.xmpp.add_event_handler('ibb_stream_data', on_stream_data)

        self.xmpp.wrap(self.xmpp['xep_0047'].open_stream('tester@localhost/receiver',
                                                         sid='testing'))
        self.wait_()

        self.send("""
          <iq type="set" to="tester@localhost/receiver" id="1">
            <open xmlns="http://jabber.org/protocol/ibb"
                  sid="testing"
                  block-size="4096"
                  stanza="iq" />
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1"
              to="tester@localhost"
              from="tester@localhost/receiver" />
        """)

        stream = streams[0]


        # Test sending data out
        self.xmpp.wrap(stream.send("Testing"))
        self.wait_()

        self.send("""
          <iq type="set" id="2"
              from="tester@localhost"
              to="tester@localhost/receiver">
            <data xmlns="http://jabber.org/protocol/ibb"
                  seq="0"
                  sid="testing">
              VGVzdGluZw==
            </data>
          </iq>
        """)

        self.recv("""
          <iq type="result" id="2"
              to="tester@localhost"
              from="tester@localhost/receiver" />
        """)

        # Test receiving data
        self.recv("""
          <iq type="set" id="A"
              to="tester@localhost"
              from="tester@localhost/receiver">
            <data xmlns="http://jabber.org/protocol/ibb"
                  seq="0"
                  sid="testing">
              aXQgd29ya3Mh
            </data>
          </iq>
        """)

        self.send("""
          <iq type="result" id="A"
              to="tester@localhost/receiver" />
        """)

        self.assertEqual(data, [b'it works!'])


suite = unittest.TestLoader().loadTestsFromTestCase(TestInBandByteStreams)
