#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path-store/test.py TestMerge
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
        # print()
        # principal = pathstore.insert(principal0, path, value
        #                              , logger=pathstore.default_logger_print)
        principal = pathstore.insert(principal0, path, value)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, principal1)
        # print(principal)
