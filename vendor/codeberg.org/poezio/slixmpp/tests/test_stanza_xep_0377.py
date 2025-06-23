import unittest
from slixmpp import Iq
from slixmpp.test import SlixTest
import slixmpp.plugins.xep_0191 as xep_0191
import slixmpp.plugins.xep_0377 as xep_0377
from slixmpp.xmlstream import register_stanza_plugin


class TestSpamReporting(SlixTest):

    def setUp(self):
        register_stanza_plugin(Iq, xep_0191.Block)
        register_stanza_plugin(
                xep_0191.Block,
                xep_0377.Report,
        )
        register_stanza_plugin(
            xep_0377.Report,
            xep_0377.Text,
        )

    def testCreateReport(self):
        report = """
          <iq type="set">
            <block xmlns="urn:xmpp:blocking">
                <report xmlns="urn:xmpp:reporting:1" reason="urn:xmpp:reporting:spam"/>
            </block>
          </iq>
        """

        iq = self.Iq()
        iq['type'] = 'set'
        iq['block']['report']['reason'] = xep_0377.XEP_0377.SPAM

        self.check(iq, report, use_values=False)

    def testEnforceOnlyOneSubElement(self):
        report = """
          <iq type="set">
            <block xmlns="urn:xmpp:blocking">
                <report xmlns="urn:xmpp:reporting:1" reason="urn:xmpp:reporting:abuse"/>
            </block>
          </iq>
        """

        iq = self.Iq()
        iq['type'] = 'set'
        iq['block']['report']['reason'] = xep_0377.XEP_0377.SPAM
        iq['block']['report']['reason'] = xep_0377.XEP_0377.ABUSE
        self.check(iq, report, use_values=False)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSpamReporting)
