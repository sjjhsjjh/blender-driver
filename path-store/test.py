#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit tests."""
# Exit if run other than as a module.

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
import rest

class Principal(object):
    def __init__(self, value=None):
        self.salad = value

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

class TestDescendOne(unittest.TestCase):
    def test_None_numeric(self):
        point, numeric, pointType = pathstore.descend_one(None, 0)
        self.assertIsNone(point)
        self.assertTrue(numeric)
        self.assertIsNone(pointType)
    def test_None_string(self):
        point, numeric, pointType = pathstore.descend_one(None, 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertIsNone(pointType)
    def test_empty_list_numeric(self):
        point, numeric, pointType = pathstore.descend_one([], 0)
        self.assertIsNone(point)
        self.assertTrue(numeric)
        self.assertEqual(pointType, pathstore.PointType.LIST)
    def test_list_numeric(self):
        point, numeric, pointType = pathstore.descend_one(['atfirst'], 0)
        self.assertEqual(point, 'atfirst')
        self.assertTrue(numeric)
        self.assertEqual(pointType, pathstore.PointType.LIST)
    def test_list_string(self):
        point, numeric, pointType = pathstore.descend_one(['atfirst'], 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_empty_dictionary_string(self):
        point, numeric, pointType = pathstore.descend_one({}, 'key1')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_dictionary_string(self):
        point, numeric, pointType = pathstore.descend_one({'key1': 8}, 'key1')
        self.assertEqual(point, 8)
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.DICTIONARY)
    def test_attr_string(self):
        parent = Principal("one")
        point, numeric, pointType = pathstore.descend_one(parent, 'salad')
        self.assertEqual(point, "one")
        self.assertFalse(numeric)
        self.assertEqual(pointType, pathstore.PointType.ATTR)
    def test_attr_string_not_found(self):
        parent = Principal("one")
        point, numeric, pointType = pathstore.descend_one(parent, 'nonsalad')
        self.assertIsNone(point)
        self.assertFalse(numeric)
        self.assertIsNone(pointType)

class TestDescend(unittest.TestCase):
    def test_None_None(self):
        value = pathstore.descend(None, None)
        self.assertIsNone(value)
    def test_string_None(self):
        parent = "t1 parent"
        value = pathstore.descend(parent, None)
        self.assertIs(parent, value)
    def test_None_numeric(self):
        with self.assertRaises(TypeError) as context:
            pathstore.descend(None, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in None")
    def test_empty_numeric(self):
        with self.assertRaises(IndexError) as context:
            pathstore.descend([], 0)
        self.assertEqual(str(context.exception), "No point for 0 in []")
    def test_empty_string(self):
        with self.assertRaises(TypeError) as context:
            pathstore.descend({}, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in {}")
    def test_short_list_numeric(self):
        with self.assertRaises(IndexError) as context:
            pathstore.descend(["Blibb", "Abb"], 2)
        self.assertEqual(
            str(context.exception), "No point for 2 in ['Blibb', 'Abb']")
    def test_list_string(self):
        parent = ["Blibb", "Abb"]
        expected = KeyError(" ".join((
            'No point for "keyZero" in', str(parent))))
        with self.assertRaises(KeyError) as context:
            pathstore.descend(parent, "keyZero")
        self.assertEqual(str(context.exception), str(expected))
    def test_list_numerics(self):
        parent = ["Blibb", "Abb"]
        with self.subTest(path=0):
            value = pathstore.descend(parent, 0)
            self.assertIs(value, parent[0])
        for path in (1, [1]):
            with self.subTest(path=path):
                value = pathstore.descend(parent, path)
                self.assertIs(value, parent[1])
    def test_list_in_list(self):
        parent = [0.0, [1.0, 1.1]]
        self.assertEqual(pathstore.descend(parent, 0), 0.0)
        self.assertIs(pathstore.descend(parent, 1), parent[1])
        self.assertIs(pathstore.descend(parent, [1]), parent[1])
        self.assertEqual(pathstore.descend(parent, (1, 0)), 1.0)
        with self.assertRaises(TypeError) as context:
            pathstore.descend(parent, [0, 0])
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in 0.0")
        with self.assertRaises(TypeError) as context:
            pathstore.descend(parent, [0, 1])
        self.assertEqual(
            str(context.exception), "Couldn't get point for 1 in 0.0")
    def test_dictionary_in_dictionary(self):
        parent = {'kaye': "valee", 'kdee': {'kb': "bee", 'ksee': "sea"}}
        self.assertIs(pathstore.descend(parent, None), parent)
        self.assertIs(pathstore.descend(parent, 'kaye'), parent['kaye'])
        with self.assertRaises(TypeError) as context:
            pathstore.descend(parent, 3)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 3 in ", str(parent))))
        self.assertEqual(pathstore.descend(parent, ('kdee', 'kb')), "bee")
    def test_list_in_dictionary(self):
        parent = {'kaye': "valee"
                  , 'kdee': {'kb': "bee", 'ksee': "sea"}
                  , 'kale': [23, 45, 67]}
        self.assertIs(pathstore.descend(parent, None), parent)
        self.assertIs(pathstore.descend(parent, 'kaye'), parent['kaye'])
        with self.assertRaises(TypeError) as context:
            pathstore.descend(parent, 3)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 3 in ", str(parent))))
        self.assertEqual(pathstore.descend(parent, ('kale', 2)), 67)
    def test_attr(self):
        value = "bobo"
        parent = Principal(value)
        self.assertIs(pathstore.descend(parent, None), parent)
        with self.assertRaises(TypeError) as context:
            pathstore.descend(parent, 0)
        self.assertEqual(
            str(context.exception)
            , "".join(("Couldn't get point for 0 in ", str(parent))))
        self.assertIs(pathstore.descend(parent, 'salad'), value)
        self.assertEqual(pathstore.descend(parent, ('salad', 1)), value[1])

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
        self.assertEqual(pathstore.make_point(specifier), {specifier: None})
        point0 = {}
        point1 = pathstore.make_point(specifier, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point0, {specifier: None})
        point0 = {specifier: "Member Zero"}
        point1 = pathstore.make_point(specifier, point0)
        self.assertIs(point1, point0)
        self.assertEqual(point1, {specifier: "Member Zero"})
        point0 = ()
        point1 = pathstore.make_point(specifier, point0)
        self.assertIsNot(point1, point0)
        self.assertEqual(point1, {specifier: None})

class TestInsert(unittest.TestCase):
    def test_zero(self):
        path = [0]
        value = "blob"

        point0 = None
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = []
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = [None]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

        point0 = ["ma"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["blob"])

    def test_one(self):
        path = [1]
        value = "blob"
        
        point0 = None
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])

        point0 = []
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = [None, None]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = ["ma"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob"])

        point0 = ["ma", "mo"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob"])

        point0 = ["ma", "mo", "mi"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob", "mi"])

        point0 = ["ma", None, "mi"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, ["ma", "blob", "mi"])

        point0 = ("ba",)
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, ("ba", "blob"))
       
        point0 = {'car': "veh"}
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])
        
        point0 = {'tooky':0, 'wonkey': "babb"}
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])

        point0 = "Stringiness"
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, [None, "blob"])
    
    def test_insert_None(self):
        path = [1]

        point0 = [None, "goner"]
        point1 = pathstore.insert(point0, path, None)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [None, "goner"])
        
    def test_zero_one(self):
        path = [0, 1]
        value = "Inner"

        point0 = ["Outer String"]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])

        point0 = [{'hand':"yy"}]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0 = [[]]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0_0 = []
        point0 = [point0_0]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertIs(point1[0], point0_0)
        self.assertEqual(point1, [[None, "Inner"]])
        
        point0_0 = ["Another"]
        point0 = [point0_0]
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertIs(point1[0], point0_0)
        self.assertIs(pathstore.descend(point0, 0), point0_0)
        self.assertEqual(point1, [["Another", "Inner"]])

    def test_string(self):
        path = "blib"
        value = "blob"
        
        point0 = None
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = 5
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = None
        point1 = pathstore.insert(point0, [path], value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {}
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = []
        point1 = pathstore.insert(point0, path, value)
        self.assertIsNot(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {'blib': "bleb"}
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob"})
        
        point0 = {'blyb': "bleb"}
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob", 'blyb': "bleb"})
        
        point0 = {'blib': "bleb", 'blil': ["bib", "bab"]}
        point1 = pathstore.insert(point0, path, value)
        self.assertIs(point0, point1)
        self.assertEqual(point1, {'blib': "blob", 'blil': ["bib", "bab"]})

class TestMerge(unittest.TestCase):
    def test_list_dict(self):
        principal0 = [
            {'a':"ava", 'b':"beaver"},
            {'c':"Cival", 'd':"devalue"}
        ]
        path = [1]
        value = {'d':"nudie", 'e':"evaluate"}
        principal1 = [
            {'a':"ava", 'b':"beaver"},
            {'c':"Cival", 'd':"nudie", 'e':"evaluate"}
        ]
        # print()
        # principal = pathstore.insert(principal0, path, value
        #                              , logger=pathstore.default_logger_print)
        principal = pathstore.insert(principal0, path, value)
        self.assertIs(principal, principal0)
        self.assertEqual(principal, principal1)
        # print(principal)


class TestRestPut(unittest.TestCase):
    def test_no_path(self):
        restInterface = rest.RestInterface()
        restInterface.rest_put(None)
        self.assertIsNone(restInterface.rest_get())
        restInterface.rest_put(1)
        self.assertEqual(restInterface.rest_get(), 1)
        principal = Principal("one")
        restInterface.rest_put(principal)
        self.assertIs(restInterface.rest_get(), principal)
      
# restInterface.rest_put(Principal("two"), [0])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "4"))
# restInterface = RestInterface()
# restInterface.rest_put(2, [0])
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "2"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(2, [0,1])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put(3, [0,2])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "3"))
# restInterface.rest_put(4, [1])
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "3"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(['blib', 'blab'])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put('bleb', (1,))
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "4"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put({'keypie': 'cap'})
# print(subTest, restInterface.rest_get())
# restInterface.rest_put('bleb', 'keypie')
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "5"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(Principal('bacon'))
# print(subTest, vars(restInterface.rest_get()))
# subTest = ".".join((test, "2"))
# restInterface.rest_put('pork', ['salad'])
# print(subTest, vars(restInterface.rest_get()))
# print()
# 
# test = "6"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put('clap', ('piker',))
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put('bleb', ['keypit'])
# print(subTest, restInterface.rest_get())
# print()

# To Do:
# -   Test with principal that has setters, and do the optimise ToDo in
#     pathstore.py file.

if __name__ == '__main__':
    unittest.main()