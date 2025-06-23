import unittest
from slixmpp import Message
from slixmpp.jid import JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0482 import stanza
from slixmpp.plugins.xep_0482.stanza import External, Jingle
from slixmpp.xmlstream import register_stanza_plugin


class TestCallInviteStanza(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def test_invite(self):
        """Test that the element is created correctly."""
        msg = Message()
        msg['call-invite']['video'] = True
        jingle = Jingle()
        jingle['sid'] = 'toto'
        jingle['jid'] = JID('toto@example.com/m')
        external = External()
        external['uri'] = "https://example.com/call"
        msg['call-invite'].append(jingle)
        msg['call-invite'].append(external)

        self.check(msg, """
<message>
  <invite xmlns="urn:xmpp:call-invites:0" video="true">
    <jingle sid="toto" jid="toto@example.com/m" />
    <external uri="https://example.com/call" />
  </invite>
</message>
        """)

        self.assertEqual(
            msg['call-invite'].get_methods(),
            ([jingle], [external]),
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestCallInviteStanza)
