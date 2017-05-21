#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path-store/test.py TestDescend
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

class TestDescend(unittest.TestCase):
    def test_None_None(self):
        value = pathstore.get(None, None)
        self.assertIsNone(value)
    def test_string_None(self):
        parent = "t1 parent"
        value = pathstore.get(parent, None)
        self.assertIs(parent, value)
    def test_None_numeric(self):
        with self.assertRaises(TypeError) as context:
            pathstore.get(None, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in None")
    def test_empty_numeric(self):
        with self.assertRaises(IndexError) as context:
            pathstore.get([], 0)
        self.assertEqual(str(context.exception), "No point for 0 in []")
    def test_empty_string(self):
        with self.assertRaises(TypeError) as context:
            pathstore.get({}, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in {}")
    def test_short_list_numeric(self):
        with self.assertRaises(IndexError) as context:
            pathstore.get(["Blibb", "Abb"], 2)
        self.assertEqual(
            str(context.exception), "No point for 2 in ['Blibb', 'Abb']")
    def test_list_string(self):
        parent = ["Blibb", "Abb"]
        expected = KeyError(" ".join((
            'No point for "keyZero" in', str(parent))))
        with self.assertRaises(KeyError) as context:
            pathstore.get(parent, "keyZero")
        self.assertEqual(str(context.exception), str(expected))
    def test_list_numerics(self):
        parent = ["Blibb", "Abb"]
        with self.subTest(path=0):
            value = pathstore.get(parent, 0)
            self.assertIs(value, parent[0])
        for path in (1, [1]):
            with self.subTest(path=path):
                value = pathstore.get(parent, path)
                self.assertIs(value, parent[1])
    def test_list_in_list(self):
        parent = [0.0, [1.0, 1.1]]
        self.assertEqual(pathstore.get(parent, 0), 0.0)
        self.assertIs(pathstore.get(parent, 1), parent[1])
        self.assertIs(pathstore.get(parent, [1]), parent[1])
        self.assertEqual(pathstore.get(parent, (1, 0)), 1.0)
        with self.assertRaises(TypeError) as context:
            pathstore.get(parent, [0, 0])
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in 0.0")
        with self.assertRaises(TypeError) as context:
            pathstore.get(parent, [0, 1])
        self.assertEqual(
            str(context.exception), "Couldn't get point for 1 in 0.0")
    def test_dictionary_in_dictionary(self):
        parent = {'kaye': "valee", 'kdee': {'kb': "bee", 'ksee': "sea"}}
        self.assertIs(pathstore.get(parent, None), parent)
        self.assertIs(pathstore.get(parent, 'kaye'), parent['kaye'])
        with self.assertRaises(TypeError) as context:
            pathstore.get(parent, 3)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 3 in ", str(parent))))
        self.assertEqual(pathstore.get(parent, ('kdee', 'kb')), "bee")
    def test_list_in_dictionary(self):
        parent = {'kaye': "valee"
                  , 'kdee': {'kb': "bee", 'ksee': "sea"}
                  , 'kale': [23, 45, 67]}
        self.assertIs(pathstore.get(parent, None), parent)
        self.assertIs(pathstore.get(parent, 'kaye'), parent['kaye'])
        with self.assertRaises(TypeError) as context:
            pathstore.get(parent, 3)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 3 in ", str(parent))))
        self.assertEqual(pathstore.get(parent, ('kale', 2)), 67)
    def test_attr(self):
        value = "bobo"
        parent = Principal(value)
        self.assertIs(pathstore.get(parent, None), parent)
        with self.assertRaises(TypeError) as context:
            pathstore.get(parent, 0)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 0 in ", str(parent))))
        self.assertIs(pathstore.get(parent, 'testAttr'), value)
        self.assertEqual(pathstore.get(parent, ('testAttr', 1)), value[1])
