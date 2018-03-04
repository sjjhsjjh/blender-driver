#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test script."""

# Standard library imports, in alphabetic order.
#
# Module for building paths.
# https://docs.python.org/3.5/library/os.path.html
import os.path
#
# Module for extending the search path.
# https://docs.python.org/3.5/library/sys.html
import sys
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
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

if __name__ == '__main__':
    # The next line is carried over from unittest.main().
    verboseMode = ('-v' in sys.argv) or ('--verbose' in sys.argv)
    initialise_logging(verboseMode)
    suites = unittest.defaultTestLoader.discover(
        os.path.join('path_store', 'test'), "*.py")
    results = unittest.TextTestRunner(
        verbosity=(2 if verboseMode else 1)).run(suites)
    sys.exit(len(results.errors) + len(results.failures))
