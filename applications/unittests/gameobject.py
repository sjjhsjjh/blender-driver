#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application with Python unit test integration.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
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
# Modules under test: 
from path_store import pathstore, blender_game_engine

class TestGameObject(unittest.TestCase):
    application = None
    
    @classmethod
    def set_application(cls, application):
        '''\
        Has to be a class method because instantiation is hidden by the test
        loader.'''
        cls.application = application
    
    def test_game_object(self):
        #
        # Fundamentals.
        self.assertTrue(self.application.bge)
        self.assertTrue(self.application.bge.types.KX_GameObject)
        templates = self.application.templates
        
        GameObject = blender_game_engine.get_game_object_subclass(
            self.application.bge)
        objectName = None
        for key in templates.keys():
            objectName = key
            break
        self.assertIsNotNone(objectName)
        gameObject = GameObject(self.application.game_add_object(objectName))
        #
        # Grab the position before gravity has had a chance to move the object.
        name = 'worldPosition'
        worldPositionNative = gameObject.worldPosition[:]
        worldPositionGot = pathstore.get(gameObject, name)[:]
        self.assertEqual(worldPositionGot, worldPositionNative)
        #
        # Test the intercept property works as expected.
        self.assertEqual(worldPositionNative, templates[objectName]['location'])
        #
        # In general, an object other than a dictionary raise TypeError when
        # an attempt to subscript it is made. A Blender KX_GameObject instance
        # raises KeyError instead. Next couple of asserts re-prove that.
        with self.assertRaises(KeyError) as context:
            gameObject[name]
        class Principal:
            pass
        principal = Principal()
        with self.assertRaises(TypeError) as context:
            principal[name]
        #
        # Also, Blender KX_GameObject returns False but objects in general raise
        # TypeError.
        self.assertFalse(name in gameObject)
        self.assertTrue(hasattr(gameObject, name))
        with self.assertRaises(TypeError) as context:
            bool_ = name in principal
        #
        # Test the dictionary-like capability of Blender KX_GameObject.
        path = 'NotAnAttribute'
        #
        # KeyError is raised by path store or native subscription.
        with self.assertRaises(KeyError) as context:
            value = pathstore.get(gameObject, path)
        with self.assertRaises(KeyError) as context:
            value = gameObject[path]
        #
        # Set native, then get with path store.
        value = 3
        gameObject[path] = value
        self.assertEqual(value, pathstore.get(gameObject, path))
        # Belt and braces: it hasn't become an attribute.
        with self.assertRaises(AttributeError) as context:
            value = gameObject.NotAnAttribute
        #
        # Check that using path store to replace a value set by subscription
        # works.
        value = 4
        gameObject0 = gameObject
        gameObject1 = pathstore.replace(gameObject0, value, path)
        self.assertIs(gameObject0, gameObject1)
        self.assertIs(gameObject0, gameObject)
        self.assertIsInstance(gameObject1, GameObject)
        self.assertEqual(gameObject0[path], value)
        #
        # Check that using path store to add a new key works.
        path = 'NotAnotherAttribute'
        with self.assertRaises(KeyError) as context:
            value = gameObject0[path]
        value = 7
        gameObject1 = pathstore.replace(gameObject0, value, path)
        self.assertIs(gameObject0, gameObject1)
        self.assertIsInstance(gameObject1, GameObject)
        self.assertEqual(gameObject0[path], value)
