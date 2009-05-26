import os
import sys
import time
import unittest

sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade




class ContentObjectTestCase(unittest.TestCase):
    
    def setUp(self):
        self.rdf = """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/"><rdf:Description rdf:about="http://en.wikipedia.org/wiki/Tony_Benn"><dc:title>Tony Benn</dc:title><dc:publisher>Wikipedia</dc:publisher><foaf:primaryTopic><foaf:Person><foaf:name>Tony Benn</foaf:name></foaf:Person></foaf:primaryTopic></rdf:Description></rdf:RDF>"""

        self.co = spade.content.ContentObject()
        self.co.addNamespace("http://xmlns.com/foaf/0.1/","foaf:")
        self.co.addNamespace("http://purl.org/dc/elements/1.1/", "dc")
        self.co["rdf:Description"] = spade.content.ContentObject()
        self.co["rdf:Description"]["dc:title"] = "Tony Benn"
        self.co["rdf:Description"]["dc:publisher"] = "Wikipedia"
        self.co["rdf:Description"]["foaf:primaryTopic"] = spade.content.ContentObject()
        self.co["rdf:Description"]["foaf:primaryTopic"]["foaf:Person"] = spade.content.ContentObject()
        self.co["rdf:Description"].primaryTopic.Person["foaf:name"] = "Tony Benn"

    def tearDown(self):
        pass
        
    def testRDFXML2CO(self):
        sco = spade.content.RDFXML2CO(self.rdf) 
        self.assertEqual(sco, self.co)
        
    def testCO2RDFXML(self):
        sco = self.co.asRDFXML()
        self.assertEqual(sco, self.rdf)
        
    def testGetData(self):
        co = spade.content.ContentObject()
        co["test1"] = spade.content.ContentObject()
        co["test1"]["test2"]= "test3"
        
        assert co.test1.test2 == "test3"
        
    def testCOSanity(self):
        
        rdf = self.co.asRDFXML()
        co = spade.content.ContentObject(rdf)
        
        assert co == self.co
        
    def testRDFSanity(self):
        
        co = spade.content.ContentObject(self.rdf)
        rdf = co.asRDFXML()
        
        assert rdf == self.rdf

if __name__ == "__main__":
    unittest.main()



