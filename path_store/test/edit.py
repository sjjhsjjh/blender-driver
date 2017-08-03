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
        def add1(parent):
            return parent, parent + 1
        principal = pathstore.edit(principal0, add1)
        self.assertIsNot(principal, principal0)
        self.assertEqual(principal, 5)

    def test_list(self):
        principal0 = [10, 11]
        def add1(parent):
            return parent, 1 + parent
        with self.assertRaises(TypeError) as context:
            principal = pathstore.edit(principal0, add1)
        self.assertIsInstance(context.exception, TypeError)
        
        principal0 = [12, 13]
        principal = pathstore.edit(principal0, add1, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 14])
        
        def even_odd(parent):
            if parent % 2 == 0:
                return parent, parent + 9
            else:
                return parent, parent + 1
        principal = pathstore.edit(principal0, even_odd, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 23])
        principal = pathstore.edit(principal0, even_odd, 1)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, 24])

    def test_change_type(self):
        principal0 = [12, {'unlucky': 13}]
        def always_blue(parent):
            return parent, "blue"
        principal = pathstore.edit(principal0, always_blue, (1,))
        self.assertIs(principal, principal0)
        self.assertEqual(principal, [12, "blue"])
