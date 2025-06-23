import unittest

from slixmpp.test import SlixTest
from slixmpp.xmlstream import ElementBase
from slixmpp.plugins.xep_0402 import stanza


class Ext1(ElementBase):
    name = "ext1"
    namespace = "http://ext1"


class Ext2(ElementBase):
    name = "ext2"
    namespace = "http://ext2"


class TestPepBookmarks(SlixTest):
    def setUp(self):
        stanza.register_plugin()

    def test_bookmarks_extensions(self):
        extension1 = Ext1()
        extension2 = Ext2()

        bookmark = stanza.Conference()
        bookmark["password"] = "pass"
        bookmark["nick"] = "nick"
        bookmark["autojoin"] = False
        bookmark["extensions"].append(extension1)
        bookmark["extensions"].append(extension2)
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'
                        autojoin='false'>
              <nick>nick</nick>
              <password>pass</password>
              <extensions>
                <ext1 xmlns="http://ext1" />
                <ext2 xmlns="http://ext2" />
              </extensions>
            </conference>
            """,
            use_values=False
        )



suite = unittest.TestLoader().loadTestsFromTestCase(TestPepBookmarks)
