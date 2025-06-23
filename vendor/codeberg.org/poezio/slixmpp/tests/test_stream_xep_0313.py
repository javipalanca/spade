import unittest
from datetime import datetime
from slixmpp.test import SlixTest
from slixmpp import JID


class TestMAM(SlixTest):

    def setUp(self):
        self.stream_start(plugins=['xep_0313'])

    def testRetrieveSimple(self):
        """Test requesting MAM messages without RSM"""

        msgs = []

        async def test():
            iq = await self.xmpp['xep_0313'].retrieve()
            for message in iq['mam']['results']:
                msgs.append(message)

        fut = self.xmpp.wrap(test())
        self.wait_()
        self.send("""
            <iq type='set' id='1'>
              <query xmlns='urn:xmpp:mam:2' queryid='1' />
            </iq>
        """)

        self.recv("""
            <message id='abc' to='tester@localhost/resource'>
              <result xmlns='urn:xmpp:mam:2' queryid='1'
                      id='28482-98726-73623'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                  <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:25Z'/>
                  <message xmlns='jabber:client' from="witch@shakespeare.lit"
                           to="tester@localhost">
                    <body>Hail to thee</body>
                  </message>
                </forwarded>
              </result>
            </message>
        """)

        self.recv("""
          <iq type="result" id="1" to="tester@localhost">
            <fin xmlns="urn:xmpp:mam:2">
              <first index='0'>28482-98726-73623</first>
              <last>28482-98726-73623</last>
            </fin>
          </iq>
        """)

        self.run_coro(fut)
        self.assertEqual(
            msgs[0]['mam_result']['forwarded']['message']['body'],
            "Hail to thee",
        )
        self.assertEqual(len(msgs),1)

    def testRetrieveRSM(self):
        """Test requesting MAM messages with RSM"""

        msgs = []

        async def test():
            iterator = self.xmpp['xep_0313'].retrieve(
                with_jid=JID('toto@titi'),
                start='2010-06-07T00:00:00Z',
                iterator=True,
            )
            async for page in iterator:
                for message in page['mam']['results']:
                    msgs.append(message)

        fut = self.xmpp.wrap(test())
        self.wait_()
        self.send("""
            <iq type='set' id='2'>
              <query xmlns='urn:xmpp:mam:2' queryid='2'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field var='FORM_TYPE' type='hidden'>
                    <value>urn:xmpp:mam:2</value>
                  </field>
                  <field var='with'>
                    <value>toto@titi</value>
                  </field>
                  <field var='start'>
                    <value>2010-06-07T00:00:00Z</value>
                  </field>
                </x>
                <set xmlns="http://jabber.org/protocol/rsm">
                  <max>10</max>
                </set>
              </query>
            </iq>
        """)

        self.recv("""
            <message id='abc' to='tester@localhost/resource'>
              <result xmlns='urn:xmpp:mam:2' queryid='2'
                      id='28482-98726-73623'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                  <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:25Z'/>
                  <message xmlns='jabber:client' from="witch@shakespeare.lit"
                           to="tester@localhost">
                    <body>Hail to thee</body>
                  </message>
                </forwarded>
              </result>
            </message>
        """)

        self.recv("""
          <iq type="result" id="2" to="tester@localhost">
            <fin xmlns="urn:xmpp:mam:2">
              <set xmlns='http://jabber.org/protocol/rsm'>
                <first index='0'>28482-98726-73623</first>
                 <last>28482-98726-73623</last>
                 <count>2</count>
              </set>
            </fin>
          </iq>
        """)

        self.send("""
            <iq type='set' id='3'>
              <query xmlns='urn:xmpp:mam:2' queryid='3'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field var='FORM_TYPE' type='hidden'>
                    <value>urn:xmpp:mam:2</value>
                  </field>
                  <field var='with'>
                    <value>toto@titi</value>
                  </field>
                  <field var='start'>
                    <value>2010-06-07T00:00:00Z</value>
                  </field>
                </x>
                <set xmlns="http://jabber.org/protocol/rsm">
                  <max>10</max>
                 <after>28482-98726-73623</after>
                </set>
              </query>
            </iq>
        """)

        self.recv("""
            <message id='abc' to='tester@localhost/resource'>
              <result xmlns='urn:xmpp:mam:2' queryid='3'
                      id='28482-98726-73624'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                  <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:26Z'/>
                  <message xmlns='jabber:client' from="witch@shakespeare.lit"
                           to="tester@localhost">
                    <body>Hi Y'all</body>
                  </message>
                </forwarded>
              </result>
            </message>
        """)

        self.recv("""
          <iq type="result" id="3" to="tester@localhost">
            <fin xmlns="urn:xmpp:mam:2">
              <set xmlns='http://jabber.org/protocol/rsm'>
                <first index='1'>28482-98726-73624</first>
                 <last>28482-98726-73624</last>
                 <count>2</count>
              </set>
            </fin>
          </iq>
        """)

        self.run_coro(fut)
        self.assertEqual(
            msgs[0]['mam_result']['forwarded']['message']['body'],
            "Hail to thee",
        )
        self.assertEqual(
            msgs[1]['mam_result']['forwarded']['message']['body'],
            "Hi Y'all",
        )
        self.assertEqual(len(msgs), 2)

    def testIterate(self):
        """Test iterating over MAM messages with RSM"""

        msgs = []

        async def test():
            iterator = self.xmpp['xep_0313'].iterate(
                with_jid=JID('toto@titi'),
                start='2010-06-07T00:00:00Z',
            )
            async for message in iterator:
                msgs.append(message)

        fut = self.xmpp.wrap(test())
        self.wait_()
        self.send("""
            <iq type='set' id='2'>
              <query xmlns='urn:xmpp:mam:2' queryid='2'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field var='FORM_TYPE' type='hidden'>
                    <value>urn:xmpp:mam:2</value>
                  </field>
                  <field var='with'>
                    <value>toto@titi</value>
                  </field>
                  <field var='start'>
                    <value>2010-06-07T00:00:00Z</value>
                  </field>
                </x>
                <set xmlns="http://jabber.org/protocol/rsm">
                  <max>10</max>
                </set>
              </query>
            </iq>
        """)

        self.recv("""
            <message id='abc' to='tester@localhost/resource'>
              <result xmlns='urn:xmpp:mam:2' queryid='2'
                             id='28482-98726-73623'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                  <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:25Z'/>
                  <message xmlns='jabber:client' from="witch@shakespeare.lit"
                           to="tester@localhost">
                    <body>Hail to thee</body>
                  </message>
                </forwarded>
              </result>
            </message>
        """)

        self.recv("""
          <iq type="result" id="2" to="tester@localhost">
            <fin xmlns="urn:xmpp:mam:2">
              <set xmlns='http://jabber.org/protocol/rsm'>
                <first index='0'>28482-98726-73623</first>
                 <last>28482-98726-73623</last>
                 <count>2</count>
              </set>
            </fin>
          </iq>
        """)

        self.send("""
            <iq type='set' id='3'>
              <query xmlns='urn:xmpp:mam:2' queryid='3'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field var='FORM_TYPE' type='hidden'>
                    <value>urn:xmpp:mam:2</value>
                  </field>
                  <field var='with'>
                    <value>toto@titi</value>
                  </field>
                  <field var='start'>
                    <value>2010-06-07T00:00:00Z</value>
                  </field>
                </x>
                <set xmlns="http://jabber.org/protocol/rsm">
                  <max>10</max>
                 <after>28482-98726-73623</after>
                </set>
              </query>
            </iq>
        """)

        self.recv("""
            <message id='abc' to='tester@localhost/resource'>
              <result xmlns='urn:xmpp:mam:2' queryid='3'
                      id='28482-98726-73624'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                  <delay xmlns='urn:xmpp:delay' stamp='2010-07-10T23:08:26Z'/>
                  <message xmlns='jabber:client' from="witch@shakespeare.lit"
                           to="tester@localhost">
                    <body>Hi Y'all</body>
                  </message>
                </forwarded>
              </result>
            </message>
        """)

        self.recv("""
          <iq type="result" id="3" to="tester@localhost">
            <fin xmlns="urn:xmpp:mam:2">
              <set xmlns='http://jabber.org/protocol/rsm'>
                <first index='1'>28482-98726-73624</first>
                 <last>28482-98726-73624</last>
                 <count>2</count>
              </set>
            </fin>
          </iq>
        """)

        self.run_coro(fut)
        self.assertEqual(
            msgs[0]['mam_result']['forwarded']['message']['body'],
            "Hail to thee",
        )
        self.assertEqual(
            msgs[1]['mam_result']['forwarded']['message']['body'],
            "Hi Y'all",
        )
        self.assertEqual(len(msgs), 2)

    def test_get_metadata(self):
        """Test a MAM metadata retrieval"""
        fut = self.xmpp.wrap(
            self.xmpp.plugin['xep_0313'].get_archive_metadata()
        )
        self.wait_()
        self.send("""
            <iq type='get' id='1'>
              <metadata xmlns='urn:xmpp:mam:2'/>
            </iq>
        """)
        self.recv("""
            <iq type='result' id='1'>
              <metadata xmlns='urn:xmpp:mam:2'>
                <start id='YWxwaGEg' timestamp='2008-08-22T21:09:04Z' />
                <end id='b21lZ2Eg' timestamp='2020-04-20T14:34:21Z' />
              </metadata>
            </iq>
        """)
        self.run_coro(fut)
        result = fut.result()
        self.assertEqual(result['mam_metadata']['start']['id'], "YWxwaGEg")
        self.assertEqual(
            result['mam_metadata']['start']['timestamp'],
            datetime.fromisoformat('2008-08-22T21:09:04+00:00')
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestMAM)
