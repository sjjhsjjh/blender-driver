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
import pathstore
import rest

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
        self.assertEqual(restInterface.principal
                         , {'keypit': 'bleb', 'piker':"clap"})

    def test_principal(self):
        restInterface = rest.RestInterface()
        class Principal:
            pass
        principal = Principal()
        principal.testAttr = 'bacon'
        restInterface.rest_put(principal)
        restInterface.rest_put('pork', ['testAttr'])
        self.assertEqual(principal.testAttr, 'pork')
        
    def test_track(self):
        restInterface = rest.RestInterface()
        self.assertEqual(restInterface.track, {})
        
        restInterface.rest_put('bleb', 'root')
        self.assertEqual(restInterface.track, restInterface.principal)
        # self.assertEqual(restInterface.track, {'root': None})

        restInterface.rest_put(2, ['route',1])
        self.assertEqual(restInterface.track, restInterface.principal)
        # self.assertEqual(restInterface.track
        #                  , {'root': None, 'route': [None, None]})
        
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
        self.assertEqual(restInterface.track
                         , {'root': None,
                            'route': [None, None],
                            'mcroute':None})
        
        restInterface.rest_put(9, ['mcroute', 'al'])
        self.assertEqual(restInterface.track
                         , {'root': None,
                            'route': [None, None],
                            'mcroute':{'al': None}
                            })

        restInterface.rest_put("busa", ['mcroute', 'hof', 2])
        expectedTrack = {
            'root': None,
            'route': [None, None],
            'mcroute':{'al': None, 'hof':[None, None, None]}
            }
        self.assertEqual(restInterface.track, expectedTrack)
        self.assertEqual(json.dumps(restInterface.track)
                         , json.dumps(expectedTrack))
        self.assertIs(principal, restInterface.rest_get('mcroute'))
