import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
import slixmpp.plugins.xep_0380 as xep_0380
from slixmpp.xmlstream import register_stanza_plugin


class TestEME(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, xep_0380.stanza.Encryption)

    def testCreateEME(self):
        """Testing creating EME."""

        xmlstring = """
          <message>
            <encryption xmlns="urn:xmpp:eme:0" namespace="%s"%s />
          </message>
        """

        msg = self.Message()
        self.check(msg, "<message />")

        msg['eme']['namespace'] = 'urn:xmpp:otr:0'
        self.check(msg, xmlstring % ('urn:xmpp:otr:0', ''))

        msg['eme']['namespace'] = 'urn:xmpp:openpgp:0'
        self.check(msg, xmlstring % ('urn:xmpp:openpgp:0', ''))

        msg['eme']['name'] = 'OX'
        self.check(msg, xmlstring % ('urn:xmpp:openpgp:0', ' name="OX"'))

        del msg['eme']
        self.check(msg, "<message />")

suite = unittest.TestLoader().loadTestsFromTestCase(TestEME)
