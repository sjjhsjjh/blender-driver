#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit tests."""

# Standard library imports, in alphabetic order.
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
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
#
# Above should be done with .discover() but I couldn't get it to work.

if __name__ == '__main__':
    unittest.main()