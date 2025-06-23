import logging
import unittest
from slixmpp.test import SlixTest


class TestCaps(SlixTest):
    def setUp(self):
        self.stream_start(plugins=["xep_0115"])

    def testConcurrentSameHash(self):
        """
        Check that we only resolve a given ver string to a disco info once,
        even if we receive several presences with that same ver string
        consecutively.
        """
        self.recv(  # language=XML
            """
            <presence from='romeo@montague.lit/orchard'>
              <c xmlns='http://jabber.org/protocol/caps'
                 hash='sha-1'
                 node='a-node'
                 ver='h0TdMvqNR8FHUfFG1HauOLYZDqE='/>
            </presence>
            """
        )
        self.recv(  # language=XML
            """
            <presence from='i-dont-know-much-shakespeare@montague.lit/orchard'>
              <c xmlns='http://jabber.org/protocol/caps'
                 hash='sha-1'
                 node='a-node'
                 ver='h0TdMvqNR8FHUfFG1HauOLYZDqE='/>
            </presence>
            """
        )
        self.send(  # language=XML
            """
            <iq xmlns="jabber:client"
                id="1"
                to="romeo@montague.lit/orchard"
                type="get">
              <query xmlns="http://jabber.org/protocol/disco#info"
                     node="a-node#h0TdMvqNR8FHUfFG1HauOLYZDqE="/>
            </iq>
            """
        )
        self.send(None)
        self.recv(  # language=XML
            """
            <iq from='romeo@montague.lit/orchard'
                id='1'
                type='result'>
              <query xmlns='http://jabber.org/protocol/disco#info'
                     node='a-nodes#h0TdMvqNR8FHUfFG1HauOLYZDqE='>
                <identity category='client' name='a client' type='pc'/>
                <feature var='http://jabber.org/protocol/caps'/>
              </query>
            </iq>
            """
        )
        self.send(None)
        self.assertTrue(
            self.xmpp["xep_0030"].supports(
                "romeo@montague.lit/orchard", "http://jabber.org/protocol/caps"
            )
        )
        self.assertTrue(
            self.xmpp["xep_0030"].supports(
                "i-dont-know-much-shakespeare@montague.lit/orchard",
                "http://jabber.org/protocol/caps",
            )
        )


logging.basicConfig(level=logging.DEBUG)
suite = unittest.TestLoader().loadTestsFromTestCase(TestCaps)
