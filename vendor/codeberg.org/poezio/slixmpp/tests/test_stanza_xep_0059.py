import unittest
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0059 import Set
from slixmpp.xmlstream import ET


class TestSetStanzas(SlixTest):

    def testSetFirstIndex(self):
        s = Set()
        s['first'] = 'id'
        s.set_first_index('10')
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
            <first index="10">id</first>
          </set>
        """)

    def testGetFirstIndex(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <first index="10">id</first>
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        expected = '10'
        self.assertTrue(s['first_index'] == expected)

    def testDelFirstIndex(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <first index="10">id</first>
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        del s['first_index']
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
            <first>id</first>
          </set>
        """)

    def testSetBefore(self):
        s = Set()
        s['before'] = True
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before />
          </set>
        """)

    def testGetBefore(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before />
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        expected = True
        self.assertTrue(s['before'] == expected)

    def testGetBefore(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before />
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        del s['before']
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
          </set>
        """)

    def testSetBeforeVal(self):
        s = Set()
        s['before'] = 'id'
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before>id</before>
          </set>
        """)

    def testGetBeforeVal(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before>id</before>
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        expected = 'id'
        self.assertTrue(s['before'] == expected)

    def testGetBeforeVal(self):
        xml_string = """
          <set xmlns="http://jabber.org/protocol/rsm">
            <before>id</before>
          </set>
        """
        s = Set(ET.fromstring(xml_string))
        del s['before']
        self.check(s, """
          <set xmlns="http://jabber.org/protocol/rsm">
          </set>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestSetStanzas)
