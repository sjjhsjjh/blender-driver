#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
        principal.al = 3
        principal.rum = 34
        principal.hof = None
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

        restInterface.rest_put("busa", ['mcroute', 'hof', 2])
        expectedGeneric = {
            'root': "bleb",
            'route': [None, 2],
            'mcroute': {
                'al': 9, 'hof':[None, None, "busa"]}
        }
        self.assertEqual(restInterface.get_generic(), expectedGeneric)

        principal0 = restInterface.rest_get('mcroute')
        self.assertIs(principal, principal0)
        self.assertEqual(principal0.hof, [None, None, "busa"])

        self.assertEqual(
            json.dumps(restInterface.get_generic()), json.dumps(expectedGeneric))
