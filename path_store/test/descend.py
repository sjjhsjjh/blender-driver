#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestDescend
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
# Modules under test.
import pathstore

class TestDescend(unittest.TestCase):
    def test_None_numeric(self):
        pointType, point, error = pathstore.descend(None, 0)
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, TypeError)
        
    def test_None_string(self):
        pointType, point, error = pathstore.descend(None, 'key1')
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, TypeError)
        
    def test_empty_list_numeric(self):
        pointType, point, error = pathstore.descend([], 0)
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, IndexError)
        
    def test_list_numeric(self):
        pointType, point, error = pathstore.descend(['atfirst'], 0)
        self.assertIs(pointType, pathstore.PointType.LIST)
        self.assertEqual(point, 'atfirst')
        self.assertIsNone(error)

    def test_list_string(self):
        pointType, point, error = pathstore.descend(['atfirst'], 'key1')
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, TypeError)

    def test_missing_dictionary_string(self):
        pointType, point, error = pathstore.descend({}, 'key1')
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, KeyError)

        pointType, point, error = pathstore.descend({'key2': "Valtwo"}, 'key3')
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, KeyError)

    def test_dictionary_string(self):
        pointType, point, error = pathstore.descend({'key1': 8}, 'key1')
        self.assertIs(pointType, pathstore.PointType.DICTIONARY)
        self.assertEqual(point, 8)
        self.assertIsNone(error)

    def test_dictionary_numeric(self):
        # The pathstore _insert() function relies on KeyError only being
        # returned if the parent is a dictionary and the specifier is a string.
        # This test verifies that a numeric specifier applied to a dictionary
        # returns TypeError, not KeyError.
        pointType, point, error = pathstore.descend({'key1': 8}, 0)
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, TypeError)

    def test_dictionary_None(self):
        pointType, point, error = pathstore.descend({'keen': None}, 'keen')
        self.assertIsNone(point)
        self.assertIs(pointType, pathstore.PointType.DICTIONARY)
        self.assertIsNone(error)

    def test_attr_string(self):
        class Principal:
            pass
        parent = Principal()
        parent.testAttr = "one"
        pointType, point, error = pathstore.descend(parent, 'testAttr')
        self.assertIs(pointType, pathstore.PointType.ATTR)
        self.assertEqual(point, "one")
        self.assertIsNone(error)

    def test_attr_none(self):
        class Principal:
            pass
        parent = Principal()
        parent.testAttr = None
        pointType, point, error = pathstore.descend(parent, 'testAttr')
        self.assertIs(pointType, pathstore.PointType.ATTR)
        self.assertIsNone(point)
        self.assertIsNone(error)
        
    def test_attr_string_not_found(self):
        parent = object()
        pointType, point, error = pathstore.descend(parent, 'nonsalad')
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, TypeError)

    def test_specifier_None(self):
        expected = TypeError(
            "Specifier must be string or numeric, but is None.")
        with self.assertRaises(type(expected)) as context:
            pointType, point, error = pathstore.descend([], None)

    def test_string_numeric(self):
        parent = "qwert"
        pointType, point, error = pathstore.descend(parent, 4)
        self.assertIs(pointType, pathstore.PointType.LIST)
        self.assertEqual(point, "t")
        self.assertIsNone(error)

        pointType, point, error = pathstore.descend(parent, 5)
        self.assertIsNone(pointType)
        self.assertIsNone(point)
        self.assertIsInstance(error, IndexError)
