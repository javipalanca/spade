import unittest
from slixmpp.test import SlixTest
from slixmpp.xmlstream.stanzabase import ET, StanzaBase


class TestStanzaBase(SlixTest):

    def testTo(self):
        """Test the 'to' interface of StanzaBase."""
        stanza = StanzaBase()
        stanza['to'] = 'user@example.com'
        self.assertTrue(str(stanza['to']) == 'user@example.com',
            "Setting and retrieving stanza 'to' attribute did not work.")

    def testFrom(self):
        """Test the 'from' interface of StanzaBase."""
        stanza = StanzaBase()
        stanza['from'] = 'user@example.com'
        self.assertTrue(str(stanza['from']) == 'user@example.com',
            "Setting and retrieving stanza 'from' attribute did not work.")

    def testPayload(self):
        """Test the 'payload' interface of StanzaBase."""
        stanza = StanzaBase()
        self.assertTrue(stanza['payload'] == [],
            "Empty stanza does not have an empty payload.")

        stanza['payload'] = ET.Element("{foo}foo")
        self.assertTrue(len(stanza['payload']) == 1,
            "Stanza contents and payload do not match.")

        stanza['payload'] = ET.Element('{bar}bar')
        self.assertTrue(len(stanza['payload']) == 2,
            "Stanza payload was not appended.")

        del stanza['payload']
        self.assertTrue(stanza['payload'] == [],
            "Stanza payload not cleared after deletion.")

        stanza['payload'] = [ET.Element('{foo}foo'),
                             ET.Element('{bar}bar')]
        self.assertTrue(len(stanza['payload']) == 2,
            "Adding multiple elements to stanza's payload did not work.")

    def testClear(self):
        """Test clearing a stanza."""
        stanza = StanzaBase()
        stanza['to'] = 'user@example.com'
        stanza['payload'] = ET.Element("{foo}foo")
        stanza.clear()

        self.assertTrue(stanza['payload'] == [],
            "Stanza payload was not cleared after calling .clear()")
        self.assertTrue(str(stanza['to']) == "user@example.com",
            "Stanza attributes were not preserved after calling .clear()")

    def testReply(self):
        """Test creating a reply stanza."""
        stanza = StanzaBase()
        stanza['to'] = "recipient@example.com"
        stanza['from'] = "sender@example.com"
        stanza['payload'] = ET.Element("{foo}foo")

        stanza = stanza.reply()

        self.assertTrue(str(stanza['to'] == "sender@example.com"),
            "Stanza reply did not change 'to' attribute.")
        self.assertTrue(stanza['payload'] == [],
            "Stanza reply did not empty stanza payload.")


suite = unittest.TestLoader().loadTestsFromTestCase(TestStanzaBase)
