# -*- coding: utf-8 -*-
import unittest

import spade
import xmpp


class JsonTestCase(unittest.TestCase):

    def testDumpACLMessage(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@myhost.com", ["xmpp://b@myhost.com", "http://myhost.com:8080"]))
        msg.setContent("testDumpACLMessage")
        cid = msg.getConversationId()

        assert msg.asJSON() == '{"performative":"inform","receivers":[{"name": "b@myhost.com", "addresses": ["xmpp://b@myhost.com", "http://myhost.com:8080"]}],"content":"testDumpACLMessage","conversation-id":"' + cid + '"}'

    def testSanityCheckACLMessage(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("b@myhost.com", ["xmpp://b@myhost.com", "http://myhost.com:8080"]))
        msg.setContent("Sanity Check")
        cid = msg.getConversationId()

        jsonmsg = msg.asJSON()

        msg2 = spade.ACLMessage.ACLMessage()
        msg2.loadJSON(jsonmsg)

        assert msg.asString() == msg2.asString()

    def testDumpACLEnvelope(self):
        env = spade.Envelope.Envelope()
        env.addTo(spade.AID.aid("b@myhost.com", ["xmpp://b@myhost.com", "http://myhost.com:8080"]))
        env.setFrom(spade.AID.aid("a@myotherhost.com", ["xmpp://a@myotherhost.com", "http://myotherhost.com:8080"]))
        env.setAclRepresentation("fipa.acl.rep.string.std")
        env.setPayloadLength("100")
        env.setPayloadEncoding("US-ASCII")
        env.setDate("20121105T134259368626")

        envjson = '{"to":[{"name":"b@myhost.com","addresses":["xmpp://b@myhost.com","http://myhost.com:8080"]}],"from":{"name":"a@myotherhost.com","addresses":["xmpp://a@myotherhost.com","http://myotherhost.com:8080"]},"acl-representation":"fipa.acl.rep.string.std","payload-length":"100","payload-encoding":"US-ASCII","date":"20121105T134259368626","intended-receiver":[{"name":"b@myhost.com","addresses":["xmpp://b@myhost.com","http://myhost.com:8080"]}]}'

        assert env.asJSON() == envjson

    def testSanityCheckACLEnvelope(self):
        env = spade.Envelope.Envelope()
        env.addTo(spade.AID.aid("b@myhost.com", ["xmpp://b@myhost.com", "http://myhost.com:8080"]))
        env.setFrom(spade.AID.aid("a@myotherhost.com", ["xmpp://a@myotherhost.com", "http://myotherhost.com:8080"]))
        env.setAclRepresentation("fipa.acl.rep.string.std")
        env.setPayloadLength("100")
        env.setPayloadEncoding("US-ASCII")
        env.setDate("20121105T134259368626")

        jsonmsg = env.asJSON()

        env2 = spade.Envelope.Envelope()
        env2.loadJSON(jsonmsg)

        assert isEqualXML(env.asXML(), env2.asXML())


def isEqualXML(a, b):
    da, db = xmpp.simplexml.NodeBuilder(a), xmpp.simplexml.NodeBuilder(b)
    return isEqualElement(da.getDom(), db.getDom())


def isEqualElement(a, b):
    if a.getName() != b.getName():
        return False
    if sorted(a.getAttrs().items()) != sorted(b.getAttrs().items()):
        return False
    if len(a.getChildren()) != len(b.getChildren()):
        return False
    if a.getData() and b.getData() and a.getData() != b.getData():
        return False
    for ac in a.getChildren():
        l = []
        for bc in b.getChildren():
            if ac.getName() == bc.getName():
                l.append(bc)
        if len(l) == 0:
            return False
        r = False
        for n in l:
            if len(ac.kids) == len(n.kids):
                r = True
        if not r:
            return False

        if ac.getData():
            for n in l:
                if n.getData() == ac.getData():
                    r = True
            if not r:
                return False

        if not ac.getData() and (len(ac.kids) > 0):
            for n in l:
                if isEqualElement(ac, n):
                    r = True
            if not r:
                return False

    return True

if __name__ == "__main__":
    unittest.main()
