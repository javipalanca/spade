# -*- coding: utf-8 -*-
import sys
from .pyparsing import *
from . import ACLMessage
from . import AID
from .BasicFipaDateTime import *

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
        StringLiteral = Combine(
            _dblQuote.suppress() + ZeroOrMore(CharsNotIn('\\"\r') | _escapedChar) + _dblQuote.suppress()).streamline()

        # Word = [~ "\0x00" – "\0x20", "(", ")", "#", "0" – "9", "-", "@"]
        #       [~ "\0x00" – "\0x20", "(", ")"]*
        ACLWord = Word(alphanums + "#@.-")
        # StringLiteral = "\"" ([ ~ "\"" ] | "\\\"")* "\""
        # StringLiteral = Combine(Literal('"')+OneOrMore(Word(alphanums+"#@ .:-_[]()+?'¿¡!$%&=*,,;<>/\\"))+Literal('"'))

        # ByteLengthEncodedString = "#" Digit+ "\"" <byte sequence>
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
        FloatMantissa = Combine(
            (OneOrMore(digit) + dot + ZeroOrMore(digit)) | (ZeroOrMore(digit) + dot + OneOrMore(digit)))
        Float = Combine((Optional(sign) + FloatMantissa + Optional(FloatExponent)) | (
        Optional(sign) + OneOrMore(digit) + FloatExponent))

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

        # URL = Word(alphanums+":/#@.")
        URL = Word(alphanums + ":/#@.-")

        URLSequence = (lpar + Literal("sequence").suppress() + OneOrMore(URL) + rpar)  # .setResultsName("URLseq")

        AgentIdentifier = Forward()

        AgentIdentifierSequence = Group(
            lpar + Literal("sequence").suppress() + OneOrMore(AgentIdentifier) + rpar)  # .setResultsName("AIDseq")

        # AddressSequence  = Group(lpar + Literal("sequence").suppress() + OneOrMore(URL)+rpar)   #Word(alphanums+"/.:+?")) + rpar)

        AgentIdentifier << Group(
            lpar + Literal("agent-identifier").suppress() +
            # Literal(":name").suppress() + ACLWord.setResultsName("name") +
            Literal(":name").suppress() + URL.setResultsName("name") +
            Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) +
            Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) +
            # This one for the X-tras (thanks Jade)
            # Make it more general-case oriented
            Optional(Literal(":X-JADE-agent-classname").suppress() + URL.suppress()) +
            rpar)  # .setResultsName("AID")

        # AgentIdentifier << Group(lpar + Literal("agent-identifier").suppress() + Literal(":name").suppress() + Word(alphanums+"@.").setResultsName("name") + Optional(Literal(":addresses").suppress() + URLSequence.setResultsName("addresses")) + Optional(Literal(":resolvers").suppress() + AgentIdentifierSequence.setResultsName("resolvers")) + rpar)#.setResultsName("AID")

        AgentIdentifierSet = Group(lpar + Literal("set").suppress() + OneOrMore(AgentIdentifier) + rpar)

        Expression = Forward()
        Expression << (ACLWord | String | Number | DateTime | (lpar + Expression + rpar))
        # Expression << (Word(alphanums).setResultsName("word") | String.setResultsName("string") | Number.setResultsName("number") | DateTime.setResultsName("datetime") | Combine(lpar + Expression + rpar).setResultsName("expression"))

        MessageParameter = (
            Literal(":sender").suppress() + AgentIdentifier.setResultsName("sender") |
            Literal(":receiver").suppress() + AgentIdentifierSet.setResultsName("receiver") |
            Literal(":content").suppress() + String.setResultsName("content") |
            # Literal(":reply-with").suppress() + Expression.setResultsName("reply-with") |
            Literal(":reply-with").suppress() + URL.setResultsName("reply-with") |
            Literal(":reply-by").suppress() + DateTime.setResultsName("reply-by") |
            Literal(":in-reply-to").suppress() + Expression.setResultsName("in-reply-to") |
            Literal(":reply-to").suppress() + AgentIdentifierSet.setResultsName("reply-to") |
            Literal(":language").suppress() + Expression.setResultsName("language") |
            Literal(":encoding").suppress() + Expression.setResultsName("encoding") |
            Literal(":ontology").suppress() + Expression.setResultsName("ontology") |
            Literal(":protocol").suppress() + ACLWord.setResultsName("protocol") |
            # Literal(":conversation-id").suppress() + Expression.setResultsName("conversation-id")
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

        Message = (lpar + MessageType.setResultsName("msgtype") + OneOrMore(
            MessageParameter.setResultsName("msgParameter")) + rpar)  # .setResultsName("message")

        ACLCommunicativeAct = Message

        self.bnf = ACLCommunicativeAct

        try:
            self.bnf.validate()

        except Exception as err:
            print(err)
            sys.exit(-1)

    def parse_AID(self, _aid):
        """
        parses an AID.
        returns a pyparsing.ParseResult class
        """

        aid = AID.aid()

        if 'name' in _aid:
            aid.set_name(_aid['name'])

        if 'addresses' in _aid:
            addr = _aid['addresses']
            for i in addr:
                aid.add_address(i)

        if 'resolvers' in _aid:
            res = _aid['resolvers']
            for i in res:
                aid.add_resolvers(self.parse_AID(i))

        return aid

    def parse(self, string):
        """
        parses a string
        returns a pyparsing.ParseResult class
        """

        try:
            parsed = self.bnf.parseString(string)
        except ParseException as err:
            print(err.line)
            print(" " * (err.column - 1) + "^")
            print(err)
            sys.exit(-1)
        except Exception as err:
            print("Unkwonw Exception")
            print(err)
            sys.exit(-1)

        return self.build_acl(parsed)

    def parse_file(self, file):
        """
        parses a file
        returns an ACLMessage
        """

        try:
            parsed = self.bnf.parseFile(file)
        except ParseException as err:
            print(err.line)
            print(" " * (err.column - 1) + "^")
            print(err)
            sys.exit(-1)
        except Exception as err:
            print("Unkwonw Exception")
            print(err)
            sys.exit(-1)

        return self.build_acl(parsed)

    def build_acl(self, parsed_object):
        """
        returns an ACLMessage object from a pyparsing.ParseResults object
        """

        msg = ACLMessage.ACLMessage()

        if 'msgtype' in parsed_object:
            msg.set_performative(parsed_object['msgtype'])

        if 'sender' in parsed_object:
            msg.set_sender(self.parse_AID(parsed_object['sender']))

        if 'receiver' in parsed_object:
            recv = parsed_object['receiver']
            for i in recv:
                msg.add_receiver(self.parse_AID(i))

        if 'content' in parsed_object:
            msg.set_content(parsed_object['content'])

        if 'reply-with' in parsed_object:
            msg.set_reply_with(parsed_object['reply-with'])

        if 'reply-by' in parsed_object:
            msg.set_reply_by(BasicFipaDateTime(parsed_object['reply-by']))

        if 'in-reply-to' in parsed_object:
            msg.set_in_reply_to(parsed_object['in-reply-to'])

        if 'reply-to' in parsed_object:
            r = parsed_object['reply-to']
            for i in r:
                msg.add_reply_to(self.parse_AID(i))

        if 'language' in parsed_object:
            msg.set_language(parsed_object['language'])

        if 'encoding' in parsed_object:
            msg.set_encoding(parsed_object['encoding'])

        if 'ontology' in parsed_object:
            msg.setOntology(parsed_object['ontology'])

        if 'protocol' in parsed_object:
            msg.set_protocol(parsed_object['protocol'])

        if 'conversation-id' in parsed_object:
            msg.set_conversation_id(parsed_object['conversation-id'])

        return msg


class ACLxmlParser(handler.ContentHandler):
    def __init__(self):

        # constants
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

    # This method is called when exist characters in the elements
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
            self.aid_tag = self.SENDER_TAG

        if self.RECEIVER_TAG == localName.lower():
            self.aid = AID.aid()
            self.aid_tag = self.RECEIVER_TAG

        if self.REPLY_TO_TAG == localName.lower():
            self.aid = AID.aid()
            self.aid_tag = self.REPLY_TO_TAG

        if self.RESOLVERS_TAG == localName.lower():
            self.aid = AID.aid()
            self.aid_tag = self.RESOLVERS_TAG

        if self.REPLY_BY_TAG == localName.lower():
            self.msg.set_reply_by(BasicFipaDateTime(attributes.getValue(self.TIME_TAG)))

        if self.NAME_TAG == localName.lower():
            self.aid.set_name(attributes.getValue(self.ID_TAG))

        if self.URL_TAG == localName.lower():
            self.aid.add_address(attributes.getValue(self.HREF_TAG))

    def endElement(self, localname):

        if self.CONTENT_TAG == localname.lower():
            self.msg.set_content(self.accumulator)

        if self.LANGUAGE_TAG == localname.lower():
            self.msg.set_language(self.accumulator)

        if self.ENCODING_TAG == localname.lower():
            self.msg.set_encoding(self.accumulator)

        if self.ONTOLOGY_TAG == localname.lower():
            self.msg.set_ontology(self.accumulator)

        if self.PROTOCOL_TAG == localname.lower():
            self.msg.set_protocol(self.accumulator)

        if self.REPLY_WITH_TAG == localname.lower():
            self.msg.set_reply_with(self.accumulator)

        if self.IN_REPLY_TO_TAG == localname.lower():
            self.msg.set_in_reply_to(self.accumulator)

        if self.REPLY_TO_TAG == localname.lower() or \
                        self.SENDER_TAG == localname.lower() or \
                        self.RECEIVER_TAG == localname.lower() or \
                        self.RESOLVERS_TAG == localname.lower():
            self.aid_tag = ""

        if self.CONVERSATION_ID_TAG == localname.lower():
            self.msg.set_conversation_id(self.accumulator)

        if self.AGENT_ID_TAG == localname.lower():
            if self.aid_tag == self.SENDER_TAG:
                self.msg.set_sender(self.aid)
            elif self.aid_tag == self.RECEIVER_TAG:
                self.msg.add_receiver(self.aid)
            elif self.aid_tag == self.REPLY_TO_TAG:
                self.msg.add_reply_to(self.aid)
            #elif self.aid_tag == self.RESOLVERS_TAG:
            #    self.msg.addResolvers(self.aid)

    """
      This does the following:
      < tag >
         content
      </ tag >
    """

    def encode_tag(self, tag, content, proptag=None, propcontent=None):
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

    def encode_aid(self, aid):

        sb = self.OT + self.AGENT_ID_TAG + self.CT
        sb = sb + self.encode_tag(self.NAME_TAG, None, self.ID_TAG, aid.getName())

        sb = sb + self.OT + self.ADDRESSES_TAG + self.CT
        addresses = aid.get_addresses()
        for addr in addresses:
            sb = sb + self.encode_tag(self.URL_TAG, "", self.HREF_TAG, addr)
        sb = sb + self.ET + self.ADDRESSES_TAG + self.CT

        resolvers = aid.get_resolvers()
        if len(resolvers) > 0:
            sb = sb + self.OT + self.RESOLVERS_TAG + self.CT
            for res in resolvers:
                sb = sb + self.encode_aid(res)
            sb = sb + self.ET + self.RESOLVERS_TAG + self.CT

        sb = sb + self.ET + self.AGENT_ID_TAG + self.CT

        return sb

    def encode_xml(self, msg):

        sb = self.OT + self.FIPA_MESSAGE_TAG
        if msg.getPerformative():
            sb += " " + self.ACT_TAG + '="' + msg.getPerformative() + '"'
        sb += self.CT

        # sender
        if msg.get_sender():
            sb += self.OT + self.SENDER_TAG + self.CT
            sb += self.encode_aid(msg.get_sender())
            sb += self.ET + self.SENDER_TAG + self.CT

        # receivers
        if len(msg.get_receivers()) > 0:
            sb += self.OT + self.RECEIVER_TAG + self.CT
            for r in msg.get_receivers():
                sb += self.encode_aid(r)
            sb += self.ET + self.RECEIVER_TAG + self.CT

        if msg.get_content():
            sb += self.encode_tag(self.CONTENT_TAG, str(msg.get_content()))

        if msg.get_language():
            sb += self.encode_tag(self.LANGUAGE_TAG, msg.get_language())

        if msg.get_encoding():
            sb += self.encode_tag(self.ENCODING_TAG, msg.get_encoding())

        if msg.get_ontology():
            sb += self.encode_tag(self.ONTOLOGY_TAG, msg.get_ontology())

        if msg.get_protocol():
            sb += self.encode_tag(self.PROTOCOL_TAG, msg.get_protocol())

        if msg.get_reply_with():
            sb += self.encode_tag(self.REPLY_WITH_TAG, msg.get_reply_with())

        if msg.get_in_reply_to():
            sb += self.encode_tag(self.IN_REPLY_TO_TAG, msg.get_in_reply_to())

        if msg.get_reply_by():
            date = BasicFipaDateTime()
            date.from_string(str(msg.get_reply_by()))
            sb += self.encode_tag(self.REPLY_BY_TAG, str(date))

        if len(msg.get_reply_to()) > 0:
            sb += self.OT + self.REPLY_TO_TAG + self.CT
            for e in msg.get_reply_to():
                sb += self.encode_aid(e)
            sb += self.ET + self.REPLY_TO_TAG + self.CT

        if msg.get_conversation_id():
            sb += self.encode_tag(self.CONVERSATION_ID_TAG, msg.get_conversation_id())

        sb += self.ET + self.FIPA_MESSAGE_TAG + self.CT

        return sb

    def parse(self, _in):
        """
        parses the xml input
        """
        xml.sax.parseString(_in, self)
        return self.msg

    def parse_file(self, file):
        xml.sax.parse(file, self)
        return self.msg


if __name__ == "__main__":
    parser = ACLxmlParser()
    msg = parser.parse_file("m.xml")
    print(msg)
    print(parser.encode_xml(msg))
