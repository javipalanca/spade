import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0308 import Replace
from slixmpp.xmlstream import register_stanza_plugin


class TestCorrectStanza(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, Replace)

    def testBuild(self):
        """Test that the element is created correctly."""
        msg = Message()
        msg['type'] = 'chat'
        msg['replace']['id'] = 'toto123'

        self.check(msg, """
          <message type="chat">
            <replace xmlns="urn:xmpp:message-correct:0" id="toto123"/>
          </message>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestCorrectStanza)
