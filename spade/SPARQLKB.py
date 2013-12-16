# -*- coding: utf-8 -*-
from logic import KB
from SPARQLWrapper import SPARQLWrapper, JSON, XML
from exceptions import NotImplementedError


class SPARQLKB(KB):
    '''SPARQL endpoint knowledge base'''
    def __init__(self, sentence=None, endpoint=None):
        '''Constructor method
        Usage:
        sentence - RDF triple to be added to KB (not implemented; default:None)
        endpoint - URL of endpoint to query'''
        self.sparql = SPARQLWrapper(endpoint)
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        '''Adding triples to RDF store - not implemented'''
        raise NotImplementedError('Adding sentences to RDF knowledge bases is not implemented')

    def ask(self, query):
        '''Queries the endpoint'''
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(XML)
        res = self.sparql.query().convert().getElementsByTagName('result')
        res = [dict([(bin.attributes['name'].nodeValue, bin.firstChild.firstChild.nodeValue) for bin in node.getElementsByTagName('binding')]) for node in res]
        return res

    def retract(self, sentence):
        '''Removing triples from RDF store - not implemented'''
        raise NotImplementedError('Removing sentences to RDF knowledge bases is not implemented')

    def _encode( self, key, value ):
	'''Encoding a value in the triple store - not implemented'''
	raise NotImplementedError('Encoding values in RDF knowledge bases is not implemented')

    def _decode( self, key ):
	'''Decoding a value from the triple store - not implemented'''
	raise NotImplementedError('Decoding values from RDF knowledge bases is not implemented')

if __name__ == '__main__':
    s = SPARQLKB(endpoint='http://lod.openlinksw.com/sparql')
    for result in s.ask('''
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
} ORDER BY ?p LIMIT 500 '''):
        print result['l'], result['p'], result['c']

    s = SPARQLKB(endpoint='http://dbpedia.org/sparql')
    for result in s.ask('''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE {
     <http://dbpedia.org/resource/Croatia>
     rdfs:label
     ?label
    }'''):
        print result['label']
