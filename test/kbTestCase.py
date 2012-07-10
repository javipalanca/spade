import os
import sys
import unittest
sys.path.append('../..')

import spade
from spade.bdi import *
from spade import SPARQLKB, ECLiPSeKB, Flora2KB, SWIKB, XSBKB
host = "127.0.0.1"

sparql1='''
PREFIX gr:<http://purl.org/goodrelations/v1#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?l ?p ?c ?s
WHERE {
?s a gr:Offering.
?s rdfs:label ?l.
?s gr:hasPriceSpecification ?ps.
?ps gr:hasCurrencyValue ?p.
?ps gr:hasCurrency ?c
FILTER( regex( ?l, "yoghurt", "i" ) )
} ORDER BY ?p LIMIT 500 '''

sparql2 = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?name
WHERE { 
 <http://dbpedia.org/resource/Croatia> 
 rdfs:name 
 ?name 
}'''

class KBTestCase(unittest.TestCase):
	
	def setUp(self):

		self.a = BDIAgent("kb@"+host,"secret")

	def tearDown(self):
		#self.a.stop()
		pass
		
	def testSPARQLopenlink(self):
		self.a.configureKB("SPARQL", sentence=None, path='http://lod.openlinksw.com/sparql')
		for result in self.a.askBelieve(sparql1):
		    assert result["p"] in ["0.5", "0.55", "0.75", "0.85"]
		    assert result["c"] == "GBP"

	def testSPARQLdbpedia(self):
		self.a.configureKB("SPARQL", sentence=None, path='http://dbpedia.org/sparql')
		for result in self.a.askBelieve(sparql2):
		    assert result["name"] in ["Croatia","Republic of Croatia","Republika Hrvatska"]
		    
	def testEclipse(self):

		path="/Users/jpalanca/Downloads/eclipse/bin/x86_64_macosx/eclipse"
		if not os.path.exists(path): path="eclipse"

		self.a.configureKB("ECLiPSe", None, path)

		if not issubclass(self.a.kb.__class__,ECLiPSeKB.ECLiPSeKB):
			self.fail("Could not find ECLiPSe.")

		self.a.addBelieve( 'a(b,c)' )
		self.a.addBelieve( 'a(c,d)' )
		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Y) )' )
		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )

		for result in self.a.askBelieve( 'p(X,Y)' ):
			assert result in [{'Y': 'c', 'X': 'b'},{'Y': 'd', 'X': 'c'},{'Y': 'd', 'X': 'b'}]

	def testFlora2(self):
		path="/Users/jpalanca/Downloads/flora/XSBFLORABUNDLE/flora2/runflora"
		if not os.path.exists(path): path="eclipse"

		self.a.configureKB("Flora2", None, path)

		if not issubclass(self.a.kb.__class__,Flora2KB.Flora2KB):
			self.fail("Could not find Flora2.")

		self.a.addBelieve( 'a[ b->c ]' )
		self.a.addBelieve( '( ?x[ c->?y ] :- ?x[ b->?y ] )', 'insertrule' )

		for result in self.a.askBelieve( '?x[ ?y->?z ]' ):
			assert result in [{'y': 'b', 'x': 'a', 'z': 'c'},{'y': 'c', 'x': 'a', 'z': 'c'}]

  		self.a.removeBelieve( 'a[ b->c ]' )
		result = self.a.askBelieve( '?x[ ?y->?z ]' )
		assert len(result)==0

	def testSWI(self):
		path="swipl"

		self.a.configureKB("SWI", None, path)

		if not issubclass(self.a.kb.__class__,SWIKB.SWIKB):
			self.fail("Could not find SWI pl.")

		self.a.addBelieve( 'a(b,c)' )
		self.a.addBelieve( 'a(c,d)' )
		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Y) )' ) 
  		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )

		self.assertFalse(self.a.askBelieve( 'p(X,Y)' ))

  		self.a.removeBelieve( 'a(b,c)' )
		self.assertFalse(self.a.askBelieve( 'p(X,Y)' ))

  		self.a.removeBelieve( 'a(c,d)' )
		self.assertTrue(self.a.askBelieve( 'p(X,Y)' ))

	def testXSB(self):
		path="/Users/jpalanca/Downloads/XSB/XSB/bin/xsb"
		if not os.path.exists(path): path="xsb"

		self.a.configureKB("XSB", None, path)

		if not issubclass(self.a.kb.__class__,XSBKB.XSBKB):
			self.fail("Could not find XSB.")

		self.a.addBelieve( 'a(b,c)' )
		self.a.addBelieve( 'a(c,d)' )
		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Y) )' ) 
  		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )

		for result in  self.a.askBelieve( 'p(X,Y)' ):
			assert result in [{'Y': 'c', 'X': 'b'}, {'Y': 'd', 'X': 'c'}, {'Y': 'd', 'X': 'b'}]

  		self.a.removeBelieve( 'a(b,c)' )
		for result in self.a.askBelieve( 'p(X,Y)' ):
			self.assertEqual(result,{'Y': 'd', 'X': 'c'})
 
  		self.a.removeBelieve( 'a(c,d)' )
		result = self.a.askBelieve( 'p(X,Y)' )
		assert result == False


if __name__ == "__main__":
    unittest.main()
