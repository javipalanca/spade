import unittest
from slixmpp import Message, Iq, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0424 import stanza as stanza424
from slixmpp.plugins.xep_0425 import stanza


class TestModeration(SlixTest):

    def setUp(self):
        stanza424.register_plugins()
        stanza.register_plugins()

    def testModerate(self):
        iq = Iq()
        iq['type'] = 'set'
        iq['id'] = 'a'
        iq['moderate']['id'] = 'some-id'
        iq['moderate'].enable('retract')
        iq['moderate']['reason'] = 'R'

        self.check(iq, """
<iq type='set' id='a'>
  <moderate xmlns='urn:xmpp:message-moderate:1' id='some-id'>
    <retract xmlns='urn:xmpp:message-retract:1'/>
    <reason>R</reason>
  </moderate>
</iq>
        """)

    def testModerated(self):
        message = Message()
        message['retract']['id'] = 'some-id'
        message['retract']['moderated']['by'] = JID('toto@titi')
        message['retract']['moderated']['occupant-id']['id'] = 'oc-id'
        message['retract']['reason'] = 'R'

        self.check(message, """
<message>
  <retract id='some-id' xmlns='urn:xmpp:message-retract:1'>
    <moderated by='toto@titi' xmlns='urn:xmpp:message-moderate:1'>
      <occupant-id xmlns="urn:xmpp:occupant-id:0" id="oc-id" />
    </moderated>
    <reason>R</reason>
  </retract>
</message>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestModeration)
