#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path-store/test.py TestPathify
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
