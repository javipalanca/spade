import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0428 import stanza as fallback_stanza
from slixmpp.plugins.xep_0461 import stanza


class TestReply(SlixTest):
    def setUp(self):
        fallback_stanza.register_plugins()
        stanza.register_plugins()

    def testReply(self):
        message = Message()
        message["reply"]["id"] = "some-id"
        message["body"] = "some-body"

        self.check(
            message,
            """
            <message>
              <reply xmlns="urn:xmpp:reply:0" id="some-id" />
              <body>some-body</body>
            </message>
            """,
        )

    def testFallback(self):
        message = Message()
        message["body"] = "12345\nrealbody"
        message["fallback"]["for"] = "NS"
        message["fallback"]["body"]["start"] = 0
        message["fallback"]["body"]["end"] = 6

        self.check(
            message,
            """
            <message xmlns="jabber:client">
              <body>12345\nrealbody</body>
              <fallback xmlns='urn:xmpp:fallback:0' for='NS'>
                <body start="0" end="6" />
              </fallback>
            </message>
            """,
        )

        assert message["fallback"].get_stripped_body("NS") == "realbody"

    def testAddFallBackHelper(self):
        msg = Message()
        msg["body"] = "Great"
        msg["reply"].add_quoted_fallback("Anna wrote:\nHi, how are you?")
        self.check(
            msg,  # language=XML
            """
        <message xmlns="jabber:client" type="normal">
            <body>> Anna wrote:\n> Hi, how are you?\nGreat</body>
            <reply xmlns="urn:xmpp:reply:0" />
            <fallback xmlns="urn:xmpp:fallback:0" for="urn:xmpp:reply:0">
                <body start='0' end='33' />
            </fallback>
        </message>
            """
        )

    def testGetFallBackBody(self):
        body = "Anna wrote:\nHi, how are you?"
        quoted = "> Anna wrote:\n> Hi, how are you?\n"

        msg = Message()
        msg["body"] = "Great"
        msg["reply"].add_quoted_fallback(body)
        body2 = msg["reply"].get_fallback_body()
        self.assertTrue(body2 == quoted, body2)


suite = unittest.TestLoader().loadTestsFromTestCase(TestReply)
