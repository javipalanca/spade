import unittest
from slixmpp.test import SlixTest
from slixmpp import JID


class TestMIXPAM(SlixTest):

    def setUp(self):
        self.stream_start(plugins=['xep_0405'])

    def testGetRosterEmpty(self):
        """Test requesting an empty annotated roster"""

        fut = self.xmpp.wrap(self.xmpp['xep_0405'].get_mix_roster())

        self.wait_()
        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster">
                <annotate xmlns='urn:xmpp:mix:roster:0' />
            </query>
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1"
              to="tester@localhost" />
        """)

        result = self.run_coro(fut)

    def testGetRoster(self):
        """Test requesting an annotated roster"""

        fut = self.xmpp.wrap(self.xmpp['xep_0405'].get_mix_roster())

        self.wait_()
        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster">
                <annotate xmlns='urn:xmpp:mix:roster:0' />
            </query>
          </iq>
        """)

        self.recv("""
          <iq type="result" id="1" to="tester@localhost">
            <query xmlns="jabber:iq:roster">
              <item jid='romeo@example.net'/>
              <item jid='juliet@example.net'/>
              <item jid='balcony@example.net'>
                <channel xmlns='urn:xmpp:mix:roster:0'
                         participant-id='123456'/>
              </item>
            </query>
          </iq>
        """)

        self.wait_()
        contacts, channels = fut.result()
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]['jid'], 'romeo@example.net')
        self.assertEqual(contacts[1]['jid'], 'juliet@example.net')
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0]['jid'], 'balcony@example.net')
        self.assertEqual(
            channels[0]['channel']['participant-id'],
            '123456'
        )

    def testClientJoin(self):
        """Test a client join"""

        fut = self.xmpp.wrap(self.xmpp['xep_0405'].join_channel(
            JID('coven@mix.shakespeare.example'),
            'toto',
        ))
        self.send("""
            <iq type='set' to='tester@localhost' id='1'>
              <client-join xmlns='urn:xmpp:mix:pam:2'
                           channel='coven@mix.shakespeare.example'>
                <join xmlns='urn:xmpp:mix:core:1'>
                  <nick>toto</nick>
                  <subscribe node='urn:xmpp:mix:nodes:messages'/>
                  <subscribe node='urn:xmpp:mix:nodes:participants'/>
                  <subscribe node='urn:xmpp:mix:nodes:info'/>
                </join>
              </client-join>
            </iq>
        """)
        self.recv("""
            <iq type='result'
                from='tester@localhost'
                to='tester@localhost/resource'
                id='1'>
                  <client-join xmlns='urn:xmpp:mix:pam:2'>
                    <join xmlns='urn:xmpp:mix:core:1'
                          jid='123456#coven@mix.shakespeare.example'>
                      <subscribe node='urn:xmpp:mix:nodes:messages'/>
                      <subscribe node='urn:xmpp:mix:nodes:participants'/>
                      <subscribe node='urn:xmpp:mix:nodes:info'/>
                   </join>
                 </client-join>
            </iq>
        """)
        self.wait_()
        self.assertEqual(fut.result(), set())

    def testClientJoinNotAllNodes(self):
        """Test a client join where one of the nodes is rejected"""

        fut = self.xmpp.wrap(self.xmpp['xep_0405'].join_channel(
            JID('coven@mix.shakespeare.example'),
            'toto',
        ))
        self.send("""
            <iq type='set' to='tester@localhost' id='1'>
              <client-join xmlns='urn:xmpp:mix:pam:2'
                           channel='coven@mix.shakespeare.example'>
                <join xmlns='urn:xmpp:mix:core:1'>
                  <nick>toto</nick>
                  <subscribe node='urn:xmpp:mix:nodes:messages'/>
                  <subscribe node='urn:xmpp:mix:nodes:participants'/>
                  <subscribe node='urn:xmpp:mix:nodes:info'/>
                </join>
              </client-join>
            </iq>
        """)
        self.recv("""
            <iq type='result'
                from='tester@localhost'
                to='tester@localhost/resource'
                id='1'>
                  <client-join xmlns='urn:xmpp:mix:pam:2'>
                    <join xmlns='urn:xmpp:mix:core:1'
                          jid='123456#coven@mix.shakespeare.example'>
                      <subscribe node='urn:xmpp:mix:nodes:messages'/>
                      <subscribe node='urn:xmpp:mix:nodes:participants'/>
                   </join>
                 </client-join>
            </iq>
        """)
        self.wait_()
        self.assertEqual(fut.result(), {'urn:xmpp:mix:nodes:info'})

    def testClientLeave(self):
        """Test a client leave"""

        fut = self.xmpp.wrap(self.xmpp['xep_0405'].leave_channel(
            JID('coven@mix.shakespeare.example'),
        ))
        self.send("""
            <iq type='set'
                to='tester@localhost'
                id='1'>
              <client-leave xmlns='urn:xmpp:mix:pam:2'
                            channel='coven@mix.shakespeare.example'>
                <leave xmlns='urn:xmpp:mix:core:1'/>
              </client-leave>
            </iq>
        """)
        self.recv("""
            <iq type='result'
                from='tester@localhost'
                to='tester@localhost/resource'
                id='1'>
              <client-leave xmlns='urn:xmpp:mix:pam:2'
                            channel='coven@mix.shakespeare.example'>
                <leave xmlns='urn:xmpp:mix:core:1'/>
              </client-leave>
            </iq>
        """)

        self.assertEqual(fut.done(), True)
        self.assertEqual(fut.exception(), None)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMIXPAM)
