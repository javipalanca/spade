# -*- coding: utf-8 -*-
from pyparsing import *
import sys


class SL0Parser:
    """
    SL parser
    """

    def __init__(self):

        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        word = ~Literal(":") + Word(alphanums + "-_@./\\:")
        StringLiteral = Combine(Literal('"') + ZeroOrMore(CharsNotIn('\"') | (Literal('\\"'))) + Literal('"')).streamline()
        String = (word | StringLiteral)  # | ByteLengthEncodedString )
        Constant = String

        Key = String
        Expr = Forward()
        Parameter = Dict(Group(Literal(":").suppress() + Key + Group(Constant | Expr)))
        Expr << Dict(Group(lpar + Key + Group(OneOrMore(Parameter) | OneOrMore(Constant) | OneOrMore(Expr)) + rpar))
        Content = (lpar + OneOrMore(Expr) + rpar)

        self.bnf = Content

        #self.bnf.setDebug()

        try:
            self.bnf.validate()
            #print "BNF VALID!!!"

        except Exception, err:
            print "ERROR: BNF NOT VALID!!!"
            print err
            #sys.exit(-1)

    def parse(self, string):
        """
        parses a string
        returns a pyparsing.ParseResults
        """

        m = None
        try:
            m = self.bnf.parseString(str(string))
        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "|"
            print err
            #sys.exit(-1)
        except Exception, err:
            print "Unknown Parsing Exception"
            print err
            #sys.exit(-1)

        return m

    def parseFile(self, file):
        """
        parses a file
        returns a pyparsing.ParseResults
        """

        try:
            m = self.bnf.parseFile(file)
        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "|"
            print err
            sys.exit(-1)
        except Exception, err:
            print "Unkwonw Exception"
            print err
            sys.exit(-1)

        return m

if __name__ == "__main__":
    p = SL0Parser()
    msg = p.parse("((prueba :name (set (bla uno) (bla dos))))")
    #msg = p.parseFile("message.sl0")
    #print repr(msg)
    print msg.asXML()
    print msg.asList()
    #print "--------------------"
    #print msg.action['agent-identifier'].addresses.keys()
    #print msg.action['agent-identifier'].addresses.sequence[1]

    print msg.prueba.name.set
    for cosa in msg.prueba.name.set:
        print cosa
    """
    print msg.prueba.name.set.bla
    print msg.prueba.name.set.bla.keys()
    print msg.prueba.name.set.bla.values()
    print msg.prueba.name.set.bla[0]
    print "--"
    print msg.prueba.name.set.values()
    """
    print "--"

    slgrande = """((result
      (search
        (set
          (df-agent-description
            :name
              (agent-identifier
                :name scheduler-agent@foo.com
                :addresses (sequence iiop://foo.com/acc))
            :ontology (set meeting-scheduler FIPA-Agent-Management)
            :languages (set FIPA-SL0 FIPA-SL1 KIF)
            :services (set
              (service-description
                :name profiling
                :type meeting-scheduler-service)
              (service-description
                :name profiling
                :type user-profiling-service)))))))"""
    slgrande = """((result  (set (ams-agent-description
:name (agent-identifier
:name agent@alien3.dsic.upv.es
:addresses
(sequence
xmpp://agent@alien3.dsic.upv.es
)
)

:ownership agent@alien3.dsic.upv.es
)
 (ams-agent-description
:name (agent-identifier
:name ams.alien3.dsic.upv.es
:addresses
(sequence
xmpp://ams.alien3.dsic.upv.es
)
)

:ownership SPADE
:state active)
 (ams-agent-description
:name (agent-identifier
:name df.alien3.dsic.upv.es
:addresses
(sequence
xmpp://df.alien3.dsic.upv.es
)
)

:ownership SPADE
:state active)
 )))"""
    from DF import DfAgentDescription
    msg = p.parse(slgrande)
    print msg
    for dfd in msg.result.search.set:
        d = DfAgentDescription()
        d.loadSL0(dfd[1])
        print str(d)
