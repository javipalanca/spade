import unittest
from slixmpp.test import SlixTest


class TestPrivatePEP(SlixTest):

    def testConfigureNode(self):
        self.stream_start(mode='client', plugins=['xep_0223'])

        self.xmpp.plugin['xep_0223'].configure(node="toto")
        self.send("""
<iq type="set" id="1">
  <pubsub xmlns='http://jabber.org/protocol/pubsub#owner'>
    <configure node='toto'>
      <x xmlns='jabber:x:data' type='submit'>
        <field var='FORM_TYPE' type='hidden'>
          <value>http://jabber.org/protocol/pubsub#node_config</value>
        </field>
        <field var='pubsub#persist_items'><value>1</value></field>
        <field var='pubsub#access_model'><value>whitelist</value></field>
      </x>
    </configure>
  </pubsub>
</iq>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestPrivatePEP)
