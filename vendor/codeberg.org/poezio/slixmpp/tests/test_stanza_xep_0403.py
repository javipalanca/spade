import unittest
from slixmpp import Presence, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0403 import stanza


class TestMIXPresenceStanza(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testMIXPresence(self):
        """Test that data is converted to base64"""
        pres = Presence()
        pres['show'] = 'dnd'
        pres['status'] = 'Hey there!'
        pres['mix']['jid'] = JID('toto@example.com')
        pres['mix']['nick'] = 'Toto toto'

        self.check(pres, """
          <presence>
             <show>dnd</show>
             <status>Hey there!</status>
             <mix xmlns="urn:xmpp:mix:presence:0">
                 <jid>toto@example.com</jid>
                 <nick>Toto toto</nick>
             </mix>
          </presence>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMIXPresenceStanza)
