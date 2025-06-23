"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2020 Mathieu Pasquet
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0444 import XEP_0444
import slixmpp.plugins.xep_0444.stanza as stanza
from slixmpp.xmlstream import register_stanza_plugin

try:
    import emoji
except ImportError:
    emoji = None


class TestReactions(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, stanza.Reactions)
        register_stanza_plugin(stanza.Reactions, stanza.Reaction, iterable=True)

    def testCreateReactions(self):
        """Testing creating Reactions."""

        xmlstring = """
          <message>
              <reactions xmlns="urn:xmpp:reactions:0" id="abcd">
                  <reaction>😃</reaction>
                  <reaction>🤗</reaction>
              </reactions>
          </message>
        """

        msg = self.Message()
        msg['reactions']['id'] = 'abcd'
        msg['reactions']['values'] = ['😃', '🤗']

        self.check(msg, xmlstring, use_values=False)

        self.assertEqual({'😃', '🤗'}, msg['reactions']['values'])


    @unittest.skipIf(emoji is None, 'Emoji package not installed')
    def testCreateReactionsUnrestricted(self):
        """Testing creating Reactions with the extra all_chars arg."""
        xmlstring = """
          <message>
              <reactions xmlns="urn:xmpp:reactions:0" id="abcd">
                  <reaction>😃</reaction>
                  <reaction>🤗</reaction>
                  <reaction>toto</reaction>
              </reactions>
          </message>
        """

        msg = self.Message()
        msg['reactions']['id'] = 'abcd'
        msg['reactions'].set_values(['😃', '🤗', 'toto'], all_chars=True)

        self.check(msg, xmlstring, use_values=False)

        self.assertEqual({'😃', '🤗'}, msg['reactions']['values'])
        self.assertEqual({'😃', '🤗', 'toto'}, msg['reactions'].get_values(all_chars=True))
        with self.assertRaises(ValueError):
            msg['reactions'].set_values(['😃', '🤗', 'toto'], all_chars=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestReactions)
