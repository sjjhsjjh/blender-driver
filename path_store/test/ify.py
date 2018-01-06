#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
