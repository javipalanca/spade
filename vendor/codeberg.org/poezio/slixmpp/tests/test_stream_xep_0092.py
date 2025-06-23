import threading

import unittest
from slixmpp.test import SlixTest


class TestStreamSet(SlixTest):

    def testHandleSoftwareVersionRequest(self):
        self.stream_start(mode='client', plugins=['xep_0030', 'xep_0092'])

        self.xmpp['xep_0092'].name = 'Slixmpp'
        self.xmpp['xep_0092'].version = 'dev'
        self.xmpp['xep_0092'].os = 'Linux'

        self.recv("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:version" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="1">
            <query xmlns="jabber:iq:version">
              <name>Slixmpp</name>
              <version>dev</version>
              <os>Linux</os>
            </query>
          </iq>
        """)

    def testMakeSoftwareVersionRequest(self):
        results = []

        def callback(result):
            results.append((result['software_version']['name'],
                            result['software_version']['version'],
                            result['software_version']['os']))

        self.stream_start(mode='client', plugins=['xep_0030', 'xep_0092'])

        self.xmpp['xep_0092'].get_version('foo@bar', callback=callback)

        self.send("""
          <iq type="get" id="1" to="foo@bar">
            <query xmlns="jabber:iq:version" />
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1" from="foo@bar" to="tester@localhost">
            <query xmlns="jabber:iq:version">
              <name>Foo</name>
              <version>1.0</version>
              <os>Linux</os>
            </query>
          </iq>
        """)

        expected = [('Foo', '1.0', 'Linux')]
        self.assertEqual(results, expected,
                "Did not receive expected results: %s" % results)


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamSet)
