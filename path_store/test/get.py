#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestGet
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
from path_store.test.principal import Principal
#
# Modules under test.
import pathstore

class TestGet(unittest.TestCase):
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
        expected = IndexError("Couldn't get point for 0 in []")
        with self.assertRaises(type(expected)) as context:
            pathstore.get([], 0)
        self.assertEqual(str(context.exception), str(expected))

    def test_empty_string(self):
        expected = TypeError("Couldn't get point for 0 in {}")
        with self.assertRaises(type(expected)) as context:
            pathstore.get({}, 0)
        self.assertEqual(str(context.exception), str(expected))

    def test_short_list_numeric(self):
        expected = IndexError("Couldn't get point for 2 in ['Blibb', 'Abb']")
        with self.assertRaises(type(expected)) as context:
            pathstore.get(["Blibb", "Abb"], 2)
        self.assertEqual(str(context.exception), str(expected))

    def test_list_string(self):
        parent = ["Blibb", "Abb"]
        expected = TypeError(" ".join((
            "Couldn't", 'get point for "keyZero" in', str(parent))))
        with self.assertRaises(type(expected)) as context:
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
        value = "bee"
        parent = {
            'kaye': "valee", 'kdee': {'kb': value, 'ksee': "sea"}, 'keen':None}
        self.assertIs(pathstore.get(parent, None), parent)
        self.assertIs(pathstore.get(parent, 'kaye'), parent['kaye'])
        expected = TypeError("".join((
            "Couldn't get point for 3 in ", str(parent))))
        with self.assertRaises(type(expected)) as context:
            pathstore.get(parent, 3)
        self.assertEqual(str(context.exception), str(expected))
        self.assertIs(pathstore.get(parent, ('kdee', 'kb')), value)
        self.assertIsNone(pathstore.get(parent, 'keen'))

    def test_list_in_dictionary(self):
        parent = {'kaye': "valee"
                  , 'kdee': {'kb': "bee", 'ksee': "sea"}
                  , 'kale': [23, 45, 67]}
        self.assertIs(pathstore.get(parent, None), parent)
        self.assertIs(pathstore.get(parent, 'kaye'), parent['kaye'])
        expected = TypeError("".join((
            "Couldn't get point for 3 in ", str(parent))))
        with self.assertRaises(type(expected)) as context:
            pathstore.get(parent, 3)
        self.assertEqual(str(context.exception), str(expected))
        self.assertEqual(pathstore.get(parent, ('kale', 2)), 67)

    def test_attr(self):
        value = "bobo"
        parent = Principal(value)
        self.assertIs(pathstore.get(parent, None), parent)
        expected = TypeError(
            "".join(("Couldn't get point for 0 in ", str(parent))))
        with self.assertRaises(type(expected)) as context:
            pathstore.get(parent, 0)
        self.assertEqual(str(context.exception), str(expected))
        self.assertIs(pathstore.get(parent, 'testAttr'), value)
        self.assertEqual(pathstore.get(parent, ('testAttr', 1)), value[1])

    def test_string_index(self):
        parent = "edcba"
        self.assertEqual(pathstore.get(parent, 0), "e")
        self.assertEqual(pathstore.get(parent, 4), "a")
        expected = IndexError("".join((
            "Couldn't get point for 5 in ", parent)))
        with self.assertRaises(type(expected)) as context:
            self.assertEqual(pathstore.get(parent, 5), "a")
        self.assertEqual(str(context.exception), str(expected))
        
    def test_descend_through_none(self):
        parent = [{'ele': "ment"}, None, {'al': "fire"}]
        expected = IndexError(
            " ".join(("Point was None for 1 in", str(parent))))
        with self.assertRaises(type(expected)) as context:
            pathstore.get(parent, (1, 'ele'))
        self.assertEqual(str(context.exception), str(expected))
    
    def test_slice(self):
        parent = [11, 12, 13, 14, 15]
        points = pathstore.get(parent, pathstore.pathify_split("1:"))
        self.assertEqual(points, [12, 13, 14, 15])

        parent0 = {'odd':11, 'even':12, 'sub':[101, 102, 103]}
        parent1 = {'odd':13, 'even':14, 'sub':[201, 202, 203]}
        parent = [
            parent0,
            parent1,
            {'odd':15, 'even':16},
            {'odd':17, 'even':18}
        ]
        points = pathstore.get(parent, pathstore.pathify_split("1:/odd"))
        self.assertEqual(points, [13,15,17])
        points = pathstore.get(parent, pathstore.pathify_split("3:/odd"))
        self.assertEqual(points, [17])
        points = pathstore.get(parent, pathstore.pathify_split("::2/odd"))
        self.assertEqual(points, [11,15])
        points = pathstore.get(parent, pathstore.pathify_split(":2/even"))
        self.assertEqual(points, [12,14])
        points = pathstore.get(parent, pathstore.pathify_split(":2/sub/1"))
        self.assertEqual(points, [102,202])
        points = pathstore.get(parent, pathstore.pathify_split(":2/sub/::2"))
        self.assertEqual(points, [[101,103],[201,203]])
        points = pathstore.get(parent, pathstore.pathify_split("0:2"))
        self.assertEqual(len(points), 2)
        self.assertIs(points[0], parent0)
        self.assertIs(points[1], parent1)
