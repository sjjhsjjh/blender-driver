#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
# https://docs.python.org/3/library/math.html
from math import degrees, radians


# https://docs.python.org/3/library/threading.html
import threading


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
        try:
            objectName = self.application.testObjectName
        except AttributeError:
            objectName = None
        if objectName is None:
            for key in self.application.templates.keys():
                if 'text' not in self.application.templates[key]:
                    objectName = key
                    break
        return GameObject, objectName
    
    def test_fundamentals(self):
        self.assertIsNotNone(self.application)

        with self.application.mainLock:
            self.assertTrue(self.application.bge)
            self.assertTrue(self.application.bge.types.KX_GameObject)        
            GameObject, objectName = self.get_class_and_name()
            self.assertIsNotNone(objectName)
    
            gameObject = GameObject(
                self.application.game_add_object(objectName))
            name = 'worldPosition'
            #
            # Grab the position before gravity has had a chance to move the
            # object.
            worldPositionNative = gameObject.worldPosition[:]
            worldPositionGot = pathstore.get(gameObject, name)[:]
            self.assertEqual(worldPositionGot, worldPositionNative)
            #
            # Test the intercept property works as expected.
            self.assertEqual(
                worldPositionNative
                , self.application.templates[objectName]['location'])

    def test_path_store(self):
        with self.application.mainLock:
            gameObject = self.add_test_object()
            GameObject = type(gameObject)
            name = 'worldPosition'
            #
            # In general, an object other than a dictionary raises TypeError
            # when an attempt to subscript it is made. A Blender KX_GameObject
            # instance raises KeyError instead. Next couple of asserts re-prove
            # that.
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
        with self.application.mainLock:
            gameObject = self.add_test_object()
            self.show_status("Created")

            gameObject.physics = False
            #
            # Initial rotation in all axes should be zero.
            self.assertEqual(0, pathstore.get(gameObject, ('rotation', 0)))
            self.assertEqual(gameObject.rotation[:], (0, 0, 0))
            
            xDegrees = degrees(gameObject.rotation.x)
            degreesMax = 720.0

        while xDegrees < degreesMax:
            with self.tick:
                # This can run quite lumpy. It isn't supposed to be smooth; it's
                # supposed to test that setting the X rotation doesn't change
                # the Y and Z rotations.
                with self.application.mainLock:
                    for _ in range(10):
                        xDegrees += 1.0
                        self.show_status(
                            "{:.2f} {:.2f}".format(xDegrees, degreesMax))
                        xRadians = radians(xDegrees)
                        gameObject.rotation.x = xRadians
                        self.assertEqual(xRadians, gameObject.rotation.x)
                        self.assertEqual(
                            xRadians, pathstore.get(gameObject, ('rotation', 0)))
                        self.assertEqual(
                            xRadians, pathstore.get(gameObject, ('rotation', 'x')))
                        self.assertEqual(0, gameObject.rotation.y)
                        self.assertEqual(0, pathstore.get(gameObject, ('rotation', 1)))
                        self.assertEqual(
                            0, pathstore.get(gameObject, ('rotation', 'y')))
                        self.assertEqual(0, gameObject.rotation.z)

        with self.application.mainLock:
            #
            # Deleting all elements, or the property, actually doesn't delete
            # it. You just get the rotation of the underlaying game object
            # instead.
            del gameObject.rotation[:]
            self.assertEqual(len(gameObject.rotation), 3)
            del gameObject.rotation
            self.assertEqual(len(gameObject.rotation), 3)
            #
            # Setting a rotation should set the underlaying game object
            # rotation. This means that setting and then deleting the rotation
            # should leave the game object rotated as before.
            rotation = (radians(1), radians(2), radians(3))
            gameObject.rotation = rotation
            self.assertSequenceEqual(
                rotation, pathstore.get(gameObject, ('rotation',)))
            del gameObject.rotation
            for index in range(len(rotation)):
                self.assertAlmostEqual(
                    rotation[index]
                    , pathstore.get(gameObject, ('rotation', index))
                    , places=5)
    
            # Next line makes the object fall away, which is nice.
            gameObject.physics = True
    
    def test_physics(self):
        lastTick = None
        with self.application.mainLock:
            gameObject = self.add_test_object()
    
            gameObject.physics = False
            self.show_status("Suspended...")
            phases = (self.application.tickPerf + 1.0,
                      self.application.tickPerf + 2.0,
                      self.application.tickPerf + 3.0)
            zPosition = gameObject.worldPosition.z
        
        while self.application.tickPerf < phases[0]:
            with self.tick:
                with self.application.mainLock:
                    self.assertEqual(zPosition, gameObject.worldPosition.z)
        
        with self.tick:
            with self.application.mainLock:
                gameObject.physics = True
                self.show_status("Dropping...")
                # No assertion; waiting for it to drop.
        while self.application.tickPerf <= phases[1]:
            with self.tick:
                pass

        with self.tick:
            lastTick = self.application.tickPerf
        while self.application.tickPerf < phases[2]:
            with self.tick:
                if self.application.tickPerf - lastTick >= 0.05:
                    with self.application.mainLock:
                        # print(gameObject.worldPosition.z, tickTime
                        #       , self.application.tickPerf
                        #       , threading.currentThread().name
                        #       , threading.get_ident())
                        # Check that its z position is falling every tick.
                        self.assertLess(
                            gameObject.worldPosition.z, zPosition
                            , "{:.4f} {:.4f} {:.4f}".format(
                                lastTick, self.application.tickPerf
                                , self.application.tickPerf - lastTick))
                        zPosition = gameObject.worldPosition.z
                        self.assertGreater(self.application.tickPerf, lastTick)
                    lastTick = self.application.tickPerf
