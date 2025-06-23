import unittest
from slixmpp import Iq, Message, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0369 import stanza
from slixmpp.plugins.xep_0060 import stanza as pstanza
from slixmpp.plugins.xep_0369.mix_core import BASE_NODES


class TestMIXStanza(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testMIXJoin(self):
        """Test that data is converted to base64"""
        iq = Iq()
        iq['type'] = 'set'
        for node in BASE_NODES:
            sub = stanza.Subscribe()
            sub['node'] = node
            iq['mix_join'].append(sub)
        iq['mix_join']['nick'] = 'Toto'

        self.check(iq, """
          <iq type="set">
              <join xmlns='urn:xmpp:mix:core:1'>
                  <subscribe node='urn:xmpp:mix:nodes:messages'/>
                  <subscribe node='urn:xmpp:mix:nodes:participants'/>
                  <subscribe node='urn:xmpp:mix:nodes:info'/>
                  <nick>Toto</nick>
              </join>
          </iq>
        """)

    def testMIXUpdateSub(self):
        iq = Iq()
        iq['type'] = 'set'
        iq.enable('mix_updatesub')
        sub = stanza.Subscribe()
        sub['node'] = 'urn:xmpp:mix:nodes:someothernode'
        iq['mix_updatesub'].append(sub)

        self.check(iq, """
          <iq type="set">
              <update-subscription xmlns='urn:xmpp:mix:core:1'>
                  <subscribe node='urn:xmpp:mix:nodes:someothernode'/>
              </update-subscription>
          </iq>
        """)

    def testMIXLeave(self):
        iq = Iq()
        iq['type'] = 'set'
        iq.enable('mix_leave')

        self.check(iq, """
          <iq type="set">
              <leave xmlns='urn:xmpp:mix:core:1'/>
          </iq>
        """)

    def testMIXSetNick(self):
        iq = Iq()
        iq['type'] = 'set'
        iq['mix_setnick']['nick'] = 'A nick'

        self.check(iq, """
          <iq type="set">
              <setnick xmlns='urn:xmpp:mix:core:1'>
                <nick>A nick</nick>
              </setnick>
          </iq>
        """)

    def testMIXMessage(self):
        msg = Message()
        msg['type'] = 'groupchat'
        msg['body'] = 'This is a message body'
        msg['mix']['nick'] = 'A nick'
        msg['mix']['jid'] = JID('toto@example.com')

        self.check(msg, """
            <message type="groupchat">
                <body>This is a message body</body>
                <mix xmlns="urn:xmpp:mix:core:1">
                    <nick>A nick</nick>
                    <jid>toto@example.com</jid>
                </mix>
            </message>
        """)

    def testMIXNewParticipant(self):
        msg = Message()
        msg['pubsub_event']['items']['node'] = 'urn:xmpp:mix:nodes:participants'
        item = pstanza.EventItem()
        item['id'] = '123456'
        item['mix_participant']['jid'] = JID('titi@example.com')
        item['mix_participant']['nick'] = 'Titi'
        msg['pubsub_event']['items'].append(item)

        self.check(msg, """
            <message>
              <event xmlns='http://jabber.org/protocol/pubsub#event'>
                <items node='urn:xmpp:mix:nodes:participants'>
                  <item id='123456'>
                    <participant xmlns='urn:xmpp:mix:core:1'>
                      <jid>titi@example.com</jid>
                      <nick>Titi</nick>
                    </participant>
                  </item>
                </items>
              </event>
            </message>
        """, use_values=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMIXStanza)
