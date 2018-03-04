#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""\
Path Store unit test module. Tests in this module can be run like:

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
        class Principal:
            testAttr = None
            countedStr = None

        nativePrincipal = Principal()
        nativePrincipal.testAttr = "three"
        nativePrincipal.countedStr = "four"
        #
        # Merging in values is the same as setting natively ...
        principal0 = Principal()
        principal1 = pathstore.merge(
            principal0, {'testAttr': "three", 'countedStr':"four"})
        self.assertIs(principal1, principal0)
        self.assertEqual(nativePrincipal.countedStr, principal1.countedStr)
        self.assertEqual(nativePrincipal.testAttr, principal1.testAttr)
        #
        # ... Unless the merged in names don't exist as properties in the principal.
        # Then it becomes a dictionary.
        principal0 = Principal()
        value = {'notAttr': "five"}
        principal1 = pathstore.merge(principal0, value)
        self.assertIsNot(principal1, principal0)
        self.assertIsInstance(principal1, dict)
        self.assertIsNot(principal1, value)
        self.assertEqual(principal1, value)

    def test_none_into(self):
        # Merging in None to a point that exists in the path store should have
        # no effect.

        principal0 = 3
        principal1 = pathstore.merge(principal0, None)
        self.assertIs(principal0, principal1)
        self.assertEqual(principal0, 3)
        
        principal0 = object()
        principal1 = pathstore.merge(principal0, None)
        self.assertIs(principal0, principal1)
        
        value = (44, 55, 66)
        principal0 = tuple(list(value))
        principal1 = pathstore.merge(principal0, None)
        self.assertIs(principal0, principal1)
        self.assertIsNot(principal0, value)
        self.assertEqual(principal0, value)
        
        value = {'aa':77}
        principal0 = dict(value)
        principal1 = pathstore.merge(principal0, None)
        self.assertIs(principal0, principal1)
        self.assertIsNot(principal0, value)
        self.assertEqual(principal0, value)

        # Merging in None to a point that doesn't exist in the path store should
        # add the path.

        value = [None, 'blib', 88]
        principal0 = value[:]
        principal1 = pathstore.merge(principal0, None, len(value))
        self.assertIs(principal0, principal1)
        self.assertIsNot(principal0, value)
        self.assertEqual(len(principal0), len(value) + 1)
        value.append(None)
        self.assertEqual(principal0, value)

        value = ('some', 'body', None)
        principal0 = value
        principal1 = pathstore.merge(principal0, None, len(value))
        self.assertIsNot(principal0, principal1)
        self.assertIs(principal0, value)
        self.assertIs(type(principal1), type(value))
        self.assertEqual(len(principal1), len(value) + 1)
        self.assertIsNone(principal1[len(value)])
        self.assertEqual(principal1[0:-1], value)

        value = {'aa':77}
        principal0 = dict(value)
        principal1 = pathstore.merge(principal0, None, 'bb')
        self.assertIs(principal0, principal1)
        self.assertIsNot(principal0, value)
        value['bb'] = None
        self.assertEqual(principal0, value)
