import os
import sys
import unittest
sys.path.append('../..')

import spade
from spade.bdi import *
from spade.pyxf import ECLiPSeExecutableNotFound, Flora2ExecutableNotFound, SWIExecutableNotFound, XSBExecutableNotFound
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
	    
	    try:
	        from spade import SPARQLKB
	    except:
	        self.fail("Could not import SPARQLKB. Try installing SPARQLWrapper (sudo easy_install SPARQLWrapper)")
	        
	    self.a.configureKB("SPARQL", sentence=None, path='http://lod.openlinksw.com/sparql')
	    for result in self.a.askBelieve(sparql1):
	        assert result["p"] in ["0.5", "0.55", "0.75", "0.85"]
	        assert result["c"] == "GBP"

	def testSPARQLdbpedia(self):
	    try:
	        from spade import SPARQLKB
	    except:
	        self.fail("Could not import SPARQLKB. Try installing SPARQLWrapper (sudo easy_install SPARQLWrapper)")
	        
	    self.a.configureKB("SPARQL", sentence=None, path='http://dbpedia.org/sparql')
	    for result in self.a.askBelieve(sparql2):
	        assert result["name"] in ["Croatia","Republic of Croatia","Republika Hrvatska"]
		    
	def testEclipse(self):
	    try:
	        from spade import ECLiPSeKB
	    except:
	        self.fail("Could not import ECLiPSeKB")

	    try:
	        self.a.configureKB("ECLiPSe", None, "eclipse")
	    except ECLiPSeExecutableNotFound:
		    self.fail('ECLiPSe Prolog executable not found on the specified path.')

	    if not issubclass(self.a.kb.__class__,ECLiPSeKB.ECLiPSeKB):
			self.fail("ECLiPSe was not properly configured.")

	    self.a.addBelieve( 'a(b,c)' )
	    self.a.addBelieve( 'a(c,d)' )
	    self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Y) )' )
	    self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )

	    for result in self.a.askBelieve( 'p(X,Y)' ):
			assert result in [{'Y': 'c', 'X': 'b'},{'Y': 'd', 'X': 'c'},{'Y': 'd', 'X': 'b'}]

	def testFlora2(self):
		try:
		    from spade import Flora2KB
		except:
		    self.fail("Could not import Flora2KB")
		try:    
		    self.a.configureKB("Flora2", None, "runflora")
		except Flora2ExecutableNotFound:
		    self.fail('Flora-2 executable not found on the specified path. Try installing flora2')

		if not issubclass(self.a.kb.__class__,Flora2KB.Flora2KB):
			self.fail("Flora2 was not properly configured.")

		self.a.addBelieve( 'a[ b->c ]' )
		self.a.addBelieve( '( ?x[ c->?y ] :- ?x[ b->?y ] )', 'insertrule' )

		for result in self.a.askBelieve( '?x[ ?y->?z ]' ):
			assert result in [{'y': 'b', 'x': 'a', 'z': 'c'},{'y': 'c', 'x': 'a', 'z': 'c'}]

  		self.a.removeBelieve( 'a[ b->c ]' )
		result = self.a.askBelieve( '?x[ ?y->?z ]' )
		assert len(result)==0

	def testSWI(self):
		try:
		    from spade import SWIKB
		except:
		    self.fail("Could not import SWIKB")

		try:
		    self.a.configureKB("SWI", None, "swipl")
		except SWIExecutableNotFound:
		    self.fail('SWI-Prolog executable not found on the specified path. Try installing swi-prolog.')

		if not issubclass(self.a.kb.__class__,SWIKB.SWIKB):
			self.fail("SWI was not properly configured.")

		self.a.addBelieve( 'a(b,c)' )
		self.a.addBelieve( 'a(c,d)' )
		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Y) )' ) 
  		self.a.addBelieve( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )

		for result in self.a.askBelieve( 'p(X,Y)' ):
		    assert result in [{'Y': 'c', 'X': 'b'}, {'Y': 'd', 'X': 'c'}, {'Y': 'd', 'X': 'b'}]

  		self.a.removeBelieve( 'a(b,c)' )
		for result in self.a.askBelieve( 'p(X,Y)' ):
		    assert result in [{'Y': 'd', 'X': 'c'}]

  		self.a.removeBelieve( 'a(c,d)' )
		self.assertFalse(self.a.askBelieve( 'p(X,Y)' ))
		

	def testXSB(self):
		try:
		    from spade import XSBKB
		except:
		    self.fail("Could not import XSBKB")

		try:
		    self.a.configureKB("XSB", None, "xsb")
		except XSBExecutableNotFound:
		    self.fail('XSB executable not found on the specified path. Try installing xsb')

		if not issubclass(self.a.kb.__class__,XSBKB.XSBKB):
			self.fail("XSB was not properly configured.")

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
