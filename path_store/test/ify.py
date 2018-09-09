#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestPathify TestIterify
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
# Module under test.
import pathstore

class TestPathify(unittest.TestCase):
    def test_None(self):
        self.assertEqual(list(pathstore.pathify(None)), [])
    def test_list_None(self):
        self.assertEqual(list(pathstore.pathify((None,))), [None])
    def test_one_number(self):
        self.assertEqual(list(pathstore.pathify(1)), [1])
    def test_one_string(self):
        self.assertEqual(list(pathstore.pathify("jio")), ["jio"])
    def test_string_number(self):
        self.assertEqual(
            list(pathstore.pathify(("jio", 2))), ["jio", 2])

class TestPathifySplit(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(list(pathstore.pathify_split(None)), [])
        self.assertEqual(list(pathstore.pathify_split("")), [])
        self.assertEqual(list(pathstore.pathify_split("/")), [])
        self.assertEqual(list(pathstore.pathify_split("//")), [])
        self.assertEqual(list(pathstore.pathify_split("//full/")), ["full"])
    def test_skip(self):
        self.assertEqual(list(pathstore.pathify_split("1/2", skip=1)), [2])
    def test_one_number(self):
        self.assertEqual(list(pathstore.pathify_split("1")), [1])
        self.assertEqual(list(pathstore.pathify_split("/1")), [1])
        self.assertEqual(list(pathstore.pathify_split("1/")), [1])
    def test_one_string(self):
        self.assertEqual(list(pathstore.pathify_split("jio")), ["jio"])
        self.assertEqual(list(pathstore.pathify_split("jio/")), ["jio"])
        self.assertEqual(list(pathstore.pathify_split("/jio")), ["jio"])
    def test_string_number(self):
        self.assertEqual(
            list(pathstore.pathify_split(("jio/2"))), ["jio", 2])
    def test_strings_numbers(self):
        self.assertEqual(
            list(pathstore.pathify_split(("jio/2/bo/4"))), ["jio", 2, "bo", 4])
        self.assertEqual(
            list(pathstore.pathify_split(("5/6/7/8"))), [5,6,7,8])
        self.assertEqual(
            list(pathstore.pathify_split(("5/6/7/8o"))), [5,6,7,"8o"])
        self.assertEqual(
            list(pathstore.pathify_split(("a/bb/cc/d"))), ["a","bb","cc","d"])
    def test_slice(self):
        self.assertEqual(
            list(pathstore.pathify_split(("jio/2:")))
            , ["jio", slice(2,None,None)])
        self.assertEqual(
            list(pathstore.pathify_split((":3/2:"))),
            [slice(None,3,None), slice(2,None)])
        self.assertEqual(
            list(pathstore.pathify_split(("3:2:1/:3/2:"))),
            [slice(3,2,1), slice(None,3,None), slice(2,None)])

class TestIterify(unittest.TestCase):
    def test_int(self):
        with self.assertRaises(TypeError) as testContext:
            iterified = pathstore.iterify(2)
        with self.assertRaises(TypeError) as harnessContext:
            enumerator = enumerate(2)
        self.assertEqual(str(testContext.exception)
                         , str(harnessContext.exception))

    def test_principal(self):
        class Principal:
            pass
        principal = Principal()
        principal.att = 'ribu'
        self.assertFalse(hasattr(principal, 'items'))
        with self.assertRaises(TypeError) as harnessContext:
            enumerator = enumerate(principal)
        with self.assertRaises(TypeError) as testContext:
            iterified = pathstore.iterify(principal)
        self.assertEqual(str(testContext.exception)
                         , str(harnessContext.exception))
    def test_str(self):
        with self.assertRaises(TypeError) as context:
            iterified = pathstore.iterify("An string.")
        self.assertEqual(str(TypeError()), str(context.exception))
    
    def test_ok(self):
        list_ = ['bif', 2, 2, None]
        type, iterator = pathstore.iterify(list_)
        self.assertEqual(tuple(enumerate(list_)), tuple(iterator))
        self.assertEqual(type, pathstore.PointType.LIST)

        dict_ = {'pag':1, 'pog':1, 'pygi':None, 'pli':list_}
        type, iterator = pathstore.iterify(dict_)
        self.assertEqual(tuple(dict_.items()), tuple(iterator))
        self.assertEqual(type, pathstore.PointType.DICTIONARY)
