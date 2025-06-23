import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.xmlstream import ET
from slixmpp.plugins.xep_0422 import stanza


class TestFastening(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testFastenExternal(self):
        message = Message()
        message['apply_to']['id'] = 'some-id'
        message['apply_to'].xml.append(
            ET.fromstring('<test xmlns="urn:tmp:test">Test</test>')
        )
        message['apply_to']['external']['name'] = 'body'
        message['body'] = 'Toto'

        self.check(message, """
<message>
  <apply-to xmlns="urn:xmpp:fasten:0" id="some-id">
      <test xmlns="urn:tmp:test">Test</test>
      <external name='body'/>
  </apply-to>
  <body>Toto</body>
</message>
        """, use_values=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestFastening)
