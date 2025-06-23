import unittest

from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0428 import stanza

from slixmpp.plugins import xep_0461
from slixmpp.plugins import xep_0444


class TestFallback(SlixTest):
    def setUp(self):
        stanza.register_plugins()

    def testSingleFallbackBody(self):
        message = Message()
        message["fallback"]["for"] = "ns"
        message["fallback"]["body"]["start"] = 0
        message["fallback"]["body"]["end"] = 8

        self.check(
            message,  # language=XML
            """
            <message>
              <fallback xmlns='urn:xmpp:fallback:0' for='ns'>
                <body start="0" end="8" />
              </fallback>
            </message>
            """,
        )

    def testSingleFallbackSubject(self):
        message = Message()
        message["fallback"]["for"] = "ns"
        message["fallback"]["subject"]["start"] = 0
        message["fallback"]["subject"]["end"] = 8

        self.check(
            message,  # language=XML
            """
            <message>
              <fallback xmlns='urn:xmpp:fallback:0' for='ns'>
                <subject start="0" end="8" />
              </fallback>
            </message>
            """,
        )

    def testSingleFallbackWholeBody(self):
        message = Message()
        message["fallback"]["for"] = "ns"
        message["fallback"].enable("body")
        self.check(
            message,  # language=XML
            """
            <message>
              <fallback xmlns='urn:xmpp:fallback:0' for='ns'>
                <body />
              </fallback>
            </message>
            """,
        )

    def testMultiFallback(self):
        message = Message()

        f1 = stanza.Fallback()
        f1["for"] = "ns1"

        f2 = stanza.Fallback()
        f2["for"] = "ns2"

        message.append(f1)
        message.append(f2)

        self.check(
            message,  # language=XML
            """
            <message>
              <fallback xmlns='urn:xmpp:fallback:0' for='ns1' />
              <fallback xmlns='urn:xmpp:fallback:0' for='ns2' />
            </message>
            """,
        )

        for i, fallback in enumerate(message["fallbacks"], start=1):
            self.assertEqual(fallback["for"], f"ns{i}")

    def testStripFallbackPartOfBody(self):
        message = Message()
        message["body"] = "> quoted\nsome-body"
        message["fallback"]["for"] = xep_0461.stanza.NS
        message["fallback"]["body"]["start"] = 0
        message["fallback"]["body"]["end"] = 9

        self.check(
            message,  # language=XML
            """
            <message>
              <body>&gt; quoted\nsome-body</body>
              <fallback xmlns='urn:xmpp:fallback:0' for='urn:xmpp:reply:0'>
                <body start="0" end="9" />
              </fallback>
            </message>
            """,
        )

        self.assertEqual(
            message["fallback"].get_stripped_body(xep_0461.stanza.NS), "some-body"
        )

    def testStripWholeBody(self):
        message = Message()
        message["body"] = "> quoted\nsome-body"
        message["fallback"]["for"] = "ns"
        message["fallback"].enable("body")

        self.check(
            message,  # language=XML
            """
            <message>
              <body>&gt; quoted\nsome-body</body>
              <fallback xmlns='urn:xmpp:fallback:0' for='ns'>
                <body />
              </fallback>
            </message>
            """,
        )

        self.assertEqual(message["fallback"].get_stripped_body("ns"), "")

    def testStripMultiFallback(self):
        message = Message()
        message["body"] = "> huuuuu\n👍"

        message["fallback"]["for"] = xep_0461.stanza.NS
        message["fallback"]["body"]["start"] = 0
        message["fallback"]["body"]["end"] = 9

        reaction_fallback = stanza.Fallback()
        reaction_fallback["for"] = xep_0444.stanza.NS
        reaction_fallback.enable("body")
        message.append(reaction_fallback)

        self.assertEqual(message["fallback"].get_stripped_body(xep_0461.stanza.NS), "👍")
        self.assertEqual(message["fallback"].get_stripped_body(xep_0444.stanza.NS), "")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFallback)
