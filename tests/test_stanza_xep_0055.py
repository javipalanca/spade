import unittest

from slixmpp import register_stanza_plugin, Iq
from slixmpp.test import SlixTest

from slixmpp.plugins.xep_0055 import stanza


class TestJabberSearch(SlixTest):
    def setUp(self):
        register_stanza_plugin(Iq, stanza.Search)
        self.stream_start(plugins={"xep_0055"})

    def testRequestSearchFields(self):
        iq = self.Iq()
        iq.set_from("juliet@capulet.com/balcony")
        iq.set_to("characters.shakespeare.lit")
        iq.set_type("get")
        iq.enable("search")
        iq["id"] = "0"
        self.check(
            iq,
            """
            <iq type='get'
                from='juliet@capulet.com/balcony'
                to='characters.shakespeare.lit'>
              <query xmlns='jabber:iq:search'/>
            </iq>
            """,
        )

    def testSendSearch(self):
        iq = self.xmpp["xep_0055"].make_search_iq(
            ifrom="juliet@capulet.com/balcony", ito="characters.shakespeare.lit"
        )
        iq["search"]["form"].add_field(var="x-gender", value="male")
        iq["id"] = "0"
        self.check(
            iq,
            """
            <iq type='set'
                from='juliet@capulet.com/balcony'
                to='characters.shakespeare.lit'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field type='hidden' var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <field var='x-gender'>
                    <value>male</value>
                  </field>
                </x>
              </query>
            </iq>
            """,
            use_values=False,
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestJabberSearch)
