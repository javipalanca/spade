import unittest
from slixmpp import Iq, Message, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0405 import stanza
from slixmpp.plugins.xep_0369 import stanza as mstanza
from slixmpp.plugins.xep_0405.mix_pam import BASE_NODES


class TestMIXPAMStanza(SlixTest):

    def setUp(self):
        stanza.register_plugins()
        mstanza.register_plugins()

    def testMIXPAMJoin(self):
        """Test that data is converted to base64"""
        iq = Iq()
        iq['type'] = 'set'
        iq['client_join']['channel'] = JID('mix@example.com')
        for node in BASE_NODES:
            sub = mstanza.Subscribe()
            sub['node'] = node
            iq['client_join']['mix_join'].append(sub)
        iq['client_join']['mix_join']['nick'] = 'Toto'

        self.check(iq, """
          <iq type="set">
              <client-join xmlns='urn:xmpp:mix:pam:2' channel='mix@example.com'>
                  <join xmlns='urn:xmpp:mix:core:1'>
                      <subscribe node='urn:xmpp:mix:nodes:messages'/>
                      <subscribe node='urn:xmpp:mix:nodes:participants'/>
                      <subscribe node='urn:xmpp:mix:nodes:info'/>
                      <nick>Toto</nick>
                  </join>
              </client-join>
          </iq>
        """)


    def testMIXPAMLeave(self):
        iq = Iq()
        iq['type'] = 'set'
        iq['client_leave']['channel'] = JID('mix@example.com')
        iq['client_leave'].enable('mix_leave')

        self.check(iq, """
          <iq type="set">
              <client-leave xmlns='urn:xmpp:mix:pam:2' channel='mix@example.com'>
                  <leave xmlns='urn:xmpp:mix:core:1'/>
              </client-leave>
          </iq>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMIXPAMStanza)
