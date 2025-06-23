import time

import unittest
from slixmpp.test import SlixTest


class TestStreamChatStates(SlixTest):

    def testChatStates(self):
        self.stream_start(mode='client', plugins=['xep_0030', 'xep_0085'])

        results = []

        def handle_state(msg):
            results.append(msg['chat_state'])

        self.xmpp.add_event_handler('chatstate_active', handle_state)
        self.xmpp.add_event_handler('chatstate_inactive', handle_state)
        self.xmpp.add_event_handler('chatstate_paused', handle_state)
        self.xmpp.add_event_handler('chatstate_gone', handle_state)
        self.xmpp.add_event_handler('chatstate_composing', handle_state)

        self.recv("""
          <message>
            <active xmlns="http://jabber.org/protocol/chatstates" />
          </message>
        """)
        self.recv("""
          <message>
            <inactive xmlns="http://jabber.org/protocol/chatstates" />
          </message>
        """)
        self.recv("""
          <message>
            <paused xmlns="http://jabber.org/protocol/chatstates" />
          </message>
        """)
        self.recv("""
          <message>
            <composing xmlns="http://jabber.org/protocol/chatstates" />
          </message>
        """)
        self.recv("""
          <message>
            <gone xmlns="http://jabber.org/protocol/chatstates" />
          </message>
        """)

        expected = ['active', 'inactive', 'paused', 'composing', 'gone']
        self.assertTrue(results == expected,
                "Chat state event not handled: %s" % results)


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamChatStates)
