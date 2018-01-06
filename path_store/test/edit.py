#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestEdit
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

class TestEdit(unittest.TestCase):
    def test_scalar(self):
        principal0 = 4
        def add1(point, path, results):
            return True, 1 + point
        principal = pathstore.walk(principal0, add1)
        self.assertIsNot(principal, principal0)
        self.assertEqual(principal, 5)

    def test_list(self):
        principal0 = [10, 11]
        def add1(point, path, results):
            return True, 1 + point
        with self.assertRaises(TypeError) as context:
            principal = pathstore.walk(principal0, add1, editIterable=True)
        self.assertIsInstance(context.exception, TypeError)
        
        principal0 = [12, 13]
        principal = pathstore.walk(principal0, add1, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 14])
        
        def even_odd(point, path, results):
            if point % 2 == 0:
                return True, point + 9
            else:
                return True, point + 1
        principal = pathstore.walk(principal0, even_odd, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 23])
        principal = pathstore.walk(principal0, even_odd, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 24])

    def test_change_type(self):
        principal0 = [12, {'unlucky': 13}]
        def always_blue(point, path, results):
            return True, "blue"
        principal = pathstore.walk(
            principal0, always_blue, (1,), editIterable=True)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, "blue"])

    def test_tuple(self):
        principal = (20, 21, 22)
        principal0 = principal
        def add_ten(point, path, results):
            return True, 10 + point
        
        expected = (20, 31, 22)
        principal1 = pathstore.walk(principal0, add_ten, 1)
        self.assertEqual(principal1, expected)
        self.assertIs(principal, principal0)
        self.assertIsNot(principal0, principal1)
        
        expected = (30, 31, 32)
        principal1 = pathstore.walk(principal0, add_ten)
        self.assertEqual(principal1, expected)
        self.assertIs(principal, principal0)
        self.assertIsNot(principal0, principal1)
