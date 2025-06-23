import unittest

from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0469 import stanza
from slixmpp.plugins.xep_0402 import stanza as b_stanza


class TestBookmarksPinning(SlixTest):
    def setUp(self):
        b_stanza.register_plugin()
        stanza.register_plugin()

    def test_pinned(self):
        bookmark = b_stanza.Conference()
        bookmark["password"] = "pass"
        bookmark["nick"] = "nick"
        bookmark["autojoin"] = False
        bookmark["extensions"].enable("pinned")
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'
                        autojoin='false'>
              <nick>nick</nick>
              <password>pass</password>
              <extensions>
                <pinned xmlns="urn:xmpp:bookmarks-pinning:0" />
              </extensions>
            </conference>
            """,
            use_values=False
        )



suite = unittest.TestLoader().loadTestsFromTestCase(TestBookmarksPinning)
