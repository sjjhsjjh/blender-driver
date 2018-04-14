#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test script."""

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3/library/argparse.html
import argparse
#
# Module for building paths.
# https://docs.python.org/3/library/os.path.html
import os.path
#
# Module for extending the search path.
# https://docs.python.org/3/library/sys.html
import sys
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
import unittest
#
# Local imports.
#
# But first, add the Blender Driver directory to sys.path so that the logging
# utilities module can be imported.
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
#
# Local module for setting up Python logging.
from blender_driver.loggingutils import initialise_logging

def discoverTests(specification):
    discoveredSuites = unittest.defaultTestLoader.discover(
        os.path.join('path_store', 'test'), "*.py")
    if specification is None or len(specification) <= 0:
        return discoveredSuites

    # Couldn't see any way to remove tests from a TestSuite. The following code
    # creates a new empty suite and then adds only the tests that match the
    # specification.
    suites = unittest.TestSuite()
    for suite in discoveredSuites:
        for test in suite:
            for case in test:
                className = case.__class__.__name__
                if className in specification:
                    suites.addTest(case)
    return suites

if __name__ == '__main__':
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument(
        '-v', '--verbose', action='store_true', help="Verbose output.")
    argumentParser.add_argument(
        'tests', nargs='*', type=str, help=
        "Tests to run. Default is to run all.")
    arguments = argumentParser.parse_args()

    initialise_logging(arguments.verbose)
        
    results = unittest.TextTestRunner(
        verbosity=(2 if arguments.verbose else 1)
        ).run(discoverTests(arguments.tests))
    sys.exit(len(results.errors) + len(results.failures))
