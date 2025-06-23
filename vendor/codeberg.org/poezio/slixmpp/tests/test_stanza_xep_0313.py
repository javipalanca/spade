import unittest
from slixmpp import JID, Iq, Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0313 import stanza
from slixmpp.plugins.xep_0004.stanza import Form
from slixmpp.plugins.xep_0297 import stanza as fstanza
from slixmpp.plugins.xep_0059 import stanza as rstanza
from slixmpp.xmlstream import register_stanza_plugin


class TestMAM(SlixTest):

    def setUp(self):
        register_stanza_plugin(stanza.MAM, Form)
        register_stanza_plugin(Iq, stanza.MAM)
        register_stanza_plugin(Message, stanza.Result)
        register_stanza_plugin(Iq, stanza.Fin)
        register_stanza_plugin(
            stanza.Result,
            fstanza.Forwarded
        )
        register_stanza_plugin(stanza.MAM, rstanza.Set)
        register_stanza_plugin(stanza.Fin, rstanza.Set)

        register_stanza_plugin(Iq, stanza.Metadata)
        register_stanza_plugin(stanza.Metadata, stanza.Start)
        register_stanza_plugin(stanza.Metadata, stanza.End)

    def testMAMQuery(self):
        """Test that we can build a simple MAM query."""
        iq = Iq()
        iq['type'] = 'set'
        iq['mam']['queryid'] = 'f27'

        self.check(iq, """
            <iq type='set'>
              <query xmlns='urn:xmpp:mam:2' queryid='f27'/>
            </iq>
        """)

    def testMAMQueryOptions(self):
        """Test that we can build a mam query with all options."""
        iq = Iq()
        iq['type'] = 'set'
        iq['mam']['with'] = JID('juliet@capulet.lit')
        iq['mam']['start'] = '2010-06-07T00:00:00Z'
        iq['mam']['end'] = '2010-07-07T13:23:54Z'
        iq['mam']['after_id'] = 'id1'
        iq['mam']['before_id'] = 'id2'
        iq['mam']['ids'] = ['a', 'b', 'c']

        self.check(iq, """
            <iq type='set'>
              <query xmlns='urn:xmpp:mam:2'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field var='FORM_TYPE' type='hidden'>
                    <value>urn:xmpp:mam:2</value>
                  </field>
                  <field var='with'>
                    <value>juliet@capulet.lit</value>
                  </field>
                  <field var='start'>
                    <value>2010-06-07T00:00:00Z</value>
                  </field>
                  <field var='end'>
                    <value>2010-07-07T13:23:54Z</value>
                  </field>
                  <field var='after-id'>
                    <value>id1</value>
                  </field>
                  <field var='before-id'>
                    <value>id2</value>
                  </field>
                  <field var='ids'>
                    <value>a</value>
                    <value>b</value>
                    <value>c</value>
                  </field>
                </x>
              </query>
            </iq>
        """, use_values=False)

    def testMAMMetadata(self):
        """Test that we can build a MAM metadata payload"""

        iq = Iq()
        iq['type'] = 'result'
        iq['mam_metadata']['start']['id'] = 'YWxwaGEg'
        iq['mam_metadata']['start']['timestamp'] = '2008-08-22T21:09:04Z'
        iq['mam_metadata']['end']['id'] = 'b21lZ2Eg'
        iq['mam_metadata']['end']['timestamp'] = '2020-04-20T14:34:21Z'

        self.check(iq, """
            <iq type='result'>
              <metadata xmlns='urn:xmpp:mam:2'>
                <start id='YWxwaGEg' timestamp='2008-08-22T21:09:04Z' />
                <end id='b21lZ2Eg' timestamp='2020-04-20T14:34:21Z' />
              </metadata>
            </iq>
        """)



suite = unittest.TestLoader().loadTestsFromTestCase(TestMAM)
