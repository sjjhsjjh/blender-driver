#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit tests."""

# Standard library imports, in alphabetic order.
#
# Module for file and directory paths, which is only used to build an import
# path.
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
#
# Unit test tests.
from test.principal import TestPrincipal
#
# Unit test modules.
from test.strquote import TestStrQuote
from test.pathify import TestPathify
from test.descendone import TestDescendOne
from test.descend import TestDescend
from test.makepoint import TestMakePoint
from test.insert import TestInsert
from test.merge import TestMerge
from test.restput import TestRestPut
from test.pointmaker import TestPointMaker
from test.hostedproperty import TestHostedProperty
from test.interceptproperty import TestInterceptProperty
from test.edit import TestEdit
#
# Above should be done with .discover() but I couldn't get it to work.

if __name__ == '__main__':
    # The next line isn't proper but I couldn't find another way to detect that
    # tests are being run in verbose mode.
    initialise_logging(('-v' in sys.argv) or ('--verbose' in sys.argv))
    unittest.main()
