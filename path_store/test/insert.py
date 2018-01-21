#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestInsert
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
from path_store.test.principal import Principal, SetCounterDict, SetCounterList
#
# Modules under test.
import pathstore

class TestInsert(unittest.TestCase):
    def test_empty(self):
        point0 = None
        value = "mt"
        point1 = pathstore.merge(point0, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, value)
        
        point0 = "full"
        point1 = pathstore.merge(point0, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, value)
        
        point1 = pathstore.merge(point0, value, [])
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, value)

    
    def test_zero(self):
        path = [0]
        value = "blob"

        point0 = None
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = []
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = [None]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = ["ma"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

    def test_one(self):
        path = [1]
        value = "blob"
        
        point0 = None
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])

        point0 = []
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = [None, None]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = ["ma"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob"])

        point0 = ["ma", "mo"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob"])

        point0 = ["ma", "mo", "mi"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob", "mi"])

        point0 = ["ma", None, "mi"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob", "mi"])

        point0 = ("ba",)
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, ("ba", "blob"))
       
        point0 = {'car': "veh"}
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = {'tooky':0, 'wonkey': "babb"}
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])

        point0 = "Stringiness"
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])
    
    def test_insert_None(self):
        path = [1]

        point0 = [None, "goner"]
        point1 = pathstore.merge(point0, None, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "goner"])
        
    def test_zero_one(self):
        path = [0, 1]
        value = "Inner"

        point0 = ["Outer String"]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])

        point0 = [{'hand':"yy"}]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0 = [[]]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0_0 = []
        point0 = [point0_0]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertIs(point1[0], point0_0)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0_0 = ["Another"]
        point0 = [point0_0]
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertIs(point1[0], point0_0)
        self.assertIs(pathstore.get(point0, 0), point0_0)
        self.assertEqual(point1, [["Another", "Inner"]])

    def test_string(self):
        path = "blib"
        value = "blob"
        
        point0 = None
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = 5
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = None
        point1 = pathstore.merge(point0, value, [path])
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {}
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = []
        point1 = pathstore.merge(point0, value, path)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {'blib': "bleb"}
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {'blyb': "bleb"}
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob", 'blyb': "bleb"})
        
        point0 = {'blib': "bleb", 'blil': ["bib", "bab"]}
        point1 = pathstore.merge(point0, value, path)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob", 'blil': ["bib", "bab"]})
    
    def test_principal_root(self):
        point0 = Principal()
        path = ('testAttr', "flim", 3, "flam")
        point1 = pathstore.merge(point0, 4, path)
        self.assertIs(point1, point0)
        self.assertIsInstance(point1, Principal)
        self.assertEqual(point1.testAttr
                         , {'flim':[None, None, None, {'flam':4}]})

        point1 = pathstore.merge(point0, 5)
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, 5)
        #
        # Default point maker replaces Principal at root.
        point1 = pathstore.merge(point0, 1, ('notAttr', "flim"))
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, {'notAttr':{'flim':1}})
        
    def test_principal_leaf(self):
        point0 = None
        path = ('de', 'fgh', 'ij', 'kl')
        value = Principal()
        point1 = pathstore.merge(point0, value, path)
        self.assertEqual(point1, {'de':{'fgh':{'ij':{'kl': value}}}})

    def test_setter_optimisation_attr(self):
        principal = Principal()
        self.assertEqual(principal.setterCount, 0)
        principal1 = pathstore.merge(principal, "valley", 'countedStr')
        self.assertIs(principal, principal1)
        self.assertEqual(principal.countedStr, "valley")
        self.assertEqual(principal.setterCount, 1)
        value = "rift"
        principal1 = pathstore.merge(principal, value, 'countedStr')
        self.assertIs(principal, principal1)
        self.assertIs(principal.countedStr, value)
        self.assertEqual(principal.setterCount, 2)
        principal1 = pathstore.merge(principal, value, 'countedStr')
        self.assertIs(principal, principal1)
        self.assertIs(principal.countedStr, value)
        self.assertEqual(principal.setterCount, 2)
        
    def test_setter_optimisation_dict(self):
        principal = SetCounterDict()
        self.assertEqual(principal.setterCount, 0)
        key = 'keen'
        principal1 = pathstore.merge(principal, "valley", key)
        self.assertIs(principal, principal1)
        self.assertEqual(principal[key], "valley")
        self.assertEqual(principal.setterCount, 1)

        value = "rift"
        principal1 = pathstore.merge(principal, value, key)
        self.assertIs(principal, principal1)
        self.assertIs(principal[key], value)
        self.assertEqual(principal.setterCount, 2)
        self.assertIs(principal, principal1)
        principal1 = pathstore.merge(principal, value, key)
        self.assertIs(principal[key], value)
        self.assertEqual(principal.setterCount, 2)
        
    def test_setter_optimisation_list(self):
        principal = SetCounterList()
        self.assertEqual(principal.setterCount, 0)
        principal1 = pathstore.merge(principal, "valley", 0)
        self.assertIs(principal, principal1)
        self.assertEqual(principal, ["valley"])
        self.assertEqual(principal.setterCount, 1)
        value = "rift"
        principal1 = pathstore.merge(principal, value, 1)
        self.assertIs(principal, principal1)
        self.assertIs(principal[1], value)
        self.assertEqual(principal.setterCount, 2)
        self.assertEqual(principal, ["valley", value])
        principal1 = pathstore.merge(principal, value, 1)
        self.assertIs(principal, principal1)
        self.assertIs(principal[1], value)
        self.assertEqual(principal.setterCount, 2)
        
