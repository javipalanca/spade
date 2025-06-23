import threading

import unittest
from slixmpp.test import SlixTest


class TestOOB(SlixTest):

    def testSendOOB(self):
        """Test sending an OOB transfer request."""
        self.stream_start(plugins=['xep_0066', 'xep_0030'])

        url = 'http://github.com/fritzy/Slixmpp/blob/master/README'

        self.xmpp['xep_0066'].send_oob('user@example.com', url,
                                       desc='Slixmpp README')

        self.send("""
          <iq to="user@example.com" type="set" id="1">
            <query xmlns="jabber:iq:oob">
              <url>http://github.com/fritzy/Slixmpp/blob/master/README</url>
              <desc>Slixmpp README</desc>
            </query>
          </iq>
        """)

        self.recv("""
          <iq id="1" type="result"
              to="tester@localhost"
              from="user@example.com" />
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestOOB)
