import unittest
from slixmpp.jid import JID
from slixmpp.test import SlixTest


class TestStreamCorrect(SlixTest):

    def test_recv_correct(self):
        self.stream_start(mode='client', plugins=['xep_0308'])

        recv = []

        def recv_correct(msg):
            recv.append(msg)

        self.xmpp.add_event_handler('message_correction', recv_correct)

        self.recv("""
            <message from="example.com" to="toto@example">
                <replace xmlns="urn:xmpp:message-correct:0" id="tototo"/>
                <body>oucou</body>
            </message>
        """)
        received = recv[0]
        self.assertEqual(received['replace']['id'], "tototo")


    def test_send_correct(self):
        self.stream_start(mode='client', plugins=['xep_0308'])

        corrected = self.xmpp.plugin['xep_0308'].build_correction(
            id_to_replace="12345",
            mto=JID('toto@example.com'),
            mbody="I am replacing",
        )
        self.assertEqual(corrected['replace']['id'], '12345')
        self.assertEqual(corrected['to'], JID('toto@example.com'))
        self.assertEqual(corrected['body'], 'I am replacing')
        corrected['id'] = 'my id'

        corrected = self.xmpp.plugin['xep_0308'].correct_message(
            corrected,
            'This is new',
        )
        self.send("""
            <message type="chat" to="toto@example.com">
                <body>This is new</body>
                <replace xmlns="urn:xmpp:message-correct:0" id="my id" />
            </message>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamCorrect)
