#!/usr/bin/python
"""An RDF/XML Parser. Sean B. Palmer, 2003-05. GPL 2. Thanks to bitsko."""

import sys, re, urllib, cStringIO, xml.sax, xml.sax.handler
try: from uripath import join as urijoin
except ImportError: from urlparse import urljoin as urijoin

class Namespace(unicode): 
   def __getattr__(self, name): return self + name

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
x = Namespace("http://www.w3.org/XML/1998/namespace")

class Element(object): 
   def __init__(self, (pfx, n), qn, attrs, p=None, base=None, qnames=True): 
      self.base = attrs.x.get(x.base) or (p and p.base) or base or ''
      self.language = attrs.x.get(x.lang) or (p and p.language) or ''
      self.URI = pfx + n
      self.qname = (qnames and qn) or 'foo:bar'
      self.attrs = attrs or {}
      self.parent = p
      self.children, self.text, self.xtext = [], '', ['', '', '']

   def __getitem__(self, attr): 
      return self.attrs[attr]

class Attribs(dict): 
   def __init__(self, attrs, qnames=True):
      self.x = {}
      self.qnames = []
      for name, value in attrs.items():
         p, n = name
         if p == x: self.x[p + n] = value
         else: dict.__setitem__(self, (p or rdf) + n, value)
   def __repr__(self): 
      return ''.join([' %s="%s"' % (q, self.val(q)) for q in self.qnames])

r_id = re.compile(r'^i([rd]+)')
r_quot = re.compile(r'([^\\])"')

class RDFParser(xml.sax.handler.ContentHandler): 
   def __init__(self, sink, base=None, qnames=True): 
      self.triple = sink.triple
      self.stack = []
      self.base = base or ''
      self.genID = 0
      self.qnames = qnames
      self.disallowed = [rdf.RDF, rdf.ID, rdf.about, rdf.bagID, 
           rdf.parseType, rdf.resource, rdf.nodeID, rdf.datatype, 
           rdf.li, rdf.aboutEach, rdf.aboutEachPrefix]

   def startElementNS(self, n, q, a): 
      if self.stack: e = Element(n, q, Attribs(a, self.qnames), 
         self.stack[-1], qnames=self.qnames)
      else: e = Element(n, q, Attribs(a, self.qnames), 
         base=self.base, qnames=self.qnames)
      e.xtext[0] += '<'+e.qname+((`e.attrs`.strip() and `e.attrs`) or '')+'>'
      self.stack += [e]
	
   def characters(self, chars): 
      self.stack[-1].text += chars
      self.stack[-1].xtext[1] += chars
	
   def endElementNS(self, name, qname): 
      element = self.stack.pop()
      element.xtext[2] += '</'+element.qname+'>'
      if self.stack: 
         self.stack[-1].children += [element]
         self.stack[-1].xtext[1] += ''.join(element.xtext)
      else: self.document(element)

   def uri(self, u): 
      return "<%s>" % u

   def bNode(self, label=None): 
      if label: 
         if not label[0].isalpha(): label = 'b' + label
         return '_:' + r_id.sub('ir\g<1>', label)
      self.genID = self.genID + 1
      return '_:id%s' % (self.genID - 1)

   def literal(self, s, lang=None, dtype=None): 
      if lang and dtype: raise "ParseError", "Can't have both"
      return ''.join(('"%s"' % r_quot.sub('\g<1>\\"', `unicode(s)`[2:-1]), 
          lang and ("@" + lang) or '', dtype and ("^^<%s>" % dtype) or ''))

   def document(self, doc): 
      assert doc.URI == rdf.RDF, "Couldn't find rdf:RDF element"
      for element in doc.children: self.nodeElement(element)

   def nodeElement(self, e): 
      assert e.URI not in self.disallowed, "Disallowed element used as node"

      if e.attrs.has_key(rdf.ID): 
         e.subject = self.uri(urijoin(e.base, "#" + e[rdf.ID]))
      elif e.attrs.has_key(rdf.about): 
         e.subject = self.uri(urijoin(e.base, e[rdf.about]))
      elif e.attrs.has_key(rdf.nodeID): e.subject = self.bNode(e[rdf.nodeID])
      elif not hasattr(e, 'subject'): e.subject = self.bNode()

      if e.URI != rdf.Description: 
         self.triple(e.subject, self.uri(rdf.type), self.uri(e.URI))
      if e.attrs.has_key(rdf.type): 
         self.triple(e.subject, self.uri(rdf.type), self.uri(e[rdf.type]))
      for attr in e.attrs.keys(): 
         if attr not in self.disallowed + [rdf.type]: 
            objt = self.literal(e[attr], e.language)
            self.triple(e.subject, self.uri(attr), objt)

      for element in e.children: 
         self.propertyElt(element)

   def propertyElt(self, e): 
      if e.URI == rdf.li: 
         if not hasattr(e.parent, 'liCounter'): e.parent.liCounter = 1
         e.URI = rdf + '_' + str(e.parent.liCounter)
         e.parent.liCounter += 1

      if len(e.children) == 1 and not e.attrs.has_key(rdf.parseType): 
         self.resourcePropertyElt(e)
      elif len(e.children) == 0 and e.text: 
         self.literalPropertyElt(e)
      elif e.attrs.has_key(rdf.parseType): 
         if e[rdf.parseType] == "Resource": 
            self.parseTypeResourcePropertyElt(e)
         elif e[rdf.parseType] == "Collection": 
            self.parseTypeCollectionPropertyElt(e)
         else: self.parseTypeLiteralOrOtherPropertyElt(e)
      elif not e.text: self.emptyPropertyElt(e)

   def resourcePropertyElt(self, e): 
      n = e.children[0]
      self.nodeElement(n)
      self.triple(e.parent.subject, self.uri(e.URI), n.subject)
      if e.attrs.has_key(rdf.ID): 
         i = self.uri(urijoin(e.base, ('#' + e.attrs[rdf.ID])))
         self.reify(i, e.parent.subject, self.uri(e.URI), n.subject)

   def reify(self, r, s, p, o): 
      self.triple(r, self.uri(rdf.subject), s)
      self.triple(r, self.uri(rdf.predicate), p)
      self.triple(r, self.uri(rdf.object), o)
      self.triple(r, self.uri(rdf.type), self.uri(rdf.Statement))

   def literalPropertyElt(self, e): 
      o = self.literal(e.text, e.language, e.attrs.get(rdf.datatype))
      self.triple(e.parent.subject, self.uri(e.URI), o)
      if e.attrs.has_key(rdf.ID): 
         i = self.uri(urijoin(e.base, ('#' + e.attrs[rdf.ID])))
         self.reify(i, e.parent.subject, self.uri(e.URI), o)

   def parseTypeLiteralOrOtherPropertyElt(self, e): 
      o = self.literal(e.xtext[1], e.language, rdf.XMLLiteral)
      self.triple(e.parent.subject, self.uri(e.URI), o)
      if e.attrs.has_key(rdf.ID): 
         e.subject = i = self.uri(urijoin(e.base, ('#' + e.attrs[rdf.ID])))
         self.reify(i, e.parent.subject, self.uri(e.URI), o)

   def parseTypeResourcePropertyElt(self, e): 
      n = self.bNode()
      self.triple(e.parent.subject, self.uri(e.URI), n)
      if e.attrs.has_key(rdf.ID): 
         e.subject = i = self.uri(urijoin(e.base, ('#' + e.attrs[rdf.ID])))
         self.reify(i, e.parent.subject, self.uri(e.URI), n)
      c = Element((rdf, 'Description'), e.qname, e.attrs, e.parent, e.base)
      c.subject = n
      for child in e.children: 
         child.parent = c
         c.children += [child]
      self.nodeElement(c)

   def parseTypeCollectionPropertyElt(self, e): 
      for element in e.children: 
         self.nodeElement(element)
      s = [self.bNode() for f in e.children]
      if not s: 
         self.triple(e.parent.subject, self.uri(e.URI), self.uri(rdf.nil))
      else: 
         self.triple(e.parent.subject, self.uri(e.URI), s[0])
         for n in s: self.triple(n, self.uri(rdf.type), self.uri(rdf.List))
         for i in range(len(s)): 
            self.triple(s[i], self.uri(rdf.first), e.children[i].subject) 
         for i in range(len(s) - 1): 
            self.triple(s[i], self.uri(rdf.rest), s[i+1])
         self.triple(s[-1], self.uri(rdf.rest), self.uri(rdf.nil))

   def emptyPropertyElt(self, e): 
      if e.attrs.keys() in ([], [rdf.ID]): 
         r = self.literal(e.text, e.language) # was o
         self.triple(e.parent.subject, self.uri(e.URI), r)
      else: 
         if e.attrs.has_key(rdf.resource): 
            r = self.uri(urijoin(e.base, e[rdf.resource]))
         elif e.attrs.has_key(rdf.nodeID): r = self.bNode(e[rdf.nodeID])
         else: r = self.bNode()

         for a in filter(lambda n: n not in self.disallowed, e.attrs.keys()): 
            if a != rdf.type: 
               o = self.literal(e.attrs[a], e.language)
               self.triple(r, self.uri(a), o)
            else: self.triple(r, self.uri(rdf.type), self.uri(e.attrs[a]))
         self.triple(e.parent.subject, self.uri(e.URI), r)
      if e.attrs.has_key(rdf.ID): 
         i = self.uri(urijoin(e.base, ('#' + e.attrs[rdf.ID])))
         self.reify(i, e.parent.subject, self.uri(e.URI), r)

class Sink(object): 
   def __init__(self): self.result = ""
   def triple(self, s, p, o): self.result += "%s %s %s .\n" % (s, p, o)
   def write(self): print self.result.rstrip().encode('utf-8')

def parseRDF(s, base=None, sink=None): 
   sink = sink or Sink()
   parser = xml.sax.make_parser()
   parser.start_namespace_decl("xml", x)
   parser.setFeature(xml.sax.handler.feature_namespaces, 1)
   try: parser.setFeature(xml.sax.handler.feature_namespace_prefixes, 1)
   except xml.sax._exceptions.SAXNotSupportedException: pass
   except xml.sax._exceptions.SAXNotRecognizedException: pass
   parser.setContentHandler(RDFParser(sink, base, qnames=False))
   parser.parse(cStringIO.StringIO(s))
   return sink

def parseURI(uri, sink=None): 
   return parseRDF(urllib.urlopen(uri).read(), base=uri, sink=sink)

if __name__=="__main__": 
   if len(sys.argv) != 2: print __doc__
   else: parseURI(sys.argv[1]).write()