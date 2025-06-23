import unittest
from slixmpp.test import SlixTest


class TestJabberSearch(SlixTest):
    def setUp(self):
        self.stream_start(
            mode="component",
            plugin_config={
                "xep_0055": {
                    "form_fields": {"first", "last"},
                    "form_instructions": "INSTRUCTIONS",
                    "form_title": "User Directory Search",
                }
            },
            jid="characters.shakespeare.lit",
            plugins={"xep_0055"}
        )
        self.xmpp["xep_0055"].api.register(get_results, "search_query")
        self.xmpp["xep_0055"].api.register(get_results, "search_query")

    def testRequestingSearchFields(self):
        self.recv(
            """
            <iq type='get'
                from='juliet@capulet.com/balcony'
                to='characters.shakespeare.lit'
                id='search3'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'/>
            </iq>
            """
        )
        self.send(
            """
            <iq type='result'
                from='characters.shakespeare.lit'
                to='juliet@capulet.com/balcony'
                id='search3'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='form'>
                  <title>User Directory Search</title>
                  <instructions>INSTRUCTIONS</instructions>
                  <field type='hidden'
                         var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <field var='first'/>
                  <field var='last'/>
                </x>
              </query>
            </iq>
            """,
            use_values=False,
        )

    def testSearchResult(self):
        self.recv(
            """
            <iq type='get'
                from='juliet@capulet.com/balcony'
                to='characters.shakespeare.lit'
                id='search2'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field type='hidden' var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <field var='last'>
                    <value>Montague</value>
                  </field>
                </x>
              </query>
            </iq>
            """
        )
        self.send(
            """
            <iq type='result'
                from='characters.shakespeare.lit'
                to='juliet@capulet.com/balcony'
                id='search2'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='result'>
                  <field type='hidden' var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <reported>
                    <field var='first' label='Given Name' />
                    <field var='last' label='Family Name' />
                  </reported>
                  <item>
                    <field var='first'><value>Benvolio</value></field>
                    <field var='last'><value>Montague</value></field>
                  </item>
                </x>
              </query>
            </iq>
            """,
            use_values=False,  # TypeError: element indices must be integers without that
        )

    def testSearchNoResult(self):
        self.xmpp["xep_0055"].api.register(get_results, "search_query")
        self.recv(
            """
            <iq type='get'
                from='juliet@capulet.com/balcony'
                to='characters.shakespeare.lit'
                id='search2'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='submit'>
                  <field type='hidden' var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <field var='last'>
                    <value>Capulet</value>
                  </field>
                </x>
              </query>
            </iq>
            """
        )
        self.send(
            """
            <iq type='result'
                from='characters.shakespeare.lit'
                to='juliet@capulet.com/balcony'
                id='search2'
                xml:lang='en'>
              <query xmlns='jabber:iq:search'>
                <x xmlns='jabber:x:data' type='result'>
                  <field type='hidden' var='FORM_TYPE'>
                    <value>jabber:iq:search</value>
                  </field>
                  <reported>
                    <field var='first' label='Given Name' />
                    <field var='last' label='Family Name' />
                  </reported>
                </x>
              </query>
            </iq>
            """,
            use_values=False,  # TypeError: element indices must be integers without that
        )

async def get_results(jid, node, ifrom, iq):
    reply = iq.reply()
    form = reply["search"]["form"]
    form["type"] = "result"

    form.add_reported("first", label="Given Name")
    form.add_reported("last", label="Family Name")

    d = iq["search"]["form"].get_values()

    if d["last"] == "Montague":
        form.add_item({"first": "Benvolio", "last": "Montague"})

    return reply


suite = unittest.TestLoader().loadTestsFromTestCase(TestJabberSearch)
