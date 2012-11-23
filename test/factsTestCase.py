# -*- coding: utf-8 -*-
import types
import unittest

from spade.kb import KB, KBNameNotString, KBValueNotKnown


class factsTestCase(unittest.TestCase):

    def setUp(self):

        self.kb = KB()

    def tearDown(self):
        pass

    def testInteger(self):
        self.kb.set("varname1", 1234)
        var = self.kb.get("varname1")
        assert var == 1234
        assert isinstance(var, types.IntType)

    def testString(self):
        self.kb.set("varname2", "TestString")
        var = self.kb.get("varname2")
        assert var == "teststring"
        assert isinstance(var, types.StringType)

    def testFloat(self):
        self.kb.set("varname3", 1234.5678)
        var = self.kb.get("varname3")
        assert var == 1234.5678
        assert isinstance(var, types.FloatType)

    def testList(self):
        self.kb.set("varname4", [1, 2, 3, 4])
        var = self.kb.get("varname4")
        assert var == [1, 2, 3, 4]
        assert isinstance(var, types.ListType)

    def testListWithMultipleTypes(self):
        self.kb.set("varname5", [1, 2, 3.4, "5", [6, 7]])
        var = self.kb.get("varname5")
        assert var == [1, 2, 3.4, "5", [6, 7]]
        assert isinstance(var, types.ListType)

    def testDict(self):
        self.kb.set("varname6", {'a': 123, 'b': 456, 789: "c"})
        var = self.kb.get("varname6")
        assert var == {'a': 123, 'b': 456, 789: "c"}
        assert isinstance(var, types.DictType)

    def testDictWithComplexTypes(self):
        self.kb.set("varname7", {'a': [123.25], 'b': [4, 5, 6], 789: {'a': 1, 'b': 2}})
        var = self.kb.get("varname7")
        assert var == {'a': [123.25], 'b': [4, 5, 6], 789: {'a': 1, 'b': 2}}
        assert isinstance(var, types.DictType)

    def testKeyNotString(self):
        self.assertRaises(KBNameNotString, self.kb.set, 123, "newvalue")

    def testValueNotKnown(self):
        class A:
            pass
        self.assertRaises(KBValueNotKnown, self.kb.set, "varname8", A())

if __name__ == "__main__":
    unittest.main()
