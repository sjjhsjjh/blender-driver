#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestDescendOne
"""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Utilities.
from .principal import Principal
#
# Modules under test.
import pathstore

class TestDescendOne(unittest.TestCase):
    def test_None_numeric(self):
        point, numeric, pointType = pathstore.descend(None, 0)
        self.assertIsNone(point)
        self.assertTrue(numeric)
        self.assertIsNone(pointType)
    def test_None_string(self):
        point, numeric, pointType = pathstore.descend(None, 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertIsNone(pointType)
    def test_empty_list_numeric(self):
        point, numeric, pointType = pathstore.descend([], 0)
        self.assertIsNone(point)
        self.assertTrue(numeric)
        self.assertEqual(pointType, pathstore.PointType.LIST)
    def test_list_numeric(self):
        point, numeric, pointType = pathstore.descend(['atfirst'], 0)
        self.assertEqual(point, 'atfirst')
        self.assertTrue(numeric)
        self.assertEqual(pointType, pathstore.PointType.LIST)
    def test_list_string(self):
        point, numeric, pointType = pathstore.descend(['atfirst'], 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_empty_dictionary_string(self):
        point, numeric, pointType = pathstore.descend({}, 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_dictionary_string(self):
        point, numeric, pointType = pathstore.descend({'key1': 8}, 'key1')
        self.assertEqual(point, 8)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_attr_string(self):
        parent = Principal("one")
        point, numeric, pointType = pathstore.descend(parent, 'testAttr')
        self.assertEqual(point, "one")
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.ATTR)
    def test_attr_string_not_found(self):
        parent = Principal("one")
        point, numeric, pointType = pathstore.descend(parent, 'nonsalad')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertIsNone(pointType)
