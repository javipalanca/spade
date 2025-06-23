import unittest
from slixmpp.test import SlixTest

from slixmpp.plugins.xep_0356 import stanza, permissions


class TestPermissions(SlixTest):
    def setUp(self):
        stanza.register()

    def testAdvertisePermission(self):
        xmlstring = """
            <message from='capulet.lit' to='pubsub.capulet.lit'>
                <privilege xmlns='urn:xmpp:privilege:2'>
                    <perm access='roster' type='both'/>
                    <perm access='message' type='outgoing'/>
                    <perm access='presence' type='managed_entity'/>
                    <perm access='iq' type='both'/>
                </privilege>
            </message>
        """
        msg = self.Message()
        msg["from"] = "capulet.lit"
        msg["to"] = "pubsub.capulet.lit"

        for access, type_ in [
            ("roster", permissions.RosterAccess.BOTH),
            ("message", permissions.MessagePermission.OUTGOING),
            ("presence", permissions.PresencePermission.MANAGED_ENTITY),
            ("iq", permissions.IqPermission.BOTH),
        ]:
            msg["privilege"].add_perm(access, type_)

        self.check(msg, xmlstring)

    def testIqPermission(self):
        x = stanza.Privilege()
        x["access"] = "iq"
        ns = stanza.NameSpace()
        ns["ns"] = "some_ns"
        ns["type"] = "get"
        x["perm"]["access"] = "iq"
        x["perm"].append(ns)
        ns = stanza.NameSpace()
        ns["ns"] = "some_other_ns"
        ns["type"] = "both"
        x["perm"].append(ns)
        self.check(
            x,
            """
              <privilege xmlns='urn:xmpp:privilege:2'>
                <perm access='iq'>
                  <namespace ns='some_ns' type='get' />
                  <namespace ns='some_other_ns' type='both' />
                </perm>
              </privilege>
            """
        )
        nss = set()
        for perm in x["perms"]:
            for ns in perm["namespaces"]:
                nss.add((ns["ns"], ns["type"]))
        assert nss == {("some_ns", "get"), ("some_other_ns", "both")}


suite = unittest.TestLoader().loadTestsFromTestCase(TestPermissions)
