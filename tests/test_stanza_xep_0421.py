import unittest
from slixmpp import JID, Message
from slixmpp.test import SlixTest
import slixmpp.plugins.xep_0421 as xep_0421
from slixmpp.xmlstream import register_stanza_plugin


class TestOccupantId(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, xep_0421.stanza.OccupantId)

    def testReadOccupantId(self):
        result = """
          <message type='groupchat' from='foo@muc/nick1'>
            <body>Some message</body>
            <occupant-id xmlns='urn:xmpp:occupant-id:0' id='unique-id1'/>
          </message>
        """

        msg = self.Message()
        msg['type'] = 'groupchat'
        msg['from'] = JID('foo@muc/nick1')
        msg['body'] = 'Some message'
        msg['occupant-id']['id'] = 'unique-id1'

        self.check(msg, result)

suite = unittest.TestLoader().loadTestsFromTestCase(TestOccupantId)
