import unittest
from slixmpp import Presence, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0437 import stanza


class TestRAI(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testResponse(self):
        presence = Presence()
        presence['rai']['activities'] = [
            JID('toto@titi'),
            JID('coucou@coucou'),
        ]
        self.check(presence, """
<presence>
  <rai xmlns="urn:xmpp:rai:0">
    <activity>toto@titi</activity>
    <activity>coucou@coucou</activity>
  </rai>
</presence>
        """, use_values=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestRAI)
