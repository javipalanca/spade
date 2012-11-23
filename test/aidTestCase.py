# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade
import xmpp

import xml.dom.minidom


class AidTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCreateAid(self):
        aid = spade.AID.aid()

        self.assertEqual(aid.getName(), None)
        self.assertEqual(aid.getAddresses(), [])
        self.assertEqual(aid.getResolvers(), [])
        self.assertEqual(aid.getProperties(), [])

        aid.setName("aidname")
        self.assertEqual(aid.getName(), "aidname")
        aid.addAddress("address@server.com")
        self.assertEqual(len(aid.getAddresses()), 1)
        self.assertEqual(aid.getAddresses()[0], "address@server.com")
        aid.addResolvers("resolver@server.com")
        self.assertEqual(len(aid.getResolvers()), 1)
        self.assertEqual(aid.getResolvers()[0], "resolver@server.com")
        aid.addProperty("prop1")
        self.assertEqual(len(aid.getProperties()), 1)
        self.assertEqual(aid.getProperties()[0], "prop1")

    def testEqual(self):
        a1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        a2 = spade.AID.aid()
        a2.setName("name1")
        a2.addAddress("addr1")
        a2.addAddress("addresses2")
        a2.addResolvers("resolver1")
        self.assertEqual(a1, a2)

        a1.addAddress("address3")
        self.assertNotEqual(a1, a2)
        a1 = spade.AID.aid(name="name1", addresses=["addr1"], resolvers=["resolver1"])
        self.assertNotEqual(a1, a2)
        a1 = spade.AID.aid(name="name1_1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        self.assertNotEqual(a1, a2)

    def testMatch(self):
        a1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        a2 = spade.AID.aid(name="name1", addresses=["addr1"], resolvers=["resolver1"])

        self.assertEqual(a1.match(a2), True)

        a2 = spade.AID.aid(name="nam", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        self.assertEqual(a1.match(a2), True)

        a2 = spade.AID.aid(addresses=["addresses2"])
        self.assertEqual(a1.match(a2), True)

        a2 = spade.AID.aid(name="other", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        self.assertEqual(a1.match(a2), False)

        a2 = spade.AID.aid(name="name1", addresses=["addr2"], resolvers=["resolver1"])
        self.assertEqual(a1.match(a2), False)

    def testXML(self):
        xml1 = '<agent-identifier>\n\t<name>name1</name>\n\t<addresses>\n\t\t<url>addr1</url>\n\t\t<url>addresses2</url>\n\t</addresses>\n</agent-identifier>\n'
        aid1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        xml2 = aid1.asXML()

        assert isEqualXML(xml1, xml2)

    def testContentObject(self):

        aid1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])

        co = spade.content.ContentObject()
        co["name"] = "name1"
        co["addresses"] = ["addr1", "addresses2"]
        co["resolvers"] = ["resolver1"]
        #co["properties"] = []

        assert aid1.asContentObject() == co

    def testCO2XML(self):
        co = spade.content.ContentObject()
        co["name"] = "name1"
        co["addresses"] = ["addr1", "addresses2"]

        aid1 = spade.AID.aid(co=co)
        xml1 = aid1.asXML()
        xml2 = '<agent-identifier>\n\t<name>name1</name>\n\t<addresses>\n\t\t<url>addr1</url>\n\t\t<url>addresses2</url>\n\t</addresses>\n</agent-identifier>\n'

        assert isEqualXML(xml1, xml2)

    def testCOSanity(self):
        aid1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        co = aid1.asContentObject()
        aid2 = spade.AID.aid(co=co)
        assert aid1 == aid2

        co2 = aid2.asContentObject()
        assert co == co2

    def testLoadSL0(self):
        parser = spade.SL0Parser.SL0Parser()
        sl0 = "((agent-identifier\n:name name1\n:addresses \n(sequence\naddr1\naddresses2\n)\n:resolvers \n(sequence\nresolver1\n)\n)\n)"
        content = parser.parse(sl0)
        self.assertNotEqual(content, None)

        aid1 = spade.AID.aid(name="name1", addresses=["addr1", "addresses2"], resolvers=["resolver1"])
        aid2 = spade.AID.aid()
        aid2.loadSL0(content)

        assert aid1 == aid2

        assert sl0 == "(" + str(aid2) + ")"
        assert str(aid1) == str(aid2)

    def testSL2XMLSanity(self):
        parser = spade.SL0Parser.SL0Parser()
        sl0 = """((agent-identifier :name name1 :addresses  (sequence addr1 addresses2 ) :resolvers (sequence resolver1)))"""
        content = parser.parse(sl0)
        self.assertNotEqual(content, None)

        xml1 = '<agent-identifier>\n\t<name>name1</name>\n\t<addresses>\n\t\t<url>addr1</url>\n\t\t<url>addresses2</url>\n\t</addresses>\n</agent-identifier>\n'
        aid2 = spade.AID.aid()
        aid2.loadSL0(content)

        assert isEqualXML(xml1, aid2.asXML())


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
