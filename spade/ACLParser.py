# -*- coding: cp1252 -*-
from pyparsing import *
import sys
from ACLMessage import *
import AID
from BasicFipaDateTime import *

class ACLParser:
	"""
	Parser for the ACL language
	"""

	def __init__(self):

		lpar = Literal("(").suppress()
		rpar = Literal(")").suppress()
		digit = oneOf("0 1 2 3 4 5 6 7 8 9")
		sign = oneOf("+ -")
		dot = Literal(".")
		Exponent = oneOf("e E")

		_bslash = "\\"
		_escapables = 'tnrfbacdeghijklmopqsuvwxyz"' + _bslash
		_octDigits = "01234567"
		_escapedChar = ( Word( _bslash, _escapables, exact=2 ) | Word( _bslash, _octDigits, min=2, max=4 ) )

		_sglQuote = Literal("'")
		_dblQuote = Literal('"')
		StringLiteral = Combine( _dblQuote.suppress() + ZeroOrMore( CharsNotIn('\\"\r') | _escapedChar ) + _dblQuote.suppress() ).streamline()


                #Word = [~ "\0x00" – "\0x20", "(", ")", "#", "0" – "9", "-", "@"]
                #       [~ "\0x00" – "\0x20", "(", ")"]*
		ACLWord = Word(alphanums+"#@.-")
		#StringLiteral = "\"" ([ ~ "\"" ] | "\\\"")* "\""
		#StringLiteral = Combine(Literal('"')+OneOrMore(Word(alphanums+"#@ .:-_[]()+?'¿¡!$%&=*,,;<>/\\"))+Literal('"'))

                #ByteLengthEncodedString = "#" Digit+ "\"" <byte sequence>
		ByteLengthEncodedString = Literal("TODO")
		String = (StringLiteral | ByteLengthEncodedString)


		Year = Combine(digit + digit + digit + digit)
		Month = Combine(digit + digit)
		Day = Combine(digit + digit)
		Hour = Combine(digit + digit)
		Minute = Combine(digit + digit)
		Second = Combine(digit + digit)
		MilliSecond = Combine(digit + digit + digit)
		DateTime = Combine(Optional(sign) + Year + Month + Day + Literal("T") + Hour + Minute + Second + MilliSecond)

		FloatExponent = Combine(Exponent + Optional(sign) + OneOrMore(digit))
		FloatMantissa = Combine((OneOrMore(digit) + dot + ZeroOrMore(digit)) | (ZeroOrMore(digit) + dot + OneOrMore(digit)) )
		Float = Combine((Optional(sign) + FloatMantissa + Optional(FloatExponent) ) | ( Optional(sign) + OneOrMore(digit) + FloatExponent ))

		Integer = Combine(Optional(sign) + OneOrMore(digit))
		Number = Group(Integer | Float)

		"""
		#bnf de una URL
		void=empty
	        digits = nums
		hex = nums + "abcdefABCDEF"
		safe =  "$-_@.&+-"
		extra = "!*\"'(),"
		escape =  "%" + hex + hex
		xalphas = Word(alphanums+safe+extra+escape)
		ialpha = (Word(alphas) + Optional(xalphas))
		alphanum2 = alphanums+"-"+"_"+"."+"+"
		password = Forward()
		password << (alphanum2+Optional(password))
		user=Forward()
		user << (alphanum2+Optional(user))
		search = Forward()
		search << (xalphas + Optional(Literal("+")+search))
		segment = xalphas
		path = Forward()
		path << (void | (segment + Optional(Literal("/")+path)))
		port = digits
		hostname = Forward()
		hostnumber = (digits + dot + digits + dot + digits + dot + digits)
		hostname << ialpha + Optional(dot + hostname)
		formcode = (Literal("N")|Literal("T")|Literal("C"))
		ftptype = ((Literal("A")+formcode)|(Literal("E")+formcode)|Literal("I")|(Literal("L")+digits))
		host = (hostname|hostnumber)
		hostport = (host + Optional(Literal(":")+port))
		login = (Optional(user + Optional(Literal(":")+password) + Literal("@")) + hostport )
		mailtoaddress = Combine(Literal("mailto:")+ xalphas + Literal("@") + hostname)
		ftpaddress = Combine(Literal("ftp://")+login+Literal("/")+path+Optional(Literal(";")+ftptype))
		httpaddress = Combine(Literal("http://")+hostport+Optional(Literal("/")+path) +Optional(Literal("?")+search))
		URL = (httpaddress|ftpaddress|mailtoaddress)
		"""
		URL = Word(alphanums+":/#@.")
		
		
		URLSequence = (lpar + Literal("sequence").suppress() + OneOrMore(URL) + rpar)#.setResultsName("URLseq")

		AgentIdentifier = Forward()

		AgentIdentifierSequence = Group(lpar + Literal("sequence").suppress() + OneOrMore(AgentIdentifier) + rpar)#.setResultsName("AIDseq")

		#AddressSequence  = Group(lpar + Literal("sequence").suppress() + OneOrMore(URL)+rpar)   #Word(alphanums+"/.:+?")) + rpar)

		AgentIdentifier << Group( \
			lpar + Literal("agent-identifier").suppress() + \
			Literal(":name").suppress() + ACLWord.setResultsName("name") + \
			Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) + \
			Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) +\
			rpar)#.setResultsName("AID")
		
		#AgentIdentifier << Group(lpar + Literal("agent-identifier").suppress() + Literal(":name").suppress() + Word(alphanums+"@.").setResultsName("name") + Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) + Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) + rpar)#.setResultsName("AID")
		
		AgentIdentifierSet = Group(lpar + Literal("set").suppress() + OneOrMore(AgentIdentifier) + rpar)

		Expression = Forward()
		Expression << (ACLWord | String | Number | DateTime | (lpar + Expression + rpar))
		#Expression << (Word(alphanums).setResultsName("word") | String.setResultsName("string") | Number.setResultsName("number") | DateTime.setResultsName("datetime") | Combine(lpar + Expression + rpar).setResultsName("expression"))


		MessageParameter = ( \
			Literal(":sender").suppress() + AgentIdentifier.setResultsName("sender") | \
			Literal(":receiver").suppress() + AgentIdentifierSet.setResultsName("receiver") | \
			Literal(":content").suppress() + String.setResultsName("content") | \
			Literal(":reply-with").suppress() + Expression.setResultsName("reply-with") | \
			Literal(":reply-by").suppress() + DateTime.setResultsName("reply-by") | \
			Literal(":in-reply-to").suppress() + Expression.setResultsName("in-reply-to") | \
			Literal(":reply-to").suppress() + AgentIdentifierSet.setResultsName("reply-to") | \
			Literal(":language").suppress() + Expression.setResultsName("language") | \
			Literal(":encoding").suppress() + Expression.setResultsName("encoding") | \
			Literal(":ontology").suppress() + Expression.setResultsName("ontology") | \
			Literal(":protocol").suppress() + ACLWord.setResultsName("protocol") | \
			Literal(":conversation-id").suppress() + Expression.setResultsName("conversation-id") \
			)

		MessageType = ( \
			Literal("accept-proposal")|\
			Literal("agree")|\
			Literal("cancel")|\
			Literal("cfp")|\
			Literal("confirm")|\
			Literal("disconfirm")|\
			Literal("failure")|\
			Literal("inform")|\
			Literal("inform-if")|\
			Literal("inform-ref")|\
			Literal("not-understood")|\
			Literal("propagate")|\
			Literal("propose")|\
			Literal("proxy")|\
			Literal("query-if")|\
			Literal("query-ref")|\
			Literal("refuse")|\
			Literal("reject-proposal")|\
			Literal("request")|\
			Literal("request-when")|\
			Literal("request-whenever")|\
			Literal("subscribe")\
			)

		Message = (lpar + MessageType.setResultsName("msgtype") + OneOrMore(MessageParameter.setResultsName("msgParameter")) + rpar)#.setResultsName("message")

		ACLCommunicativeAct = Message

		self.bnf = ACLCommunicativeAct

		#bnf = OneOrMore(line).setResultsName("program")

		#bnf.ignore(comment)
		#bnf.ignore(directive)

		try:
			self.bnf.validate()

		except Exception, err:
			print err
			sys.exit(-1)
		

		#bnf.setDebug()

	def processAID(self, _aid):
		"""
		parses an AID.
		returns a pyparsing.ParseResult class
		"""

		aid = AID.aid()

		if 'name' in _aid:
			aid.setName(_aid['name'])

		if 'addresses' in _aid:
			addr = _aid['addresses']
			for i in addr:
				aid.addAddress(i)

		if 'resolvers' in _aid:
			res = _aid['resolvers']
			for i in res:
				aid.addResolvers(self.processAID(i))

		return aid

	def parse(self,string):
		"""
		parses a string
		returns a pyparsing.ParseResult class
		"""

		try:
			m = self.bnf.parseString(string)
		except ParseException, err:
			print err.line
			print " "*(err.column-1)+"^"
			print err
			sys.exit(-1)
		except Exception, err:
			print "Unkwonw Exception"
			print err
			sys.exit(-1)

		return self.buildACL(m)

	def parseFile(self,file):
		"""
		parses a file
		returns an ACLMessage
		"""

		try:
			m = self.bnf.parseFile(file)
		except ParseException, err:
			print err.line
			print " "*(err.column-1)+"^"
			print err
			sys.exit(-1)
		except Exception, err:
			print "Unkwonw Exception"
			print err
			sys.exit(-1)

		return self.buildACL(m)

	def buildACL(self, m):
		"""
		returns an ACLMessage object from a pyparsing.ParseResults object
		"""
		
		#print repr(m)
		#print m.asXML()
		#print m.asList()

		msg = ACLMessage()

		if 'msgtype' in m:
			msg.setPerformative(m['msgtype'])

		if 'sender' in m:
			msg.setSender(self.processAID(m['sender']))

		if 'receiver' in m:
			recv = m['receiver']
			for i in recv:
				msg.addReceiver(self.processAID(i))

		if 'content' in m:
			msg.setContent(m['content'])

		if 'reply-with' in m:
			msg.setReplyWith(m['reply-with'])

		if 'reply-by' in m:
			msg.setReplyBy(BasicFipaDateTime(m['reply-by']))

		if 'in-reply-to' in m:
			msg.setInReplyTo(m['in-reply-to'])

		if 'reply-to' in m:
			r = m['reply-to']
			for i in r:
				msg.AddReplyTo(self.processAID(i))

		if 'language' in m:
			msg.setLanguage(m['language'])

		if 'encoding' in m:
			msg.setEncoding(m['encoding'])

		if 'ontology' in m:
			msg.setOntology(m['ontology'])

		if 'protocol' in m:
			msg.setProtocol(m['protocol'])

		if 'conversation-id' in m:
			msg.setConversationId(m['conversation-id'])

		
		return msg



#p = ACLParser()
#msg = p.parse("message3.acl")
#print msg



#Debug print
#print program.asXML("instruction")
#for line in program:
#	print line
#	for k in line.keys():
#		print k + ':' + str(line[k])
#	print


#exception control
#	except ParseException,err:
#		print err.line
#		print " "*(err.column-1)+"^"
#		print err
#
#	except RecursiveGrammarException, err:
#		print err.line
#		print err


