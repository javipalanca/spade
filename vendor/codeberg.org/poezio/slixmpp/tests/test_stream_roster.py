# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import unittest
from slixmpp.exceptions import IqTimeout
from slixmpp.test import SlixTest
import time
import threading


class TestStreamRoster(SlixTest):
    """
    Test handling roster updates.
    """

    def testGetRoster(self):
        """Test handling roster requests."""
        self.stream_start(mode='client', jid='tester@localhost')

        roster_updates = []

        self.xmpp.add_event_handler('roster_update', roster_updates.append)

        self.xmpp.get_roster()

        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)
        self.recv("""
          <iq to='tester@localhost' type="result" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    name="User"
                    subscription="from"
                    ask="subscribe">
                <group>Friends</group>
                <group>Examples</group>
              </item>
            </query>
          </iq>
        """)

        self.check_roster('tester@localhost', 'user@localhost',
                          name='User',
                          subscription='from',
                          afrom=True,
                          pending_out=True,
                          groups=['Friends', 'Examples'])

        self.assertTrue(len(roster_updates) == 1,
                "Wrong number of roster_update events fired: %s (should be 1)" % len(roster_updates))

    def testRosterSet(self):
        """Test handling pushed roster updates."""
        self.stream_start(mode='client')
        events = []

        def roster_update(e):
            events.append('roster_update')

        self.xmpp.add_event_handler('roster_update', roster_update)

        self.recv("""
          <iq to='tester@localhost' type="set" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    name="User"
                    subscription="both">
                <group>Friends</group>
                <group>Examples</group>
              </item>
            </query>
          </iq>
        """)
        self.send("""
          <iq type="result" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)

        self.check_roster('tester@localhost', 'user@localhost',
                          name='User',
                          subscription='both',
                          groups=['Friends', 'Examples'])


        self.assertTrue('roster_update' in events,
                "Roster updated event not triggered: %s" % events)

    def testRosterPushRemove(self):
        """Test handling roster item removal updates."""
        self.stream_start(mode='client')
        events = []

        # Add roster item
        self.recv("""
          <iq to='tester@localhost' type="set" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    name="User"
                    subscription="both">
                <group>Friends</group>
                <group>Examples</group>
              </item>
            </query>
          </iq>
        """)
        self.send("""
          <iq type="result" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)

        self.assertTrue('user@localhost' in self.xmpp.client_roster)

        # Receive item remove push
        self.recv("""
          <iq to='tester@localhost' type="set" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    subscription="remove">
              </item>
            </query>
          </iq>
        """)
        self.send("""
          <iq type="result" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)

        self.assertTrue('user@localhost' not in self.xmpp.client_roster)

    def testUnauthorizedRosterPush(self):
        """Test rejecting a roster push from an unauthorized source."""
        self.stream_start()
        self.recv("""
          <iq to='tester@localhost' from="malicious_user@localhost"
              type="set" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    name="User"
                    subscription="both">
                <group>Friends</group>
                <group>Examples</group>
              </item>
            </query>
          </iq>
        """)
        self.send("""
          <iq to="malicious_user@localhost" type="error" id="1">
            <error type="cancel" code="503">
              <service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
            </error>
          </iq>
        """)

    def testRosterCallback(self):
        """Test handling a roster request callback."""
        self.stream_start()
        events = []

        def roster_callback(iq):
            events.append('roster_callback')

        self.xmpp.get_roster(callback=roster_callback)

        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)
        self.recv("""
          <iq type="result" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="user@localhost"
                    name="User"
                    subscription="both">
                <group>Friends</group>
                <group>Examples</group>
              </item>
            </query>
          </iq>
        """)

        self.assertTrue(events == ['roster_callback'],
                 "Roster timeout event not triggered: %s." % events)

    def testRosterUnicode(self):
        """Test that JIDs with Unicode values are handled properly."""
        self.stream_start(plugins=[])
        self.recv("""
          <iq to="tester@localhost" type="set" id="1">
            <query xmlns="jabber:iq:roster">
              <item jid="andré@foo" subscription="both">
                <group>Unicode</group>
              </item>
            </query>
          </iq>
        """)

        self.check_roster('tester@localhost', 'andré@foo',
                          subscription='both',
                          groups=['Unicode'])

        jids = list(self.xmpp.client_roster.keys())
        self.assertTrue(jids == ['andré@foo'],
                 "Too many roster entries found: %s" % jids)

        self.recv("""
          <presence to="tester@localhost" from="andré@foo/bar">
            <show>away</show>
            <status>Testing</status>
          </presence>
        """)

        result = self.xmpp.client_roster['andré@foo'].resources
        expected = {'bar': {'status':'Testing',
                            'show':'away',
                            'priority':0}}
        self.assertTrue(result == expected,
                "Unexpected roster values: %s" % result)

    def testSendLastPresence(self):
        """Test that sending the last presence works."""
        self.stream_start(plugins=[])
        self.xmpp.send_presence(pshow='dnd')
        self.xmpp.auto_authorize = True
        self.xmpp.auto_subscribe = True

        self.send("""
          <presence>
            <show>dnd</show>
          </presence>
        """)

        self.recv("""
          <presence from="user@localhost"
                    to="tester@localhost"
                    type="subscribe" />
        """)

        self.send("""
          <presence to="user@localhost"
                    type="subscribed" />
        """)

        self.send("""
          <presence to="user@localhost">
            <show>dnd</show>
          </presence>
        """)

    def testUnsupportedRosterVer(self):
        """Test working with a server without roster versioning."""
        self.stream_start()
        self.assertTrue('rosterver' not in self.xmpp.features)

        self.xmpp.get_roster()

        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster" />
          </iq>
        """)
        self.recv("""
          <iq to="tester@localhost" type="result" id="1" />
        """)

    def testBootstrapRosterVer(self):
        """Test bootstrapping with roster versioning."""
        self.stream_start()
        self.xmpp.features.add('rosterver')
        self.xmpp.client_roster.version = ''

        self.xmpp.get_roster()

        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster" ver="" />
          </iq>
        """)
        self.recv("""
          <iq to="tester@localhost" type="result" id="1" />
        """)


    def testExistingRosterVer(self):
        """Test using a stored roster version."""
        self.stream_start()
        self.xmpp.features.add('rosterver')
        self.xmpp.client_roster.version = '42'

        self.xmpp.get_roster()

        self.send("""
          <iq type="get" id="1">
            <query xmlns="jabber:iq:roster" ver="42" />
          </iq>
        """)
        self.recv("""
          <iq to="tester@localhost" type="result" id="1" />
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamRoster)
