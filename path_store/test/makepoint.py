#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestMakePoint
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
from path_store.test.principal import Principal
#
# Modules under test.
import pathstore

class TestMakePoint(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(pathstore.make_point(0), [None])
        point0 = []
        point1 = pathstore.make_point(0, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point0, [None])
        point0 = ["ma"]
        point1 = pathstore.make_point(0, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point0, ["ma"])

    def test_one(self):
        self.assertEqual(pathstore.make_point(1), [None, None])
        point0 = []
        point1 = pathstore.make_point(1, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point0, [None, None])
        point0 = ["ma"]
        point1 = pathstore.make_point(1, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point0, ["ma", None])
        point0 = ("ba",)
        point1 = pathstore.make_point(1, point0)
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, ("ba", None))
        point0 = {'car': "veh"}
        point1 = pathstore.make_point(1, point0)
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, [None, None])

    def test_string(self):
        specifier = 'memzero'

        point1 = pathstore.make_point(specifier)
        point1[specifier] = None
        self.assertEqual(point1, {specifier: None})

        point0 = {}
        point1 = pathstore.make_point(specifier, point0)
        point1[specifier] = None
        self.assertIs(point1, point0)
        self.assertEqual(point0, {specifier: None})

        point0 = {specifier: "Member Zero"}
        point1 = pathstore.make_point(specifier, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point1, {specifier: "Member Zero"})

        point0 = ()
        point1 = pathstore.make_point(specifier, point0)
        point1[specifier] = None
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, {specifier: None})

    def test_attr(self):
        principal = Principal()
        point = pathstore.make_point('testAttr', principal)
        self.assertIs(point, principal)

        point = pathstore.make_point('wrongAttr', principal)
        self.assertIsNot(point, principal)
        self.assertEqual(point, {})
    
    def test_none(self):
        point1 = pathstore.make_point(None)
        self.assertIsNone(point1)
        
        point0 = object()
        point1 = pathstore.make_point(None, point0)
        self.assertIs(point0, point1)
