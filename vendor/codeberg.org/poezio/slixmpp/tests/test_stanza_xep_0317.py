import unittest
from slixmpp import Presence
from slixmpp.test import SlixTest
import slixmpp.plugins.xep_0317 as xep_0317
from slixmpp.plugins.xep_0317 import stanza


class TestStanzaHats(SlixTest):

    def setUp(self):
        stanza.register_plugin()

    def test_create_hats(self):
        raw_xml = """
          <hats xmlns="urn:xmpp:hats:0">
            <hat uri="http://example.com/hats#Teacher" title="Teacher"/>
          </hats>
        """

        hats = xep_0317.Hats()

        hat = xep_0317.Hat()
        hat['uri'] = 'http://example.com/hats#Teacher'
        hat['title'] = 'Teacher'
        hats.append(hat)

        self.check(hats, raw_xml, use_values=False)

    def test_set_single_hat(self):
        presence = Presence()
        presence["hats"]["hat"]["uri"] = "test-uri"
        presence["hats"]["hat"]["title"] = "test-title"
        self.check(
            presence,  # language=XML
            """
            <presence>
              <hats xmlns='urn:xmpp:hats:0'>
                <hat uri='test-uri' title='test-title'/>
              </hats>
            </presence>
            """,
        )

    def test_set_multi_hat(self):
        presence = Presence()
        presence["hats"].add_hats([("uri1", "title1"), ("uri2", "title2")])
        self.check(
            presence,  # language=XML
            """
            <presence>
              <hats xmlns='urn:xmpp:hats:0'>
                <hat uri='uri1' title='title1'/>
                <hat uri='uri2' title='title2'/>
              </hats>
            </presence>
            """,
        )

    def test_get_hats(self):
        presence = Presence()
        presence["hats"].add_hats([("uri1", "title1"), ("uri2", "title2")])
        for i, hat in enumerate(presence["hats"]["hats"], start=1):
            self.assertEqual(hat["uri"], f"uri{i}")
            self.assertEqual(hat["title"], f"title{i}")


suite = unittest.TestLoader().loadTestsFromTestCase(TestStanzaHats)
