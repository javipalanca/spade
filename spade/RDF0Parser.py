# -*- coding: cp1252 -*-
import xml.sax
from xml.sax import handler
import cStringIO

class Newdict(dict):
	def __getattr__(self, name): return self[name]

# build a shorthand tag
def btag(n1,n2):
	return n1+":"+n2

class RDF0Parser(handler.ContentHandler):
	"""
	FIPA RDF Content Language Parser
	"""
	def __init__(self):


		#Constants
		self.OT = "<"
		self.ET = "</"
		self.CT = ">"
		self.NULL = ""
		self.TYPE_SEP = "^^"
		

		#RDF syntax namespace constants
		self.XML_VERSION = '<?xml version="1.0"?>'
		self.RDF_PREF = "rdf"
		self.RDF = "RDF"
		self.RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
		self.ID = "ID"
		self.RESOURCE = "resource"
		self.DESCRIPTION = "Description"
		self.ABOUT = "about"			
		self.SUBJECT = "subject"
		self.PREDICATE = "predicate"
		self.OBJECT = "object"
		self.BAG = "bag"
		self.SEQ = "seq"
		self.ALT = "alt"
		self.LI	= "li"
		self.DATATYPE = "datatype"
		
		#Fipa namespace constants 
		self.FIPA_PREF = "fipa"
		self.FIPA_NS = "http://www.fipa.org/schemas/fipa-rdf0#"
		self.PROPOSITION = "Proposition"
		self.BELIEF = "belief"
		self.ACTION = "Action"
		self.ACTOR = "actor"
		self.ACT = "act"
		self.ARGUMENT = "argument"
		self.ACTOR = "actor"
		self.DONE = "done"
		self.RESULT = "result"
		self.IMPLBY = "implementedBy"
		self.CODE = "Code"
		self.LANGUAGE = "language"
		self.BINDING = "binding"
		self.CODE_URI = "code-uri"
		self.SCRIPT = "script"



		self.content = Newdict()




	#   ***************************************************
	#   *               Encoding methods                  *
	#   ***************************************************

	def encodeTag( self, tag, content ):
	
		if isinstance(content,dict):
			# encoding a RDF resource
			sb = self.encodeOneLineTag( tag, btag(self.RDF_PREF,self.RESOURCE), content[self.RESOURCE])	
		else:
			if self.TYPE_SEP in content:
				#encoding value with type
				value, type = content.split(self.TYPE_SEP)
				sb = self.encodeInitTagAttr( tag, btag(self.RDF_PREF,self.DATATYPE), type)
				sb = sb + value.strip('"')
		
			else: 
				sb = self.OT + tag + self.CT
				sb = sb + content

			sb = sb + self.ET + tag + self.CT + '\n'

		return sb
  
	def encodeInitTag( self, tag):
		sb = self.OT + tag + self.CT
		return sb + '\n'

	def encodeEndTag( self, tag):
		sb = self.ET + tag + self.CT
		return sb + '\n'

	def encodeInitTagAttr( self, tag, attr, value):
		sb = self.OT + tag + " " + attr + '="' + value + '"' + self.CT
		return sb 
 
	def encodeOneLineTag( self, tag1, tag2, value ):
		sb = self.OT + tag1 + " "
		sb = sb + tag2 + '="' + value + '"/>'
		return sb + '\n'
  
	def encode(self, content):
		"""
		Content Encoding
		"""
		#version encoding
		sb = self.XML_VERSION+'\n'
		
		#namespaces encoding
		sb = sb + self.OT + btag(self.RDF_PREF,self.RDF)+ ' ' + btag("xmlns",self.RDF_PREF) + '="' + self.RDF_NS + '"'
		sb = sb +'\n ' + btag("xmlns",self.FIPA_PREF) + '="' + self.FIPA_NS + '"' + self.CT + '\n\n'
				     

		# Action encoding  
		if self.ACTION in content:
			if self.ID in content[self.ACTION]:
				sb_action = self.encodeInitTagAttr(btag(self.FIPA_PREF,self.ACTION),btag(self.RDF_PREF,self.ID),content[self.ACTION][self.ID])

			elif self.ABOUT in content[self.ACTION]:
				sb_action = self.encodeInitTagAttr(btag(self.FIPA_PREF,self.ACTION),btag(self.RDF_PREF,self.ABOUT),content[self.ACTION][self.ABOUT])

			else:
				sb_action = self.encodeInitTag(btag(self.FIPA_PREF,self.ACTION))

			
						
			if self.ACTOR in content[self.ACTION]:
				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.ACTOR),content[self.ACTION][self.ACTOR])

			if self.ACT in content[self.ACTION]:
				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.ACT),content[self.ACTION][self.ACT])

			if self.ARGUMENT in content[self.ACTION]:
				container = None
				if self.BAG in content[self.ACTION][self.ARGUMENT]:
					container = self.BAG
				elif self.SEQ in content[self.ACTION][self.ARGUMENT]:
					container = self.SEQ
				elif self.ALT in content[self.ACTION][self.ARGUMENT]:
					container = self.ALT
				
				accum = ""
				if container == None:
					accum = content[self.ACTION][self.ARGUMENT]
				else: 
					for literal in content[self.ACTION][self.ARGUMENT][container]:
						accum = accum + self.encodeTag(btag(self.RDF_PREF,self.LI),literal)
					accum = self.encodeTag(btag(self.RDF_PREF,container),accum)
				
				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.ARGUMENT),accum)

			
			if self.IMPLBY in content[self.ACTION]:
				container = None
				# An action can be performed following alternative implementations
				if self.ALT in content[self.ACTION][self.IMPLBY]:
					container = self.ALT
			
				keys = [self.LANGUAGE, self.BINDING, self.CODE_URI, self.SCRIPT]
	
				if container == None:
					if self.CODE in content[self.ACTION][self.IMPLBY]:
						accum = ""
						
						for key in keys:
							if key in content[self.ACTION][self.IMPLBY][self.CODE]:
								accum = accum + self.encodeTag(btag(self.FIPA_PREF,key),content[self.ACTION][self.IMPLBY][self.CODE][key])
						accum = self.encodeTag(btag(self.FIPA_PREF,self.CODE),accum)
	
				else:
					accum = ""
					for code in content[self.ACTION][self.IMPLBY][self.ALT]:
						 accum2 = ""
						 for key in keys:
							if key in code[self.CODE].keys():
								accum2 = accum2 + self.encodeTag(btag(self.FIPA_PREF,key),code[self.CODE][key])
						 accum = accum + self.encodeTag(btag(self.FIPA_PREF,self.CODE),accum2)
 
					accum = self.encodeTag(btag(self.RDF_PREF,container),accum)


				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.IMPLBY),accum)



			if self.DONE in content[self.ACTION]:
				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.DONE),content[self.ACTION][self.DONE])

			
			if self.RESULT in content[self.ACTION]:
				sb_action = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.RESULT),content[self.ACTION][self.RESULT])

			

			sb = sb + sb_action + self.encodeEndTag(btag(self.FIPA_PREF,self.ACTION))
 
		

		# Proposition Encoding
		if self.PROPOSITION in content:
			accum = ""
			if self.SUBJECT in content[self.PROPOSITION]:
				accum = accum + self.encodeTag(btag(self.RDF_PREF,self.SUBJECT),content[self.PROPOSITION][self.SUBJECT])
			if self.PREDICATE in content[self.PROPOSITION]:
				accum = accum + self.encodeTag(btag(self.RDF_PREF,self.PREDICATE),content[self.PROPOSITION][self.PREDICATE])
			if self.OBJECT in content[self.PROPOSITION]:
				accum = accum + self.encodeTag(btag(self.RDF_PREF,self.OBJECT),content[self.PROPOSITION][self.OBJECT])
			if self.BELIEF in content[self.PROPOSITION]:
				accum = accum + self.encodeTag(btag(self.FIPA_PREF,self.BELIEF),content[self.PROPOSITION][self.BELIEF])
			
			sb = sb + self.encodeTag(btag(self.FIPA_PREF,self.PROPOSITION),accum)


		sb = sb + self.encodeEndTag(btag(self.RDF_PREF,self.RDF)) 
    
		return sb

		# Description Encoding
		if self.DESCRIPTION in content:
			sb = sb + self.encodeInitTagAttr(btag(self.RDF_PREF,self.DESCRIPTION),btag(self.RDF_PREF,self.ABOUT),content[self.DESCRIPTION][self.ABOUT])
			if self.DONE in content[self.DESCRIPTION]:
				sb = sb + self.encodeTag(btag(self.FIPA_PREF,self.DONE),content[self.DESCRIPTION][self.DONE])

			
			if self.RESULT in content[self.DESCRIPTION]:
				sb = sb_action + self.encodeTag(btag(self.FIPA_PREF,self.RESULT),content[self.DESCRIPTION][self.RESULT])



			sb = sb + self.encodeEndTag(btag(self.FIPA_PREF,self.ACTION))
 





	"""
	 ***************************************************
	 *               Decoding methods                  *
	 ***************************************************
	"""
   
	#This method is called when start the document XML
	def startDocument(self):
		self.prefixs = Newdict()
		self.content = Newdict()
		self.resource = {}
		self.datatype = {}
		self.container = None
		self.accumulator = ""
		self.s = ""
		self.p = ""
  

	def startPrefixMapping(self,prefix,uri):
		if uri == self.RDF_NS:
			self.prefixs['rdf']=prefix
		elif uri == self.FIPA_NS:
			self.prefixs['fipa']=prefix
		else:
			print "RDFParser: Not recognized URI"
			#excepcio sino peta despres la clau
			

	def startElementNS(self, name, qname, attributes):
	
		self.accumulator = ""
   		
		#fipa Actions 
		if btag(self.prefixs.fipa,self.ACTION) == qname:
			self.content[self.ACTION] = Newdict()
			self.s = self.ACTION
			if btag(self.prefixs.rdf,self.ID) in attributes.getQNames():
				self.content[self.ACTION][self.ID] = attributes.getValueByQName(btag(self.prefixs.rdf,self.ID))
			elif btag(self.prefixs.rdf,self.ABOUT) in attributes.getQNames():
				self.content[self.ACTION][self.ABOUT] = attributes.getValueByQName(btag(self.prefixs.rdf,self.ABOUT))


		elif btag(self.prefixs.fipa,self.ARGUMENT) == qname:
			self.content[self.s][self.ARGUMENT] = Newdict()
			self.p = self.ARGUMENT

		
		elif btag(self.prefixs.fipa,self.IMPLBY) == qname:
			self.content[self.s][self.IMPLBY] = Newdict()
			self.p = self.IMPLBY
				
		elif btag(self.prefixs.fipa,self.CODE) == qname:
			self.code = Newdict()

		elif btag(self.prefixs.rdf,self.BAG) == qname:
			self.content[self.s][self.p][self.BAG] = []
			self.container = self.BAG

		elif btag(self.prefixs.rdf,self.SEQ) == qname:
			self.content[self.s][self.p][self.SEQ] = []
			self.container = self.SEQ

		elif btag(self.prefixs.rdf,self.ALT) == qname:
			self.content[self.s][self.p][self.ALT] = []
			self.container = self.ALT
		

		#fipa Propositions	
		elif btag(self.prefixs.fipa,self.PROPOSITION) == qname:
			self.content[self.PROPOSITION]=Newdict()
			self.s = self.PROPOSITION

		#rdf Descriptions
		elif btag(self.prefixs.rdf,self.DESCRIPTION) == qname:
			self.content[self.DESCRIPTION]=Newdict()
			self.s = self.DESCRIPTION
			if btag(self.prefixs.rdf,self.ABOUT) in attributes.getQNames():
				self.content[self.DESCRIPTION][self.ABOUT] = attributes.getValueByQName(btag(self.prefixs.rdf,self.ABOUT))





		# if tag refers to a resource
		if btag(self.prefixs.rdf,self.RESOURCE) in attributes.getQNames():
				self.resource[name] = attributes.getValueByQName(btag(self.prefixs.rdf,self.RESOURCE))

		# catching datatype
		if btag(self.prefixs.rdf,self.DATATYPE) in attributes.getQNames():
				self.datatype[name] = attributes.getValueByQName(btag(self.prefixs.rdf,self.DATATYPE))

			
		
		
  
	def endElementNS(self, name, qname):

		# tags with resource don't need any value
		if self.resource.has_key(name):
			self.accumulator = {self.RESOURCE:self.resource[name]}
			self.resource.clear()

		# Adding datatype to tag with value
		if self.datatype.has_key(name):
			self.accumulator = '"'+ self.accumulator + '"' + self.TYPE_SEP + self.datatype[name]
			self.datatype.clear()	
			



		# start name check
	
		if self.ACTOR == name[1]:
			self.content[self.s][self.ACTOR] = self.accumulator

		elif self.ACT == name[1]:
			self.content[self.s][self.ACT] = self.accumulator
		
		elif self.ARGUMENT == name[1]:
			if self.content[self.s][self.ARGUMENT].keys() == []:
				self.content[self.s][self.ARGUMENT] = self.accumulator

		elif self.BAG == name[1] or self.SEQ == name[1] or self.ALT == name[1]:
			self.container = None

		
		elif self.LI == name[1]:
			if self.container != None:
				self.content[self.s][self.p][self.container].append(self.accumulator)
			else: pass 

		elif self.SUBJECT == name[1]:
			self.content[self.s][self.SUBJECT] = self.accumulator

		elif self.PREDICATE == name[1]:
			self.content[self.s][self.PREDICATE] = self.accumulator

		elif self.OBJECT == name[1]:
			self.content[self.s][self.OBJECT] = self.accumulator

		elif self.BELIEF == name[1]:
			self.content[self.s][self.BELIEF] = self.accumulator

		elif self.DONE == name[1]:
			self.content[self.s][self.DONE] = self.accumulator

		elif self.RESULT == name[1]:
			self.content[self.s][self.RESULT] = self.accumulator

		elif self.CODE == name[1]:
			if self.container != None:
				self.content[self.s][self.p][self.container].append({self.CODE:self.code})
			else: self.content[self.s][self.p][self.CODE] = self.code
	
		elif self.LANGUAGE == name[1]:
			self.code[self.LANGUAGE] = self.accumulator

		elif self.BINDING == name[1]:
			self.code[self.BINDING] = self.accumulator

		elif self.CODE_URI == name[1]:
			self.code[self.CODE_URI] = self.accumulator

		elif self.SCRIPT == name[1]:
			self.code[self.SCRIPT] = self.accumulator

		
		self.accumulator=""



	def characters(self, buff):
		self.accumulator = self.accumulator + buff

		
	# Main decoding method #
	def parse(self, s):
		parser = xml.sax.make_parser()
		parser.start_namespace_decl("xml", "http://www.w3.org/XML/1998/namespace")
		#enabling namespaces
		try:
			parser.setFeature(xml.sax.handler.feature_namespaces, 1)
		 	#parser.setFeature(xml.sax.handler.feature_namespace_prefixes, 1)
			#parser.setFeature(xml.sax.handler.feature_string_interning, 1)
		except xml.sax._exceptions.SAXNotSupportedException: pass
		except xml.sax._exceptions.SAXNotRecognizedException:pass

		#setting handler and start parsing
		parser.setContentHandler(self)
		parser.parse(cStringIO.StringIO(str(s)))
		
		#return generated content
		return self.content 


if __name__ == "__main__":
	f=open("example5.rdf","r")
	s=f.read()
	rdfparser=RDF0Parser()
	content=rdfparser.parse(s)
	print content
	result=rdfparser.encode(content)
	print result
	print rdfparser.parse(result)


"""
TODO
- no Case-sensitive (si te sentit)
- RDF Collections
- Description namespace
"""
