import unittest
from slixmpp.jid import JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0410 import PingStatus


class TestStreamSelfPing(SlixTest):

    def test_ping_workflow(self):
        """
        Try the autoping provided by the plugin, as well as the events
        generated
        """
        self.stream_start(mode='client', plugins=['xep_0410'])
        self.xmpp.plugin['xep_0410'].ping_interval = 0.1

        recv = []
        def recv_ping(args):
            recv.append(args)

        self.xmpp.add_event_handler('muc_ping_changed', recv_ping)

        self.xmpp.plugin['xep_0410'].enable_self_ping(
            JID('muc@muc.example.com/toto'),
            JID('toto@example.com/test'),
        )
        self.wait_(0.2)
        self.send("""
<iq from="toto@example.com/test" to="muc@muc.example.com/toto" type="get" id="1">
    <ping xmlns='urn:xmpp:ping'/>
</iq>
        """)
        self.recv("""
<iq to="toto@example.com/test" from="muc@muc.example.com/toto" type="result" id="1"/>
        """)
        self.wait_()

        self.assertEqual(
            recv[-1]['result'],
            PingStatus.JOINED,
        )
        self.assertEqual(
            self.xmpp.plugin['xep_0410'].get_ping_status(
                JID('muc@muc.example.com/toto'),
                JID('toto@example.com/test'),
            ),
            PingStatus.JOINED,
        )
        self.wait_(0.2)
        self.send("""
<iq from="toto@example.com/test" to="muc@muc.example.com/toto" type="get" id="2">
    <ping xmlns='urn:xmpp:ping'/>
</iq>
        """)
        self.recv("""
<iq to="toto@example.com/test" from="muc@muc.example.com/toto" type="error" id="2">
  <error type="cancel" by="muc.example.com">
    <not-acceptable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
  </error>
</iq>
        """)
        self.wait_()
        self.assertEqual(
            recv[-1]['result'],
            PingStatus.DISCONNECTED,
        )
        self.assertEqual(
            self.xmpp.plugin['xep_0410'].get_ping_status(
                JID('muc@muc.example.com/toto'),
                JID('toto@example.com/test'),
            ),
            PingStatus.DISCONNECTED,
        )
        self.xmpp.plugin['xep_0410'].disable_self_ping(
            JID('muc@muc.example.com/toto'),
            JID('toto@example.com/test'),
        )
        self.wait_()



suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamSelfPing)
