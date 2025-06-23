import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
import slixmpp.plugins.xep_0184 as xep_0184
from slixmpp.xmlstream import register_stanza_plugin


class TestReciept(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, xep_0184.Request)
        register_stanza_plugin(Message, xep_0184.Received)

    def testCreateRequest(self):
        request = """
          <message>
            <request xmlns="urn:xmpp:receipts" />
          </message>
        """

        msg = self.Message()

        self.assertEqual(msg['request_receipt'], False)

        msg['request_receipt'] = True
        self.check(msg, request)

    def testCreateReceived(self):
        received = """
          <message>
            <received xmlns="urn:xmpp:receipts" id="1" />
          </message>
        """

        msg = self.Message()

        msg['receipt'] = '1'
        self.check(msg, received)


suite = unittest.TestLoader().loadTestsFromTestCase(TestReciept)
