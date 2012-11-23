# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

import spade
import xmpp

import xml.dom.minidom


def CreateSD(s=""):
    sd = spade.DF.ServiceDescription()
    sd.setName("servicename1" + s)
    sd.setType("type1" + s)
    sd.addProtocol("sdprotocol1" + s)
    sd.addOntologies("sdontology1" + s)
    sd.addLanguage("sdlanguage1" + s)
    sd.setOwnership("agent1" + s)
    sd.addProperty("P", "valueP" + s)
    sd.addProperty("Q", "valueQ" + s)

    return sd


def CreateDAD(s=""):
    dad = spade.DF.DfAgentDescription()
    aid = spade.AID.aid()
    aid.setName("aidname" + s)
    dad.setAID(aid)

    dad.addProtocol("protocol1" + s)
    dad.addOntologies("ontology1" + s)
    dad.addLanguage("language1" + s)
    dad.setLeaseTime(1000)
    dad.addScope("scope1" + s)

    return dad


def CreateCO(s=""):
    co = spade.content.ContentObject()
    co["name"] = spade.AID.aid(name="aidname" + s).asContentObject()
    co["lease-time"] = 1000
    co["protocols"] = ["protocol1" + s, "sdprotocol1" + s]
    co["ontologies"] = ["ontology1" + s, "sdontology1" + s]
    co["languages"] = ["language1" + s, "sdlanguage1" + s]
    co["scope"] = "scope1" + s

    sdco = spade.content.ContentObject()
    sdco["name"] = "servicename1" + s
    sdco["type"] = "type1" + s
    sdco["protocols"] = ["sdprotocol1" + s]
    sdco["languages"] = ["sdlanguage1" + s]
    sdco["ontologies"] = ["sdontology1" + s]
    sdco["ownership"] = "agent1" + s
    sdco["properties"] = spade.content.ContentObject()
    sdco["properties"]["P"] = "valueP" + s
    sdco["properties"]["Q"] = "valueQ" + s

    co["services"] = [sdco]

    return co


class DadTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCreateDad(self):
        dad = spade.DF.DfAgentDescription()

        self.assertEqual(dad.getName(), spade.AID.aid())
        self.assertEqual(dad.getServices(), [])
        self.assertEqual(dad.getProtocols(), [])
        self.assertEqual(dad.getOntologies(), [])
        self.assertEqual(dad.getLanguages(), [])
        self.assertEqual(dad.getLeaseTime(), None)
        self.assertEqual(dad.getScope(), [])

        aid = spade.AID.aid()
        aid.setName("aidname")
        dad.setAID(aid)
        self.assertEqual(dad.getName(), "aidname")

        dad.addProtocol("protocol1")
        self.assertEqual(dad.getProtocols(), ["protocol1"])
        dad.addOntologies("ontology1")
        self.assertEqual(dad.getOntologies(), ["ontology1"])
        dad.addLanguage("language1")
        self.assertEqual(dad.getLanguages(), ["language1"])
        dad.setLeaseTime(1000)
        self.assertEqual(dad.getLeaseTime(), 1000)
        dad.addScope("scope1")
        self.assertEqual(dad.getScope(), "scope1")

    def testAddService(self):
        dad = CreateDAD()
        sd1 = CreateSD("a")
        sd2 = CreateSD("b")

        dad.addService(sd1)
        self.assertEqual(len(dad.getServices()), 1)
        self.assertEqual(dad.getServices()[0].getName(), "servicename1a")
        self.assertEqual(dad.getProtocols(), ["protocol1", "sdprotocol1a"])
        self.assertEqual(dad.getLanguages(), ["language1", "sdlanguage1a"])
        self.assertEqual(dad.getOntologies(), ["ontology1", "sdontology1a"])

        dad.addService(sd2)
        self.assertEqual(len(dad.getServices()), 2)
        self.failIf(dad.getServices()[0].getName() not in ["servicename1a", "servicename1b"])
        self.failIf(dad.getServices()[1].getName() not in ["servicename1a", "servicename1b"])
        self.assertEqual(dad.getProtocols(), ["protocol1", "sdprotocol1a", "sdprotocol1b"])
        self.assertEqual(dad.getLanguages(), ["language1", "sdlanguage1a", "sdlanguage1b"])
        self.assertEqual(dad.getOntologies(), ["ontology1", "sdontology1a", "sdontology1b"])

    def testDelService(self):
        dad = CreateDAD()
        sd1 = CreateSD("a")
        sd2 = CreateSD("b")

        dad.addService(sd1)
        dad.addService(sd2)
        self.assertEqual(len(dad.getServices()), 2)

        delsd1 = CreateSD("a")
        r = dad.delService(delsd1)
        self.assertEqual(r, True)
        self.assertEqual(len(dad.getServices()), 1)
        self.failIf(dad.getServices()[0].getName() != "servicename1b")
        self.failIf("sdprotocol1a" in dad.getProtocols())
        self.failIf("sdlanguage1a" in dad.getLanguages())
        self.failIf("sdontology1a" in dad.getOntologies())

        delsd2 = CreateSD("b")
        dad.delService(delsd2)
        self.assertEqual(len(dad.getServices()), 0)
        self.failIf("sdprotocol1b" in dad.getProtocols())
        self.failIf("sdlanguage1b" in dad.getLanguages())
        self.failIf("sdontology1b" in dad.getOntologies())

    def testUpdateService(self):
        dad = CreateDAD()
        sd1 = CreateSD("a")
        dad.addService(sd1)

        sd2 = CreateSD("a")
        sd2.setType("updated_type")

        r = dad.updateService(sd2)
        self.assertEqual(r, True)
        self.assertEqual(len(dad.getServices()), 1)
        self.assertEqual(dad.getServices()[0].getType(), "updated_type")
        self.assertEqual(dad.getServices()[0].getName(), "servicename1a")

    def testCreateSD(self):
        sd = spade.DF.ServiceDescription()
        self.assertEqual(sd.getName(), None)
        self.assertEqual(sd.getType(), None)
        self.assertEqual(sd.getProtocols(), [])
        self.assertEqual(sd.getOntologies(), [])
        self.assertEqual(sd.getLanguages(), [])
        self.assertEqual(sd.getOwnership(), None)
        self.assertEqual(sd.getProperties(), {})

        sd.setName("servicename1")
        self.assertEqual(sd.getName(), "servicename1")
        sd.setType("type1")
        self.assertEqual(sd.getType(), "type1")
        sd.addProtocol("protocol1")
        self.assertEqual(sd.getProtocols(), ["protocol1"])
        sd.addOntologies("ontology1")
        self.assertEqual(sd.getOntologies(), ["ontology1"])
        sd.addLanguage("language1")
        self.assertEqual(sd.getLanguages(), ["language1"])
        sd.setOwnership("agent1")
        self.assertEqual(sd.getOwnership(), "agent1")
        sd.addProperty("key1", "value1")
        self.assertEqual(sd.getProperty("key1"), "value1")
        sd.addProperty("key2", "value2")
        self.assertEqual(sd.getProperty("key2"), "value2")
        self.assertEqual(sd.getProperties(), {'key1': 'value1', 'key2': 'value2'})

    def testMatchSD(self):

        sd1 = CreateSD("a")
        sd2 = spade.DF.ServiceDescription()
        sd2.setName("servicename1a")

        self.assertEqual(sd1.match(sd2), True)

        sd2.setType("type1a")
        self.assertEqual(sd1.match(sd2), True)

        sd1.addOntologies("sdontology2a")
        sd2.addOntologies("sdontology1a")
        self.assertEqual(sd1.match(sd2), True)

        sd2.setType("modified_type")
        self.assertEqual(sd1.match(sd2), False)

        sd2.addOntologies("sdontology3")
        self.assertEqual(sd1.match(sd2), False)

    def testMatchDAD(self):

        dad1 = CreateDAD("a")
        dad2 = spade.DF.DfAgentDescription()
        aid = spade.AID.aid()
        aid.setName("aidnamea")
        dad2.setAID(aid)
        self.assertEqual(dad1.match(dad2), True)

        dad2.addLanguage("language1a")
        self.assertEqual(dad1.match(dad2), True)

        dad1.addLanguage("language2a")
        self.assertEqual(dad1.match(dad2), True)

        dad2.addLanguage("language3a")
        self.assertEqual(dad1.match(dad2), False)

        dad1 = CreateDAD("a")
        dad2 = spade.DF.DfAgentDescription()
        aid = spade.AID.aid()
        aid.setName("aidnamea")
        dad2.setAID(aid)
        sd1 = CreateSD("a")
        dad1.addService(sd1)
        dad2.addService(sd1)
        self.assertEqual(dad1.match(dad2), True)

        sd2 = CreateSD("b")
        dad2.addService(sd2)
        self.assertEqual(dad1.match(dad2), False)
        dad1.addService(sd2)
        self.assertEqual(dad1.match(dad2), True)

    def testXML(self):
        xml1 = '<name><name>aidname1</name></name><lease-time>1000</lease-time><languages list="true"><languages>language11</languages><languages>sdlanguage11</languages></languages><services list="true"><services><name>servicename11</name><properties><Q>valueQ1</Q><P>valueP1</P></properties><languages list="true"><languages>sdlanguage11</languages></languages><ownership>agent11</ownership><type>type11</type><ontologies list="true"><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>sdprotocol11</protocols></protocols></services></services><scope>scope11</scope><ontologies list="true"><ontologies>ontology11</ontologies><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>protocol11</protocols><protocols>sdprotocol11</protocols></protocols>'
        dad = CreateDAD("1")
        sd = CreateSD("1")
        dad.addService(sd)
        xml2 = dad.asRDFXML()

        assert xml1 == xml2

    def testContentObject(self):

        dad = CreateDAD("1")
        sd = CreateSD("1")
        dad.addService(sd)

        co = CreateCO("1")

        assert str(dad.asContentObject()) == str(co)

    def testCO2XML(self):
        co = CreateCO("1")
        dad = spade.DF.DfAgentDescription(co=co)

        xml1 = dad.asRDFXML()
        xml2 = '<name><name>aidname1</name></name><lease-time>1000</lease-time><languages list="true"><languages>language11</languages><languages>sdlanguage11</languages></languages><services list="true"><services><name>servicename11</name><properties><Q>valueQ1</Q><P>valueP1</P></properties><languages list="true"><languages>sdlanguage11</languages></languages><ownership>agent11</ownership><type>type11</type><ontologies list="true"><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>sdprotocol11</protocols></protocols></services></services><scope>scope11</scope><ontologies list="true"><ontologies>ontology11</ontologies><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>protocol11</protocols><protocols>sdprotocol11</protocols></protocols>'

        assert xml1 == xml2

    def testCOSanity(self):
        dad1 = CreateDAD("1")
        sd1 = CreateSD("1")
        dad1.addService(sd1)
        co1 = dad1.asContentObject()

        co2 = CreateCO("1")
        dad2 = spade.DF.DfAgentDescription(co=co2)
        assert dad1.match(dad2)

        co3 = dad2.asContentObject()

        assert str(co2) == str(co3)

    def DISABLEDtestLoadSL0(self):
        parser = spade.SL0Parser.SL0Parser()
        sl0 = """(df-agent-description
        :name (agent-identifier
        :name aidname1
        )

        :protocols
        (set
        protocol11
        sdprotocol11
        )
        :ontologies
        (set
        ontology11
        sdontology11
        )
        :languages
        (set
        language11
        sdlanguage11
        )
        :services
        (set
        (service-description
        :name servicename11
        :type type11
        :protocols
        (set
        sdprotocol11 )
        :ontologies
        (set
        sdontology11 )
        :languages
        (set
        sdlanguage11 )
        :ownership agent11
        :properties
         (set
         (property :name Q :value valueQ1)
         (property :name P :value valueP1)
        )
        )

        )
        :lease-time 1000
        :scope scope11
        )
        """
        content = parser.parse(sl0)
        self.assertNotEqual(content, None)

        dad1 = CreateDAD("1")
        sd = CreateSD("1")
        dad1.addService(sd)
        dad2 = spade.DF.DfAgentDescription()
        dad2.loadSL0(content)

        assert dad1.match(dad2)

        assert sl0 == "(" + dad2.asSL0() + ")"
        assert dad1.asSL0() == dad2.asSL0()

    def DISABLEDtestSL2XMLSanity(self):
        parser = spade.SL0Parser.SL0Parser()
        sl0 = '((df-agent-description \n:name (agent-identifier\n:name aidname1\n)\n\n:services \n(set\n(service-description\n:name servicename11\n:type type11\n:protocols \n(set\nsdprotocol11 )\n:ontologies \n(set\nsdontology11 )\n:languages \n(set\nsdlanguage11 ):ownershipagent11\n:properties \n (set\n (property :name Q :value valueQ1)\n (property :name P :value valueP1)\n)\n)\n\n)\n:protocols \n(set\nprotocol11\nsdprotocol11\n)\n:ontologies \n(set\nontology11\nsdontology11\n)\n:languages \n(set\nlanguage11\nsdlanguage11\n)\n:lease-time 1000\n:scope scope11\n)\n)'
        content = parser.parse(sl0)
        self.assertNotEqual(content, None)

        xml = '<name><name>aidname1</name><addresses list="true"></addresses></name><lease-time>1000</lease-time><languages list="true"><languages>language11</languages><languages>sdlanguage11</languages></languages><services list="true"><services><name>servicename11</name><properties><Q>valueQ1</Q><P>valueP1</P></properties><languages list="true"><languages>sdlanguage11</languages></languages><ownership>agent11</ownership><type>type11</type><ontologies list="true"><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>sdprotocol11</protocols></protocols></services></services><scope>scope11</scope><ontologies list="true"><ontologies>ontology11</ontologies><ontologies>sdontology11</ontologies></ontologies><protocols list="true"><protocols>protocol11</protocols><protocols>sdprotocol11</protocols></protocols>'
        dad = spade.DF.DfAgentDescription()
        dad.loadSL0(content)

        assert isEqualXML(xml, dad.asXML())


def isEqualXML(a, b):
    da, db = xmpp.simplexml.NodeBuilder(a), xmpp.simplexml.NodeBuilder(b)
    return isEqualElement(da.getDom(), db.getDom())


def isEqualElement(a, b):
    if a.getName() != b.getName():
        return False
    if sorted(a.getAttrs().items()) != sorted(b.getAttrs().items()):
        return False
    if len(a.getChildren()) != len(b.getChildren()):
        return False
    if a.getData() and b.getData() and a.getData() != b.getData():
        return False
    for ac in a.getChildren():
        l = []
        for bc in b.getChildren():
            if ac.getName() == bc.getName():
                l.append(bc)
        if len(l) == 0:
            return False
        r = False
        for n in l:
            if len(ac.kids) == len(n.kids):
                r = True
        if not r:
            return False

        if ac.getData():
            for n in l:
                if n.getData() == ac.getData():
                    r = True
            if not r:
                return False

        if not ac.getData() and (len(ac.kids) > 0):
            for n in l:
                if isEqualElement(ac, n):
                    r = True
            if not r:
                return False

    return True


if __name__ == "__main__":
    unittest.main()
