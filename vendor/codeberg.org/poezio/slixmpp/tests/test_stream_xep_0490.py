import unittest.mock

from slixmpp.test import SlixTest
# from slixmpp.plugins import xep_0490


class TestMessageDisplaySynchronization(SlixTest):
    def setUp(self):
        self.stream_start(jid="juliet@capulet.lit", plugins={"xep_0490"})

    def test_catch_up(self):
        future = self.xmpp.plugin["xep_0490"].catch_up()
        self.send(  # language=XML
            """
            <iq type="get" to="juliet@capulet.lit" id="1">
              <pubsub xmlns="http://jabber.org/protocol/pubsub">
                <items node="urn:xmpp:mds:displayed:0" />
              </pubsub>
            </iq>
            """
        )
        self.recv(  # language=XML
            """
            <iq type='result'
                to='juliet@capulet.lit/balcony'
                id='1'>
              <pubsub xmlns='http://jabber.org/protocol/pubsub'>
                <items node='urn:xmpp:mds:displayed:0'>
                  <item id='romeo@montegue.lit'>
                    <displayed xmlns='urn:xmpp:mds:displayed:0'>
                      <stanza-id xmlns='urn:xmpp:sid:0'
                                 id='0f710f2b-52ed-4d52-b928-784dad74a52b'
                                 by='juliet@capulet.lit'/>
                    </displayed>
                  </item>
                  <item id='example@conference.shakespeare.lit'>
                    <displayed xmlns='urn:xmpp:mds:displayed:0'>
                      <stanza-id xmlns='urn:xmpp:sid:0'
                                 id='ca21deaf-812c-48f1-8f16-339a674f2864'
                                 by='example@conference.shakespeare.lit'/>
                    </displayed>
                  </item>
                </items>
              </pubsub>
            </iq>
            """
        )
        iq = future.result()
        item = list(iq["pubsub"]["items"])
        self.assertEqual(item[0]["id"], "romeo@montegue.lit")
        self.assertEqual(
            item[0]["displayed"]["stanza_id"]["id"],
            "0f710f2b-52ed-4d52-b928-784dad74a52b",
        )

        self.assertEqual(item[1]["id"], "example@conference.shakespeare.lit")
        self.assertEqual(
            item[1]["displayed"]["stanza_id"]["id"],
            "ca21deaf-812c-48f1-8f16-339a674f2864",
        )

    def test_flag_chat(self):
        self.xmpp.plugin["xep_0490"].flag_chat(
            "romeo@montegue.lit", "0f710f2b-52ed-4d52-b928-784dad74a52b"
        )
        self.send(  # language=XML
            """
            <iq type='set' id='1'>
              <pubsub xmlns='http://jabber.org/protocol/pubsub'>
                <publish node='urn:xmpp:mds:displayed:0'>
                  <item id='romeo@montegue.lit'>
                    <displayed xmlns='urn:xmpp:mds:displayed:0'>
                      <stanza-id xmlns='urn:xmpp:sid:0' 
                                 id="0f710f2b-52ed-4d52-b928-784dad74a52b" />
                    </displayed>
                  </item>
                </publish>
                <publish-options>
                  <x xmlns='jabber:x:data' type='submit'>
                    <field var='FORM_TYPE' type='hidden'>
                      <value>http://jabber.org/protocol/pubsub#publish-options</value>
                    </field>
                    <field var='pubsub#persist_items'>
                      <value>1</value>
                    </field>
                    <field var='pubsub#max_items'>
                      <value>max</value>
                    </field>
                    <field var='pubsub#send_last_published_item'>
                      <value>never</value>
                    </field>
                    <field var='pubsub#access_model'>
                      <value>whitelist</value>
                    </field>
                  </x>
                </publish-options>
              </pubsub>
            </iq>
            """,
            use_values=False,
        )

    def test_notification(self):
        handler = unittest.mock.Mock()

        self.xmpp.add_event_handler(
            "message_displayed_synchronization_publish", handler
        )
        self.recv(  # language=XML
            """
            <message from='juliet@capulet.lit' to='juliet@capulet.lit/balcony' type='headline' id='new-displayed-pep-event'>
              <event xmlns='http://jabber.org/protocol/pubsub#event'>
                <items node='urn:xmpp:mds:displayed:0'>
                  <item id='romeo@montegue.lit'>
                    <displayed xmlns='urn:xmpp:mds:displayed:0'>
                      <stanza-id xmlns='urn:xmpp:sid:0' by='juliet@capulet.lit' id='0423e3a9-d516-493d-bb06-bee0e51ab9fb'/>
                    </displayed>
                  </item>
                </items>
              </event>
            </message>
            """
        )
        handler.assert_called()
        msg = handler.call_args[0][0]
        self.assertEqual(
            msg["pubsub_event"]["items"]["item"]["id"], "romeo@montegue.lit"
        )
        self.assertEqual(
            msg["pubsub_event"]["items"]["item"]["displayed"]["stanza_id"]["id"],
            "0423e3a9-d516-493d-bb06-bee0e51ab9fb",
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestMessageDisplaySynchronization)
