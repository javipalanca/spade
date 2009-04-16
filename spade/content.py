from xmpp import simplexml

class SpadeContentObject(dict):
    def __getattr__(self, name): return self[name]

    def pprint(self, ind=0):
        s = ""
        for k,v in self.items():
                try:
                        s = s + ('\t'*ind)+str(k)+":\n"+v.pprint(ind+1) + '\n'
                except:
                        s = s + ('\t'*ind)+str(k)+": " + str(v) + '\n'
        return s
        

def Node2SCO(node, nsdict):
    if len(node.kids) == 0:
        # Leaf node
        return node.data
    else:
        # Blank node
        s = SpadeContentObject()
        for c in node.kids:  
            if c.namespace in nsdict.keys():
                key = nsdict[c.namespace]+c.name
            else:
                key = c.name
            s[key] = Node2SCO(c,nsdict)
        return s
            

def RDFXML2SCO(rdfdata):
    #print "Gonna parse: "+rdfdata
    nb = simplexml.NodeBuilder(rdfdata)
    #print "Parsed: "+str(nb.getDom())+str(nb.namespaces)
    return Node2SCO(nb.getDom(), nb.namespaces)


if __name__=="__main__":
    import urllib2
    f = urllib2.urlopen("http://infomesh.net/2003/rdfparser/meta.rdf")
    sco = RDFXML2SCO(f.read())
    print str(sco)
    print sco.pprint()
    