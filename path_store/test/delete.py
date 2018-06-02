#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestDelete
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

class TestDelete(unittest.TestCase):
    def test_list_numerics(self):
        principal0 = "Blibb"
        principal1 = "Abb"
        principal = [principal0, principal1]
        deleted = pathstore.delete(principal, 0)
        self.assertIs(deleted, principal0)
        self.assertIs(principal[0], principal1)
        self.assertEqual(principal, [principal1])
        
    def test_dict_strings(self):
        principalZero = "Blibb"
        principalOne = "Abb"
        principal = {'zero':principalZero, 'one':principalOne}
        deleted = pathstore.delete(principal, 'zero')
        self.assertIs(deleted, principalZero)
        self.assertIs(principal['one'], principalOne)
        self.assertEqual(principal, {'one':principalOne})
        
    def test_attr(self):
        principalZero = "Blibb"
        principalOne = "Abb"
        class Principal(object):
            def __init__(self):
                self.zero = principalZero
                self.one = principalOne
        principal = Principal()
        self.assertIs(principal.zero, principalZero)

        deleted = pathstore.delete(principal, 'zero')
        self.assertIs(deleted, principalZero)
        self.assertIs(principal.one, principalOne)
        with self.assertRaises(AttributeError) as context:
            principal.zero

    def test_error_return(self):
        principalZero = "Blibb"
        principalOne = "Abb"
        principal = {
            'ngDict': {'zero': principalZero, 'one': principalOne},
            'ngList': [None]
        }
        #
        # Delete an array element that isn't there because the array is shorter.
        listError = pathstore.delete(principal, ('ngList', 1))
        with self.assertRaises(IndexError) as listContext:
            pathstore.get(principal, ('ngList', 1))
        self.assertEqual(str(listError), str(listContext.exception))
        #
        # Delete a dictionary element that isn't there.
        dictError = pathstore.delete(principal, ('ngDict', 'two'))
        with self.assertRaises(KeyError) as dictContext:
            pathstore.get(principal, ('ngDict', 'two'))
        self.assertEqual(str(dictError), str(dictContext.exception))
