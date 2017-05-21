#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestMerge
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

class TestMerge(unittest.TestCase):
    def test_into_none(self):
        value = {'kiki':"valoo", 'ikik':"valet"}
        parent = pathstore.merge(None, value)
        self.assertEqual(parent, value)
        self.assertIsNot(parent, value)
    
    def test_list_dict(self):
        principal0 = [
            {'ak':"ava", 'bk':"beaver"},
            {'ck':"Cival", 'dk':"devalue"}
        ]
        path = [1]
        value = {'dk':"nudie", 'ek':"evaluate"}
        principal1 = [
            {'ak':"ava", 'bk':"beaver"},
            {'ck':"Cival", 'dk':"nudie", 'ek':"evaluate"}
        ]
        principal = pathstore.merge(principal0, value, path)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, principal1)

    def test_into_principal(self):
        nativePrincipal = Principal("three")
        nativePrincipal.countedStr = "four"
        principal0 = Principal()
        principal1 = pathstore.merge(
            principal0, {'testAttr': "three", 'countedStr':"four"})
        self.assertIs(principal1, principal0)
        self.assertEqual(nativePrincipal.countedStr, principal1.countedStr)
        self.assertEqual(nativePrincipal.testAttr, principal1.testAttr)
