# -*- coding: utf-8 -*-
from spade.utils import deprecated
from xmpp import simplexml


def co2xml(map):
    """ Convenience recursive function for transforming ContentObjects into XML.
        The transformation is {x:y} --> <x>y</x> """
    xml = ""
    for key, value in list(map.items()):
        if isinstance(value, ContentObject):
            xml += "<%s>%s</%s>" % (key, co2xml(value), key)
        elif isinstance(value, list):
            xml += '<%s list="true">' % (key)
            for i in value:
                xml += "<%s>%s</%s>" % (key, i, key)
            xml += "</%s>" % (key)
        elif value is not None and value != "None":
            xml += "<%s>%s</%s>" % (key, value, key)
    return xml


class ContentObject(dict):
    """
    WARNING: copy.copy() does NOT work for this class :-?
    """

    def __init__(self, namespaces={}):
        dict.__init__(self)
        self.namespaces = namespaces

    def __setitem__(self, key, value):
        try:
            if ":" in key:
                prefix, tag = key.rsplit(":")
                if prefix not in self.namespaces:
                    # The usual FIPA namespace
                    if prefix == "fipa":
                        self.addNamespace("http://www.fipa.org/schemas/fipa-rdf0#", "fipa")
                    else:
                        self.addNamespace("", prefix)
        except:
            pass
        return dict.__setitem__(self, key, value)

    # TODO
    def DEACTIVATED__setattr__(self, key, value):
        """
        Overloader of __setattr__ allows for entering keys in prefix:tag format
        without worry.
        """
        if '_ContentObject__initialised' not in list(self.__dict__.keys()):
            return dict.__setattr__(self, key, value)
        elif key in list(self.__dict__.keys()):
            dict.__setattr__(self, key, value)
        else:
            try:
                if ":" in key:
                    prefix, tag = key.rsplit(":")
                    if prefix not in self.namespaces:
                        # The usual FIPA namespace
                        if prefix == "fipa":
                            self.addNamespace("http://www.fipa.org/schemas/fipa-rdf0#", "fipa")
                        else:
                            self.addNamespace("", prefix)
            except:
                pass
            self.__setitem__(key, value)

    def __getattr__(self, name):
        try:
            if name in list(self.keys()):
                return self[name]
        except:
            pass
        for ns in list(self.namespaces.values()):
            try:
                if ns + name in list(self.keys()):
                    return self[ns + name]
            except:
                pass
        # Ethical dilemma: Should ContentObject return a None when trying to
        # access a key that does not exist or should it raise an Exception?
        # raise KeyError
        return None

    def add_namespace(self, uri, abv):
        if abv[-1] != ":":
            abv = abv + ":"
        self.namespaces[uri] = abv
        return

    addNamespace = deprecated(add_namespace, "addNamespace")

    def pprint(self, ind=0):
        s = ""
        for k, v in list(self.items()):
            try:
                s = s + ('\t' * ind) + str(k) + ":\n" + v.pprint(ind + 1) + '\n'
            except:
                s = s + ('\t' * ind) + str(k) + ": " + str(v) + '\n'
        return s

    def to_rdfxml(self):
        # Build rdf:RDF node
        root = simplexml.Node("rdf:RDF", {"xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"})
        nss = {}
        for k, v in list(self.namespaces.items()):
            if v in ["xml:", "rdf:"]:
                pass
            elif v is not None and v != "None":
                nss["xmlns:" + v[:-1]] = k
        root.attrs.update(nss)
        root.addData("#WILDCARD#")
        return str(root).replace("#WILDCARD#", co2xml(self))

    asRDFXML = deprecated(to_rdfxml, "asRDFXML")

    def __str__(self):
        return co2xml(self)


def node2co(node, nsdict):
    if len(node.kids) == 0:
        # Leaf node
        if node.getData():
            return str(node.getData())
        else:
            try:
                return str(node.attrs["rdf:resource"])
            except:
                return ""
    else:
        # Blank node
        is_list = False
        #  Is it a list?
        if "list" in list(node.attrs.keys()):
            # It IS a marked list
            is_list = True
        else:
            for c in node.kids[1:]:
                if node.kids[0].name == c.name:
                    #  It IS a f*ck*ng list!!!
                    is_list = True
                    break
        if is_list:
            s = []
            for c in node.kids:
                s.append(node2co(c, nsdict))
        else:
            s = ContentObject()
            for c in node.kids:
                if c.namespace in list(nsdict.keys()):
                    key = nsdict[c.namespace] + c.name
                else:
                    key = c.name
                s[key] = Node2CO(c, nsdict)
        return s


Node2CO = deprecated(node2co, "Node2CO")


def rdfxml2co(rdfdata):
    nb = simplexml.NodeBuilder(rdfdata)
    co = node2co(nb.getDom(), nb.namespaces)
    co.namespaces.update(nb.namespaces)
    return co


RDFXML2CO = deprecated(rdfxml2co, "RDFXML2CO")


if __name__ == "__main__":

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
        <rdf:bla>
            <rdf:friend>Alice</rdf:friend>
            <rdf:friend>Bob</rdf:friend>
        </rdf:bla>
    </rdf:RDF>
    """

    sco = rdfxml2co(ex)
    sco.add_namespace("http://spade2.googlecode.com/ns/2.0/", "spade:")
    sco["rdf:Description"]["foaf:primaryTopic"]["spade:friend"] = []
    sco["rdf:Description"]["foaf:primaryTopic"]["spade:friend"].append("John Doe")
    sco["rdf:Description"]["foaf:primaryTopic"]["spade:friend"].append("Chuck Bartowski")
    sco["rdf:Description"]["foaf:primaryTopic"]["spade:friend"].append("Sarah Connor")
    sco["spade:uno"] = ContentObject()
    sco["spade:uno"]["spade:dos"] = "FOO"
    sco.uno["spade:tres"] = "BAR"

    print("ORIGINAL:")
    print(sco.pprint())
    print(sco.to_rdfxml())
    sco2 = rdfxml2co(sco.to_rdfxml())
    print("SECOND:")
    print(sco2.pprint())
    print(sco2.to_rdfxml())

