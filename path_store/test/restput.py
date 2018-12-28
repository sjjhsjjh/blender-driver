#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestRestPut
"""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module that facilitates container subclasses.
# https://docs.python.org/3/library/collections.html#collections.UserList
import collections
# Data model reference documentation is also useful:
# https://docs.python.org/3/reference/datamodel.html#emulating-container-types
#
# Module for JavaScript Object Notation (JSON) strings.
# https://docs.python.org/3.5/library/json.html
import json
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Modules under test.
import rest
#
# Modules that will be patched.
import pathstore


class TestRestPut(unittest.TestCase):
    def test_no_path(self):
        restInterface = rest.RestInterface()
        restInterface.rest_put(None)
        self.assertIsNone(restInterface.rest_get())
        restInterface.rest_put(1)
        self.assertEqual(restInterface.rest_get(), 1)
        principal = object()
        restInterface.rest_put(principal)
        self.assertIs(restInterface.rest_get(), principal)

    def test_zero(self):
        restInterface = rest.RestInterface()
        principal = object()
        restInterface.rest_put(principal, [0])
        self.assertEqual(len(restInterface.principal), 1)
        self.assertIs(restInterface.principal[0], principal)
        
        restInterface = rest.RestInterface()
        restInterface.rest_put(2, [0])
        self.assertEqual(restInterface.principal, [2])

    def test_numeric(self):
        restInterface = rest.RestInterface()
        restInterface.rest_put(2, [0,1])
        self.assertEqual(restInterface.principal, [[None, 2]])
        restInterface.rest_put(3, [0,2])
        self.assertEqual(restInterface.principal, [[None, 2, 3]])
        restInterface.rest_put(4, [1])
        self.assertEqual(restInterface.principal, [[None, 2, 3], 4])

        restInterface = rest.RestInterface()
        restInterface.rest_put(['blib', 'blab'])
        restInterface.rest_put('bleb', (1,))
        self.assertEqual(restInterface.principal, ['blib', 'bleb'])
    
    def test_string(self):
        restInterface = rest.RestInterface()
        restInterface.rest_put({'keypie': 'cap'})
        restInterface.rest_put('bleb', 'keypie')
        self.assertEqual(restInterface.principal, {'keypie': 'bleb'})
    
        restInterface = rest.RestInterface()
        restInterface.rest_put("clap", ('piker',))
        restInterface.rest_put("bleb", ['keypit'])
        self.assertEqual(
            restInterface.principal, {'keypit': 'bleb', 'piker':"clap"})

    def test_generic_value(self):
        class Principal:
            pass
        principal = Principal()
        self.assertEqual(rest._generic_value(principal), {})

        principal = Principal()
        principal.testAttr = 'bacon'
        self.assertEqual(rest._generic_value(principal), {})
        
        class CustomList(collections.UserList):
            pass
        self.assertEqual(rest._generic_value(CustomList()), [])

    def test_principal(self):
        restInterface = rest.RestInterface()
        class Principal:
            pass
        principal = Principal()
        principal.testAttr = 'bacon'
        #
        # Next couple of lines show a way to use patch to replace an imported
        # function. First line puts a Mock object in place; second line makes it
        # chain to the original function imported by a different route.
        with unittest.mock.patch('rest.pathstore.replace') as patched:
            patched.side_effect = pathstore.replace
            restInterface.rest_put(principal)
            restInterface.rest_put('pork', ['testAttr'])
        # Now we have a call list that can be printed for debugging, like this:
        # print(patched.call_args_list)
        # Assertions can also be made.
        self.assertEqual(patched.call_count, 4)
        self.assertIs(principal, restInterface.principal)
        self.assertEqual(principal.testAttr, 'pork')
    
    def test_get_generic(self):
        restInterface = rest.RestInterface()
        self.assertIsNone(restInterface.get_generic())
        
        restInterface.rest_put('bleb', 'root')
        self.assertEqual(restInterface.get_generic(), restInterface.principal)

        restInterface.rest_put(2, ['route',1])
        self.assertEqual(restInterface.get_generic(), restInterface.principal)
        
        class Principal:
            pass
        principal = Principal()
        #
        # Attribute that gets changed by rest_put.
        principal.al = 3
        #
        # Attribute that isn't access via the path store, so doesn't feature in
        # the generic.
        principal.rum = 34
        #
        # Attribute that gets changed to a different type, by rest_put.
        principal.hof = None
        #
        # Attribute that is rest_get'd and so is added to the generic, but isn't
        # set by path store.
        gotValue = 'gotten'
        principal.got = gotValue
        
        with self.assertRaises(TypeError) as context:
            asJSON = json.dumps(principal)
        
        restInterface.rest_put(principal, ['mcroute'])
        with self.assertRaises(TypeError) as context:
            asJSON = json.dumps(restInterface.rest_get())
        generic = restInterface.get_generic()
        self.assertNotEqual(generic, restInterface.principal)
        # Generic has an empty dictionary in place of the Principal instance.
        self.assertEqual(generic, {
            'root': "bleb", 'route': [None, 2], 'mcroute': {}})
        
        restInterface.rest_put(9, ['mcroute', 'al'])
        self.assertEqual(restInterface.get_generic(), {
            'root': "bleb", 'route': [None, 2], 'mcroute': {'al': 9}})
        
        gotGot = restInterface.rest_get(['mcroute', 'got'])
        self.assertIs(gotGot, gotValue)

        restInterface.rest_put("busa", ['mcroute', 'hof', 2])
        expectedGeneric = {
            'root': "bleb",
            'route': [None, 2],
            'mcroute': {
                'al': 9, 'hof':[None, None, "busa"], 'got':"gotten"}
        }
        self.assertEqual(restInterface.get_generic(), expectedGeneric)

        principal0 = restInterface.rest_get('mcroute')
        self.assertIs(principal, principal0)
        self.assertEqual(principal0.hof, [None, None, "busa"])

        self.assertEqual(
            json.dumps(restInterface.get_generic(), sort_keys=True)
            , json.dumps(expectedGeneric, sort_keys=True))

    def test_get_generic(self):
        # These have to be the same as the values in the constructor, below.
        dictionaryValues = (
            {'dictIndex': 0, 'alpha':"bravo"},
            {'dictIndex': 1, 'alpha':"delta"})

        class Principal:
            @property
            def index(self):
                return self._index
            @index.setter
            def index(self, index):
                self._index = index
                
            @property
            def currentDictionary(self):
                if self.index is None:
                    return None
                return self._dictionaries[self.index]
            
            def __init__(self):
                # These have to be the same as the values in the tuple, above.
                self._dictionaries = (
                    {'dictIndex': 0, 'alpha':"bravo"},
                    {'dictIndex': 1, 'alpha':"delta"})
                self._index = None

        # Initialise.
        restInterface = rest.RestInterface()
        restInterface.rest_put(Principal())
        restInterface.rest_put(0, 'index')
        #
        # Get an item from the dictionary, which also populates the generic
        # object.
        alpha0 = restInterface.rest_get(('currentDictionary', 'alpha'))
        self.assertEqual(alpha0, dictionaryValues[0]['alpha'])
        #
        # Get the principal dictionary, and the generic version.
        dict0 = restInterface.rest_get('currentDictionary')
        dictGeneric = restInterface.get_generic('currentDictionary')
        self.assertIsNot(dict0, dictGeneric)
        #
        # The generic one only contains items that have been accessed through
        # the rest interface.
        self.assertEqual(dictGeneric, {'alpha':alpha0})

        # Re-initialise.
        restInterface = rest.RestInterface()
        restInterface.rest_put(Principal())
        restInterface.rest_put(0, 'index')
        #
        # Get the dictionary itself, which mustn't later result in a shared
        # reference to the dictionary being put into the generic object.
        dict0 = restInterface.rest_get('currentDictionary')
        #
        # Next line is a naughty extraction of an attribute that isn't public.
        generic = restInterface._generic
        #
        # The generic object should contain None, as a placeholder.
        self.assertIsNone(generic["currentDictionary"])
        #
        # Test the reference hasn't become shared by the actions of the generic
        # object populate code.
        dictGeneric = restInterface.get_generic('currentDictionary')
        self.assertIsNot(dict0, dictGeneric)
        self.assertEqual(dictGeneric, {})
        
        restInterface.rest_put(1, 'index')
        dict1 = restInterface.rest_get('currentDictionary')
        self.assertEqual(dict1, dictionaryValues[1])
        #
        # Dummy gets to load the generic object.
        restInterface.rest_get(('currentDictionary', 'dictIndex'))
        restInterface.rest_get(('currentDictionary', 'alpha'))
        dictGeneric = restInterface.get_generic('currentDictionary')
        self.assertIsNot(dictGeneric, dict0)
        self.assertIsNot(dictGeneric, dict1)
        self.assertEqual(dictGeneric, dict1)
        #
        # Revert the index and test that the generic get now returns the values
        # for index:0. 
        restInterface.rest_put(0, 'index')
        dictGeneric = restInterface.get_generic('currentDictionary')
        self.assertIsNot(dictGeneric, dict0)
        self.assertIsNot(dictGeneric, dict1)
        self.assertEqual(dictGeneric, dict0)

    def test_load(self):
        restInterface = rest.RestInterface()
        restInterface.load_generic({'b':'c', 'd':('e', 'f')}, ('a',))
        self.assertEqual(
            restInterface._generic, {'a': {'b': None, 'd': [None, None]}})
        
        restInterface.rest_patch({'h':(10, 11, 12)}, 'g')
        # The previous line patches in a tuple, but the generic store will have
        # a list, until get_generic is called.
        self.assertEqual(
            restInterface._generic, {
                'a': {'b': None, 'd': [None, None]},
                'g': {'h':[None, None, None]}
            })
