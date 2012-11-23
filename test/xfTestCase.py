# -*- coding: utf-8 -*-
import os
import sys
import unittest

from spade.pyxf import *


class xfTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEclipse(self):
        try:
            e = eclipse()
        except ECLiPSeExecutableNotFound:
            self.skipTest('ECLiPSe Prolog executable not found on the specified path.')

        e.load('test/logic/test_eclipse')
        assert e.query('dislikes( john, mushrooms )') is True
        for result in e.query('likes( Person, Food )'):
            assert result in [{'Food': 'curry', 'Person': 'john'}, {'Food': 'mushrooms', 'Person': 'sandy'}]
        del e

    def testFlora2(self):
        try:
            f = flora2()
        except Flora2ExecutableNotFound:
            self.skipTest('Flora-2 executable not found on the specified path. Try installing flora2')

        f.load('test/logic/test_flora')
        assert f.query('john[ dislikes->mushrooms ]') is True
        for result in f.query('?person[ likes->?food ]'):
            assert result in [{'food': 'curry', 'person': 'john'}, {'food': 'mushrooms', 'person': 'sandy'}]
        del f

    def testSWI(self):
        try:
            s = swipl()
        except SWIExecutableNotFound:
            self.skipTest('SWI-Prolog executable not found on the specified path. Try installing swi-prolog.')

        s.load('test/logic/test_swi')
        assert s.query('dislikes( john, mushrooms )') is True
        for result in s.query('likes( Person, Food )'):
            assert result in [{'Food': 'curry', 'Person': 'john'}, {'Food': 'mushrooms', 'Person': 'sandy'}]
        del s

    def testXSB(self):
        try:
            x = xsb()
        except XSBExecutableNotFound:
            self.skipTest('XSB executable not found on the specified path. Try installing xsb')

        x.load('test/logic/test_xsb')
        assert x.query('dislikes( john, mushrooms )') is True
        for result in x.query('likes( Person, Food )'):
            assert result in [{'Food': 'curry', 'Person': 'john'}, {'Food': 'mushrooms', 'Person': 'sandy'}]
        del x


if __name__ == "__main__":
    unittest.main()
