from xmpp import simplexml
#from copy import copy
#from _dict2xml import dict2Xml

def co2xml(map):
    """ Convenience method for transforming dictionaries into xml.  
        The transformation is {x:y} --> <x>y</x> """
    xml = ""
    for key, value in map.items():
        if "ContentObject" in str(type(value)):
            xml += "<%s>%s</%s>" % (key, co2xml(value), key)
        else:
            xml += "<%s>%s</%s>" % (key, value, key)
    return xml

class ContentObject(dict):
    def __init__(self):
        dict.__init__(self)
        self.namespaces = {}
        print "INIT",self.namespaces
        
    def __getattr__(self, name): return self[name]

    def pprint(self, ind=0):
        s = ""
        for k,v in self.items():
                try:
                        s = s + ('\t'*ind)+str(k)+":\n"+v.pprint(ind+1) + '\n'
                except:
                        s = s + ('\t'*ind)+str(k)+": " + str(v) + '\n'
        return s
    
    def asRDFXML(self):
		# Build rdf:RDF node
		root = simplexml.Node("rdf:RDF", {"xmlns:rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#"})
		nss = {}
		for k,v in self.namespaces.items():
		    if v in ["xml:","rdf:"]:
		        pass
		    else:
		        nss["xmlns:"+v[:-1]] = k
		root.attrs.update(nss)
		root.addData("#WILDCARD#")
		return str(root).replace("#WILDCARD#",co2xml(self))


def Node2CO(node, nsdict):
    if len(node.kids) == 0:
        # Leaf node
		if node.getData():
			return node.getData()
		else:
			try:
				return node.attrs["rdf:resource"]
			except:
				return ""
    else:
        # Blank node
        s = ContentObject()
        for c in node.kids:  
            if c.namespace in nsdict.keys():
                key = nsdict[c.namespace]+c.name
            else:
                key = c.name
            s[key] = Node2CO(c,nsdict)
        return s
            

def RDFXML2CO(rdfdata):
    #print "Gonna parse: "+rdfdata
    nb = simplexml.NodeBuilder(rdfdata)
    #print "Parsed: "+str(nb.getDom())+str(nb.namespaces)
    co = Node2CO(nb.getDom(), nb.namespaces)
    co.namespaces.update(nb.namespaces)
    return co


if __name__=="__main__":
    import urllib2
    f = urllib2.urlopen("http://infomesh.net/2003/rdfparser/meta.rdf")
    #f = urllib2.urlopen("http://tourism.gti-ia.dsic.upv.es/rdf/ComidasTascaRapida.rdf")

    ex = """<rdf:RDF
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

    #sco = RDFXML2CO(f.read())
    sco = RDFXML2CO(ex)
    print str(sco)
    print sco.pprint()
    #print sco["rdf:Description"]["dc:creator"]["foaf:name"], str(type(sco["rdf:Description"]["dc:creator"]["foaf:name"]))
    #print sco["rdf:Description"]["dc:creator"]["foaf:homePage"]
    print sco.asRDFXML()
    print sco.namespaces