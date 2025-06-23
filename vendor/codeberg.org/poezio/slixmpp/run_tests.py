#!/usr/bin/env python3

import sys
import logging
import unittest

from argparse import ArgumentParser
from importlib import import_module
from pathlib import Path


def run_tests(filenames=None, debug=False):
    """
    Find and run all tests in the tests/ directory.

    Excludes live tests (tests/live_*).
    """
    if not filenames:
        filenames = [i for i in Path('tests').glob('test_*')]
    else:
        filenames = [Path(i) for i in filenames]

    modules = ['.'.join(test.parts[:-1] + (test.stem,)) for test in filenames]

    suites = []
    for filename in modules:
        module = import_module(filename)
        suites.append(module.suite)

    tests = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner(verbosity=2)

    if debug:
        logging.basicConfig(level='DEBUG')
    else:
        # Disable logging output
        logging.basicConfig(level=100)
        logging.disable(100)

    result = runner.run(tests)
    return result


if __name__ == '__main__':
    parser = ArgumentParser(description='Run unit tests.')
    parser.add_argument('tests', metavar='TEST', nargs='*', help='list of tests to run, or nothing to run them all')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', default=False, help='enable debug output')
    args = parser.parse_args()

    result = run_tests(args.tests, args.debug)
    print("<tests %s ran='%s' errors='%s' fails='%s' success='%s'/>" % (
        "xmlns='http//andyet.net/protocol/tests'",
        result.testsRun, len(result.errors),
        len(result.failures), result.wasSuccessful()))

    sys.exit(not result.wasSuccessful())
