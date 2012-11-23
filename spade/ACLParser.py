# -*- coding: utf-8 -*-
from pyparsing import *
import sys
import ACLMessage
import AID
from BasicFipaDateTime import *

import xml.sax
from xml.sax import handler


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
        _escapedChar = (Word(_bslash, _escapables, exact=2) | Word(_bslash, _octDigits, min=2, max=4))

        _sglQuote = Literal("'")
        _dblQuote = Literal('"')
        StringLiteral = Combine(_dblQuote.suppress() + ZeroOrMore(CharsNotIn('\\"\r') | _escapedChar) + _dblQuote.suppress()).streamline()

        #Word = [~ "\0x00" – "\0x20", "(", ")", "#", "0" – "9", "-", "@"]
        #       [~ "\0x00" – "\0x20", "(", ")"]*
        ACLWord = Word(alphanums + "#@.-")
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
        FloatMantissa = Combine((OneOrMore(digit) + dot + ZeroOrMore(digit)) | (ZeroOrMore(digit) + dot + OneOrMore(digit)))
        Float = Combine((Optional(sign) + FloatMantissa + Optional(FloatExponent)) | (Optional(sign) + OneOrMore(digit) + FloatExponent))

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

        #URL = Word(alphanums+":/#@.")
        URL = Word(alphanums + ":/#@.-")

        URLSequence = (lpar + Literal("sequence").suppress() + OneOrMore(URL) + rpar)  # .setResultsName("URLseq")

        AgentIdentifier = Forward()

        AgentIdentifierSequence = Group(lpar + Literal("sequence").suppress() + OneOrMore(AgentIdentifier) + rpar)  # .setResultsName("AIDseq")

        #AddressSequence  = Group(lpar + Literal("sequence").suppress() + OneOrMore(URL)+rpar)   #Word(alphanums+"/.:+?")) + rpar)

        AgentIdentifier << Group(
            lpar + Literal("agent-identifier").suppress() +
            #Literal(":name").suppress() + ACLWord.setResultsName("name") +
            Literal(":name").suppress() + URL.setResultsName("name") +
            Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) +
            Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) +
            # This one for the X-tras (thanks Jade)
            # Make it more general-case oriented
            Optional(Literal(":X-JADE-agent-classname").suppress() + URL.suppress()) +
            rpar)  # .setResultsName("AID")

        #AgentIdentifier << Group(lpar + Literal("agent-identifier").suppress() + Literal(":name").suppress() + Word(alphanums+"@.").setResultsName("name") + Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) + Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) + rpar)#.setResultsName("AID")

        AgentIdentifierSet = Group(lpar + Literal("set").suppress() + OneOrMore(AgentIdentifier) + rpar)

        Expression = Forward()
        Expression << (ACLWord | String | Number | DateTime | (lpar + Expression + rpar))
        #Expression << (Word(alphanums).setResultsName("word") | String.setResultsName("string") | Number.setResultsName("number") | DateTime.setResultsName("datetime") | Combine(lpar + Expression + rpar).setResultsName("expression"))

        MessageParameter = (
            Literal(":sender").suppress() + AgentIdentifier.setResultsName("sender") |
            Literal(":receiver").suppress() + AgentIdentifierSet.setResultsName("receiver") |
            Literal(":content").suppress() + String.setResultsName("content") |
            #Literal(":reply-with").suppress() + Expression.setResultsName("reply-with") |
            Literal(":reply-with").suppress() + URL.setResultsName("reply-with") |
            Literal(":reply-by").suppress() + DateTime.setResultsName("reply-by") |
            Literal(":in-reply-to").suppress() + Expression.setResultsName("in-reply-to") |
            Literal(":reply-to").suppress() + AgentIdentifierSet.setResultsName("reply-to") |
            Literal(":language").suppress() + Expression.setResultsName("language") |
            Literal(":encoding").suppress() + Expression.setResultsName("encoding") |
            Literal(":ontology").suppress() + Expression.setResultsName("ontology") |
            Literal(":protocol").suppress() + ACLWord.setResultsName("protocol") |
            #Literal(":conversation-id").suppress() + Expression.setResultsName("conversation-id")
            Literal(":conversation-id").suppress() + URL.setResultsName("conversation-id")
        )

        MessageType = (
            Literal("accept-proposal") |
            Literal("agree") |
            Literal("cancel") |
            Literal("cfp") |
            Literal("confirm") |
            Literal("disconfirm") |
            Literal("failure") |
            Literal("inform") |
            Literal("inform-if") |
            Literal("inform-ref") |
            Literal("not-understood") |
            Literal("propagate") |
            Literal("propose") |
            Literal("proxy") |
            Literal("query-if") |
            Literal("query-ref") |
            Literal("refuse") |
            Literal("reject-proposal") |
            Literal("request") |
            Literal("request-when") |
            Literal("request-whenever") |
            Literal("subscribe") |
            # I'm looking at you, Jade!
            Literal("ACCEPT-PROPOSAL") |
            Literal("AGREE") |
            Literal("CANCEL") |
            Literal("CFP") |
            Literal("CONFIRM") |
            Literal("DISCONFIRM") |
            Literal("FAILURE") |
            Literal("INFORM") |
            Literal("INFORM-IF") |
            Literal("INFORM-REF") |
            Literal("NOT-UNDERSTOOD") |
            Literal("PROPAGATE") |
            Literal("PROPOSE") |
            Literal("PROXY") |
            Literal("QUERY-IF") |
            Literal("QUERY-REF") |
            Literal("REFUSE") |
            Literal("REJECT-PROPOSAL") |
            Literal("REQUEST") |
            Literal("REQUEST-WHEN") |
            Literal("REQUEST-WHENEVER") |
            Literal("SUBSCRIBE")
        )

        Message = (lpar + MessageType.setResultsName("msgtype") + OneOrMore(MessageParameter.setResultsName("msgParameter")) + rpar)  # .setResultsName("message")

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

    def parse(self, string):
        """
        parses a string
        returns a pyparsing.ParseResult class
        """

        try:
            m = self.bnf.parseString(string)
        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "^"
            print err
            sys.exit(-1)
        except Exception, err:
            print "Unkwonw Exception"
            print err
            sys.exit(-1)

        return self.buildACL(m)

    def parseFile(self, file):
        """
        parses a file
        returns an ACLMessage
        """

        try:
            m = self.bnf.parseFile(file)
        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "^"
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

        msg = ACLMessage.ACLMessage()

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


class ACLxmlParser(handler.ContentHandler):

    def __init__(self):

        #constants
        self.FIPA_MESSAGE_TAG = "fipa-message"
        self.ACT_TAG = "act"
        self.CONVERSATION_ID_TAG = "conversation-id"
        self.SENDER_TAG = "sender"
        self.RECEIVER_TAG = "receiver"
        self.CONTENT_TAG = "content"
        self.LANGUAGE_TAG = "language"
        self.ENCODING_TAG = "encoding"
        self.ONTOLOGY_TAG = "ontology"
        self.PROTOCOL_TAG = "protocol"
        self.REPLY_WITH_TAG = "reply-with"
        self.IN_REPLY_TO_TAG = "in-reply-to"
        self.REPLY_BY_TAG = "reply-by"
        self.REPLY_TO_TAG = "reply-to"
        self.CONVERSATION_ID_TAG = "conversation-id"
        self.AGENT_ID_TAG = "agent-identifier"
        self.NAME_TAG = "name"
        self.ADDRESSES_TAG = "addresses"
        self.URL_TAG = "url"
        self.RESOLVERS_TAG = "resolvers"
        self.USER_DEFINED_TAG = "user-defined"
        self.TIME_TAG = "time"
        self.ID_TAG = "id"
        self.HREF_TAG = "href"
        self.OT = "<"
        self.ET = "</"
        self.CT = ">"
        self.NULL = ""

    """
    ***************************************************
    *               Decoding methods                  *
    ***************************************************
    """

    def startDocument(self):
        self.msg = ACLMessage.ACLMessage()

    def endDocument(self):
        pass

    #This method is called when exist characters in the elements
    def characters(self, buff):
        self.accumulator = self.accumulator + buff

    def startElement(self, localName, attributes):

        self.accumulator = ""

        if self.FIPA_MESSAGE_TAG == localName.lower():
            self.msg.setPerformative(attributes.getValue(self.ACT_TAG))
            try:
                self.msg.setConversationId(attributes.getValue(self.CONVERSATION_ID_TAG))

            except:
                pass

        if self.SENDER_TAG == localName.lower():
            self.aid = AID.aid()
            self.aidTag = self.SENDER_TAG

        if self.RECEIVER_TAG == localName.lower():
            self.aid = AID.aid()
            self.aidTag = self.RECEIVER_TAG

        if self.REPLY_TO_TAG == localName.lower():
            self.aid = AID.aid()
            self.aidTag = self.REPLY_TO_TAG

        if self.RESOLVERS_TAG == localName.lower():
            self.aid = AID.aid()
            self.aidTag = self.RESOLVERS_TAG

        if self.REPLY_BY_TAG == localName.lower():
            self.msg.setReplyBy(BasicFipaDateTime(attributes.getValue(self.TIME_TAG)))

        if self.NAME_TAG == localName.lower():
            self.aid.setName(attributes.getValue(self.ID_TAG))

        if self.URL_TAG == localName.lower():
            self.aid.addAddress(attributes.getValue(self.HREF_TAG))

    def endElement(self, localName):

        if self.CONTENT_TAG == localName.lower():
            self.msg.setContent(self.accumulator)

        if self.LANGUAGE_TAG == localName.lower():
            self.msg.setLanguage(self.accumulator)

        if self.ENCODING_TAG == localName.lower():
            self.msg.setEncoding(self.accumulator)

        if self.ONTOLOGY_TAG == localName.lower():
            self.msg.setOntology(self.accumulator)

        if self.PROTOCOL_TAG == localName.lower():
            self.msg.setProtocol(self.accumulator)

        if self.REPLY_WITH_TAG == localName.lower():
            self.msg.setReplyWith(self.accumulator)

        if self.IN_REPLY_TO_TAG == localName.lower():
            self.msg.setInReplyTo(self.accumulator)

        if self.REPLY_TO_TAG == localName.lower() or \
            self.SENDER_TAG == localName.lower() or \
            self.RECEIVER_TAG == localName.lower() or \
                self.RESOLVERS_TAG == localName.lower():
            self.aidTag = ""

        if self.CONVERSATION_ID_TAG == localName.lower():
            self.msg.setConversationId(self.accumulator)

        if self.AGENT_ID_TAG == localName.lower():
            if self.aidTag == self.SENDER_TAG:
                self.msg.setSender(self.aid)
            elif self.aidTag == self.RECEIVER_TAG:
                self.msg.addReceiver(self.aid)
            elif self.aidTag == self.REPLY_TO_TAG:
                self.msg.addReplyTo(self.aid)
            elif self.aidTag == self.RESOLVERS_TAG:
                self.msg.addResolvers(self.aid)

    """
      This does the following:
      < tag >
         content
      </ tag >
    """
    def encodeTag(self, tag, content, proptag=None, propcontent=None):
        sb = self.OT + tag
        if proptag is not None:
            sb = sb + " " + proptag + '="' + str(propcontent) + '"'

        if content is None or content == "":
            sb = sb + "/" + self.CT
            return sb
        sb = sb + self.CT
        sb = sb + content
        sb = sb + self.ET + tag + self.CT

        return sb

    """ Encode the information of Agent, Tags To and From """
    def encodeAid(self, aid):

        sb = self.OT + self.AGENT_ID_TAG + self.CT
        sb = sb + self.encodeTag(self.NAME_TAG, None, self.ID_TAG, aid.getName())

        sb = sb + self.OT + self.ADDRESSES_TAG + self.CT
        addresses = aid.getAddresses()
        for addr in addresses:
            sb = sb + self.encodeTag(self.URL_TAG, "", self.HREF_TAG, addr)
        sb = sb + self.ET + self.ADDRESSES_TAG + self.CT

        resolvers = aid.getResolvers()
        if len(resolvers) > 0:
            sb = sb + self.OT + self.RESOLVERS_TAG + self.CT
            for res in resolvers:
                sb = sb + self.encodeAid(res)
            sb = sb + self.ET + self.RESOLVERS_TAG + self.CT

        sb = sb + self.ET + self.AGENT_ID_TAG + self.CT

        return sb

    def encodeXML(self, msg):

        sb = self.OT + self.FIPA_MESSAGE_TAG
        if msg.getPerformative():
            sb += " " + self.ACT_TAG + '="' + msg.getPerformative() + '"'
        sb += self.CT

        #sender
        if msg.getSender():
            sb += self.OT + self.SENDER_TAG + self.CT
            sb += self.encodeAid(msg.getSender())
            sb += self.ET + self.SENDER_TAG + self.CT

        #receivers
        if len(msg.getReceivers()) > 0:
            sb += self.OT + self.RECEIVER_TAG + self.CT
            for r in msg.getReceivers():
                sb += self.encodeAid(r)
            sb += self.ET + self.RECEIVER_TAG + self.CT

        if msg.getContent():
            sb += self.encodeTag(self.CONTENT_TAG, str(msg.getContent()))

        if msg.getLanguage():
            sb += self.encodeTag(self.LANGUAGE_TAG, msg.getLanguage())

        if msg.getEncoding():
            sb += self.encodeTag(self.ENCODING_TAG, msg.getEncoding())

        if msg.getOntology():
            sb += self.encodeTag(self.ONTOLOGY_TAG, msg.getOntology())

        if msg.getProtocol():
            sb += self.encodeTag(self.PROTOCOL_TAG, msg.getProtocol())

        if msg.getReplyWith():
            sb += self.encodeTag(self.REPLY_WITH_TAG, msg.getReplyWith())

        if msg.getInReplyTo():
            sb += self.encodeTag(self.IN_REPLY_TO_TAG, msg.getInReplyTo())

        if msg.getReplyBy():
            date = BasicFipaDateTime()
            date.fromString(str(msg.getReplyBy()))
            sb += self.encodeTag(self.REPLY_BY_TAG, str(date))

        if len(msg.getReplyTo()) > 0:
            sb += self.OT + self.REPLY_TO_TAG + self.CT
            for e in msg.getReplyTo():
                sb += self.encodeAid(e)
            sb += self.ET + self.REPLY_TO_TAG + self.CT

        if msg.getConversationId():
            sb += self.encodeTag(self.CONVERSATION_ID_TAG, msg.getConversationId())

        sb += self.ET + self.FIPA_MESSAGE_TAG + self.CT

        return sb

    def parse(self, _in):
        """
        parses the xml input
        """
        xml.sax.parseString(_in, self)
        return self.msg

    def parseFile(self, file):
        xml.sax.parse(file, self)
        return self.msg


#p = ACLParser()
#msg = p.parse("message3.acl")
#print msg
if __name__ == "__main__":

    p = ACLxmlParser()
    m = p.parseFile("m.xml")
    print m
    print p.encodeXML(m)



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
