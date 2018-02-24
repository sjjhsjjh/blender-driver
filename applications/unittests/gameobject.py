#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver unit test that can be run from the unittest application.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for mathematical operations needed to decompose a rotation matrix.
# https://docs.python.org/3.5/library/math.html
from math import radians
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication
#
# Modules under test: 
from path_store import pathstore, blender_game_engine

class TestGameObject(TestCaseWithApplication):
    def get_class_and_name(self):
        GameObject = blender_game_engine.get_game_object_subclass(
            self.application.bge)
        objectName = None
        for key in self.application.templates.keys():
            objectName = key
            break
        return GameObject, objectName
    
    def get_game_object(self):
        GameObject, objectName = self.get_class_and_name()
        return GameObject(self.application.game_add_object(objectName))
    
    def test_fundamentals(self):
        self.assertIsNotNone(self.application)
        self.assertTrue(self.application.bge)
        self.assertTrue(self.application.bge.types.KX_GameObject)        
        GameObject, objectName = self.get_class_and_name()
        self.assertIsNotNone(objectName)

        gameObject = self.get_game_object()
        name = 'worldPosition'
        #
        # Grab the position before gravity has had a chance to move the object.
        worldPositionNative = gameObject.worldPosition[:]
        worldPositionGot = pathstore.get(gameObject, name)[:]
        self.assertEqual(worldPositionGot, worldPositionNative)
        #
        # Test the intercept property works as expected.
        self.assertEqual(worldPositionNative
                         , self.application.templates[objectName]['location'])
    
    def test_path_store(self):
        gameObject = self.get_game_object()
        GameObject = type(gameObject)
        name = 'worldPosition'
        #
        # In general, an object other than a dictionary raises TypeError when
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
        # Also, property name `in` Blender KX_GameObject returns False but
        # objects in general raise TypeError.
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
        # Belt and braces: check that it hasn't become an attribute.
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

    def test_rotation(self):
        gameObject = self.get_game_object()
        self.assertEqual(0, pathstore.get(gameObject, ('rotation', 0)))
        self.assertEqual(gameObject.rotation[:], (0, 0, 0))
        for xDegrees in range(0,720):
            xRadians = radians(xDegrees)
            gameObject.rotation.x = xRadians
            self.assertEqual(xRadians, gameObject.rotation.x)
            self.assertEqual(0, gameObject.rotation.y)
            self.assertEqual(0, gameObject.rotation.z)
        
        del gameObject.rotation[:]
        self.assertEqual(len(gameObject.rotation), 3)
