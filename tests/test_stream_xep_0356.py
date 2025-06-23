import unittest

from slixmpp import Message, JID, Iq
from slixmpp.plugins.xep_0356 import permissions
from slixmpp.plugins.xep_0356.permissions import RosterAccess
from slixmpp.test import SlixTest


class TestPermissions(SlixTest):
    def setUp(self):
        self.stream_start(
            mode="component",
            plugins=["xep_0356", "xep_0045"],
            jid="pubsub.capulet.lit",
            server="capulet.lit",
        )

    def testPluginEnd(self):
        exc = False
        try:
            self.xmpp.plugin.disable("xep_0356")
        except Exception as e:
            exc = True
        self.assertFalse(exc)

    def testGrantedPrivileges(self):
        results = {"event": False}
        x = self.xmpp["xep_0356"]
        self.xmpp.add_event_handler(
            "privileges_advertised", lambda msg: results.__setitem__("event", True)
        )
        self.recv(
            """
            <message from='capulet.lit' to='pubsub.capulet.lit' id='54321'>
                <privilege xmlns='urn:xmpp:privilege:2'>
                    <perm access='roster' type='both'/>
                    <perm access='message' type='outgoing'/>
                    <perm access='iq'>
                      <namespace ns='some_ns' type='get' />
                      <namespace ns='some_other_ns' type='both' />
                    </perm>
                </privilege>
            </message>
            """
        )
        server = JID("capulet.lit")
        self.assertEqual(
            x.granted_privileges[server].roster, permissions.RosterAccess.BOTH
        )
        self.assertEqual(
            x.granted_privileges[server].message, permissions.MessagePermission.OUTGOING
        )
        self.assertEqual(
            x.granted_privileges[server].presence, permissions.PresencePermission.NONE
        )
        self.assertEqual(
            x.granted_privileges[server].iq["nope"], permissions.IqPermission.NONE
        )
        self.assertEqual(
            x.granted_privileges[server].iq["some_ns"], permissions.IqPermission.GET
        )
        self.assertEqual(
            x.granted_privileges[server].iq["some_other_ns"], permissions.IqPermission.BOTH
        )
        self.assertTrue(results["event"])

    def testGetRosterIq(self):
        iq = self.xmpp["xep_0356"]._make_get_roster("juliet@example.com")
        xmlstring = """
        <iq xmlns="jabber:component:accept"
            id='1'
            from='pubsub.capulet.lit'
            to='juliet@example.com'
            type='get'>
                <query xmlns='jabber:iq:roster'/>
        </iq>
        """
        self.check(iq, xmlstring, use_values=False)

    def testSetRosterIq(self):
        jid = "juliet@example.com"
        items = {
            "friend1@example.com": {
                "name": "Friend 1",
                "subscription": "both",
                "groups": ["group1", "group2"],
            },
            "friend2@example.com": {
                "name": "Friend 2",
                "subscription": "from",
                "groups": ["group3"],
            },
        }
        iq = self.xmpp["xep_0356"]._make_set_roster(jid, items)
        xmlstring = f"""
        <iq xmlns="jabber:component:accept"
            id='1'
            from='pubsub.capulet.lit'
            to='{jid}'
            type='set'>
                <query xmlns='jabber:iq:roster'>
                    <item name='Friend 1' jid='friend1@example.com' subscription='both'>
                        <group>group1</group>
                        <group>group2</group>
                    </item>
                    <item name='Friend 2' jid='friend2@example.com' subscription='from'>
                        <group>group3</group>
                    </item>
                </query>
        </iq>
        """
        self.check(iq, xmlstring, use_values=False)

    def testMakeOutgoingMessage(self):
        xmlstring = """
        <message xmlns="jabber:component:accept" from='pubsub.capulet.lit' to='capulet.lit'>
            <privilege xmlns='urn:xmpp:privilege:2'>
                <forwarded xmlns='urn:xmpp:forward:0'>
                    <message from="juliet@capulet.lit" to="romeo@montague.lit" xmlns="jabber:client">
                        <body>I do not hate you</body>
                    </message>
                </forwarded>
            </privilege>
        </message>
        """
        msg = Message()
        msg["from"] = "juliet@capulet.lit"
        msg["to"] = "romeo@montague.lit"
        msg["body"] = "I do not hate you"

        priv_msg = self.xmpp["xep_0356"]._make_privileged_message(msg)
        self.check(priv_msg, xmlstring, use_values=False)

    def testDetectServer(self):
        msg = Message()
        msg["from"] = "juliet@something"
        msg["to"] = "romeo@montague.lit"
        msg["body"] = "I do not hate you"

        priv_msg = self.xmpp["xep_0356"]._make_privileged_message(msg)
        assert priv_msg.get_to() == "something"
        assert priv_msg.get_from() == "pubsub.capulet.lit"

    def testIqOnBehalf(self):
        iq = Iq()
        iq["mucadmin_query"]["item"]["affiliation"] = "member"
        iq.set_from("juliet@xxx")
        iq.set_to("somemuc@conf")
        iq.set_type("get")
        self.xmpp["xep_0356"].granted_privileges["conf"].iq["http://jabber.org/protocol/muc#admin"] = permissions.IqPermission.BOTH
        r = self.xmpp.loop.create_task(self.xmpp["xep_0356"].send_privileged_iq(iq, iq_id="0"))
        self.send(
            """
            <iq from="pubsub.capulet.lit"
                to="juliet@xxx"
                xmlns="jabber:component:accept"
                type="get" id="0">
                <privileged_iq xmlns='urn:xmpp:privilege:2'>
                    <iq xmlns='jabber:client'
                        type='get'
                        to='somemuc@conf'
                        from='juliet@xxx'
                         id="0">
                          <query xmlns='http://jabber.org/protocol/muc#admin'>
                            <item affiliation='member'/>
                          </query>
                    </iq>
                </privileged_iq>
            </iq>
            """,
            use_values=False
        )

    def testGetRosterWithInvalidJIDItem(self):
        roster_items = None

        def cb(task):
            nonlocal roster_items
            iq = task.result()
            roster_items = iq["roster"]["items"]

        self.xmpp.plugin["xep_0356"].granted_privileges[
            "toto.com"
        ].roster = RosterAccess.GET
        task = self.xmpp.loop.create_task(
            self.xmpp.plugin["xep_0356"].get_roster("toto@toto.com")
        )
        task.add_done_callback(cb)

        self.send(  # language=XML
            """
            <iq xmlns="jabber:component:accept"
                id="1"
                type="get"
                to="toto@toto.com"
                from="pubsub.capulet.lit">
              <query xmlns="jabber:iq:roster" />
            </iq>
            """
        )
        self.recv(  # language=XML
            """
            <iq id="1"
                to="pubsub.capulet.lit"
                from="toto@toto.com"
                type="result">
              <query xmlns="jabber:iq:roster">
                <item jid="xmpp:invalid"
                      name="User"
                      subscription="from"
                      ask="subscribe"></item>
                <item jid="valid@xmpp.love"
                      name="User"
                      subscription="from"
                      ask="subscribe"></item>
              </query>
            </iq>
            """
        )
        self.run_coro(task)
        assert roster_items == {
            "valid@xmpp.love": {
                "ask": "subscribe",
                "approved": "",
                "subscription": "from",
                "groups": [],
                "name": "User",
            }
        }


suite = unittest.TestLoader().loadTestsFromTestCase(TestPermissions)
