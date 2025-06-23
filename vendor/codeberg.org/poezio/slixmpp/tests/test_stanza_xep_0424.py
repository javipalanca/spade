import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0424 import stanza


class TestRetraction(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testRetract(self):
        message = Message()
        message['retract']['id'] = 'some-id'

        self.check(message, """
<message>
  <retract xmlns="urn:xmpp:message-retract:1" id="some-id"/>
</message>
        """, use_values=False)

    def testRetracted(self):
        message = Message()
        message['retracted']['stamp'] = '2019-09-20T23:09:32Z'
        message['retracted']['id'] = 'originid'

        self.check(message, """
<message>
  <retracted stamp="2019-09-20T23:09:32Z"
             xmlns="urn:xmpp:message-retract:1"
             id="originid" /> 
</message>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestRetraction)
