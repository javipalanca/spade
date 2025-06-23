import os
import re
import sys
import unittest
import compileall


class TestOverall(unittest.TestCase):

    """
    Test overall package health by compiling and checking
    code style.
    """

    def testModules(self):
        """Testing all modules by compiling them"""
        src = '.%sslixmpp' % os.sep
        rx = re.compile('/[.]svn|.*26.*')
        self.assertTrue(compileall.compile_dir(src, rx=rx, quiet=True))


suite = unittest.TestLoader().loadTestsFromTestCase(TestOverall)
