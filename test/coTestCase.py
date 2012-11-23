
# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade
import xmpp


class ContentObjectTestCase(unittest.TestCase):

    def setUp(self):
        #self.rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/"><rdf:Description rdf:about="http://en.wikipedia.org/wiki/Tony_Benn"><dc:title>Tony Benn</dc:title><dc:publisher>Wikipedia</dc:publisher><foaf:primaryTopic><foaf:Person><foaf:name>Tony Benn</foaf:name></foaf:Person></foaf:primaryTopic></rdf:Description></rdf:RDF>"""
        self.rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/"><rdf:Description><dc:title>Tony Benn</dc:title><dc:publisher>Wikipedia</dc:publisher><foaf:primaryTopic><foaf:Person><foaf:name list="true"><foaf:name>Tony Benn</foaf:name><foaf:name>Pepe</foaf:name></foaf:name></foaf:Person></foaf:primaryTopic></rdf:Description></rdf:RDF>"""
        self.nb = xmpp.simplexml.NodeBuilder(self.rdf)

        self.co = spade.content.ContentObject()
        self.co.addNamespace("http://xmlns.com/foaf/0.1/", "foaf:")
        self.co.addNamespace("http://purl.org/dc/elements/1.1/", "dc")
        self.co["rdf:Description"] = spade.content.ContentObject()
        self.co["rdf:Description"]["dc:title"] = "Tony Benn"
        self.co["rdf:Description"]["dc:publisher"] = "Wikipedia"
        self.co["rdf:Description"]["foaf:primaryTopic"] = spade.content.ContentObject()
        self.co["rdf:Description"]["foaf:primaryTopic"]["foaf:Person"] = spade.content.ContentObject()
        self.co["rdf:Description"].primaryTopic.Person["foaf:name"] = ["Tony Benn", "Pepe"]

    def tearDown(self):
        pass

    def testRDFXML2CO(self):
        sco = spade.content.RDFXML2CO(self.rdf)
        self.assertEqual(sco, self.co)

    def testCO2RDFXML(self):
        rdf = self.co.asRDFXML()
        assert isEqualXML(rdf, self.rdf)

    def testGetData(self):
        co = spade.content.ContentObject()
        co["test1"] = spade.content.ContentObject()
        co["test1"]["test2"] = "test3"

        assert co.test1.test2 == "test3"

    def testCOSanity(self):
        rdf = self.co.asRDFXML()
        co = spade.content.RDFXML2CO(rdf)

        assert co == self.co

    def testRDFSanity(self):
        co = spade.content.RDFXML2CO(self.rdf)
        rdf = co.asRDFXML()

        assert isEqualXML(rdf, self.rdf)


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
