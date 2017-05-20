#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path-store/test.py TestStrQuote
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

class TestStrQuote(unittest.TestCase):
    def test_None(self):
        self.assertEqual(pathstore.str_quote(None), "None")
    def test_str(self):
        self.assertEqual(pathstore.str_quote("blib"), '"blib"')
    def test_number(self):
        self.assertEqual(pathstore.str_quote(2), "2")
    def test_dict(self):
        dict_ = {'alp':"bet", 'pla':2}
        self.assertEqual(pathstore.str_quote(dict), str(dict))
