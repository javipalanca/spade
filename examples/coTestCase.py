import os
import sys
import time
import unittest

sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade




class ContentObjectTestCase(unittest.TestCase):
    
    def setUp(self):
        self.rdf = """<rdf:RDF
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:foaf="http://xmlns.com/foaf/0.1/" 
          xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:Description rdf:about="http://en.wikipedia.org/wiki/Tony_Benn">
                <dc:title>Tony Benn</dc:title>
                <dc:publisher>Wikipedia</dc:publisher>
                <foaf:primaryTopic>
                     <foaf:Person>
                          <foaf:name>Tony Benn</foaf:name>  
                     </foaf:Person>
                </foaf:primaryTopic>
            </rdf:Description>
        </rdf:RDF>
        """
        self.co = spade.content.ContentObject()
        self.co.addNamespace("http://xmlns.com/foaf/0.1/","foaf:")
        self.co.addNamespace("http://purl.org/dc/elements/1.1/", "dc")
        self.co.Description = spade.content.ContentObject()
        self.co.Description["dc:title"] = "Tony Benn"
        self.co.Description["dc:publisher"] = "Wikipedia"
        self.co.Description["foaf:primaryTopic"] = spade.content.ContentObject()
        self.co.Description.primaryTopic["foaf:name"] = "Tony Benn"
        
    def tearDown(self):
        pass
        
    def testRDFXML2CO(self):
        sco = spade.content.RDFXML2CO(self.rdf)
        
        print self.co
        
        self.assertEqual(sco, self.co)

if __name__ == "__main__":
    unittest.main()



