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
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication
#
# Modules under test: 
from path_store import pathstore
from path_store import rest
from path_store.blender_game_engine import gameobject, gameobjectcollection

from diagnostic.analysis import fall_analysis

class TestGameObject(TestCaseWithApplication):
    def get_class_and_name(self):
        GameObject = gameobject.get_game_object_subclass(self.application.bge)
        try:
            objectName = self.application.testObjectName
        except AttributeError:
            objectName = None
        if objectName is None:
            for key in self.application.templates.keys():
                if 'text' in self.application.templates[key]:
                    continue
                if objectName is not None:
                    raise RuntimeError(
                        "Couldn't determine object name."
                        ' At least two candidates in templates.')
                objectName = key
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
            worldPositionNative = gameObject.worldPosition.copy()
            worldPositionGot = pathstore.get(gameObject, name)[:]
            self.assertEqual(worldPositionGot, worldPositionNative[:])
            #
            # Test the intercept property works as expected.
            self.assertEqual(
                worldPositionNative[:]
                , self.application.templates[objectName]['location'])
            #
            # The worldPosition value will be a BGE Vector instance.
            # The iterify() subroutine relies on:
            #
            # -   AttributeError being raised by objects that aren't
            #     dictionaries when their items method is called.
            # -   Vector being enumerable.
            #
            # Test those here.
            with self.assertRaises(AttributeError) as context:
                items = worldPositionNative.items()
            self.assertEqual(tuple(enumerate(worldPositionNative))
                             , tuple(enumerate(worldPositionNative[:])))
            #
            # Test the generic value of a Vector is the same as its items.
            self.assertEqual(worldPositionNative[:]
                             , rest._generic_value(worldPositionNative))

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
            self.assertSequenceEqual(gameObject.rotation[:], [0, 0, 0])
            
            xDegrees = degrees(gameObject.rotation.x)
            degreesMax = 720.0
        
        with self.tick:
            lastTick = self.application.tickPerf

        while xDegrees < degreesMax:
            with self.tick:
                elapsed = self.application.tickPerf - lastTick
                addDegrees = int(elapsed * 120.0)
                # This can run quite lumpy. It isn't supposed to be smooth; it's
                # supposed to test that setting the X rotation doesn't change
                # the Y and Z rotations.
                with self.application.mainLock:
                    for _ in range(1 if addDegrees < 1 else addDegrees):
                        xDegrees += 1.0
                        self.show_status("{:d} {:.2f} {:.2f}".format(
                            addDegrees, xDegrees, degreesMax))
                        xRadians = radians(xDegrees)
                        gameObject.rotation.x = xRadians
                        self.assertEqual(xRadians, gameObject.rotation.x)
                        self.assertEqual(
                            xRadians
                            , pathstore.get(gameObject, ('rotation', 0)))
                        self.assertEqual(
                            xRadians
                            , pathstore.get(gameObject, ('rotation', 'x')))
                        self.assertEqual(0, gameObject.rotation.y)
                        self.assertEqual(
                            0, pathstore.get(gameObject, ('rotation', 1)))
                        self.assertEqual(
                            0, pathstore.get(gameObject, ('rotation', 'y')))
                        self.assertEqual(0, gameObject.rotation.z)
                lastTick = self.application.tickPerf

        with self.tick, self.application.mainLock:
            # Test that rotation can be reset.
            self.assertNotEqual(gameObject.rotation.x, 0)
            gameObject.rotation = (0, 0, 0)
            self.assertSequenceEqual(gameObject.rotation, (0, 0, 0))
            
        with self.tick, self.application.mainLock:
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
        with self.application.mainLock:
            gameObject = self.add_test_object()
    
            gameObject.physics = False
            self.show_status("Suspended...")
            self.add_phase_starts(1, 2, 5)
            zPosition = gameObject.worldPosition.z

        with self.tick:
            lastTick = self.application.tickPerf
        
        while self.up_to_phase(0):
            with self.tick, self.application.mainLock:
                self.assertEqual(zPosition, gameObject.worldPosition.z)
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf

        with self.tick, self.application.mainLock:
            gameObject.physics = True
            self.show_status("Dropping...")
            # No assertion; waiting for it to drop.

        while self.up_to_phase(1):
            with self.tick:
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf

        with self.tick, self.application.mainLock:
            zPositions = []
            zPosition = gameObject.worldPosition.z
        while self.up_to_phase(2):
            with self.tick, self.application.mainLock:
                self.assertGreater(self.application.tickPerf, lastTick)
                # Next is LessEqual because sometimes it doesn't fall.
                self.assertLessEqual(gameObject.worldPosition.z, zPosition)
                lastTick = self.application.tickPerf
                zPosition = gameObject.worldPosition.z
                zPositions.append((zPosition, lastTick))
        
        fallErrors, fallDump = fall_analysis(zPositions)
        if fallErrors > 0:
            print("Fall errors:{:d}\n{}".format(fallErrors, fallDump))

    def test_list(self):
        self.add_phase_starts(3, 4, 5)
        count = 4
        paraList = []
        error = RuntimeError(
            "KX_GameObject.GetPhysicsId() - Blender Game Engine data has been"
            " freed, cannot use this python variable")

        with self.application.mainLock:
            gameObjects = gameobjectcollection.GameObjectList()
            for index in range(count):
                gameObject = self.add_test_object()
                gameObject.physics = False
                gameObject.rotation.y = radians(20 * index)
                gameObject.worldPosition.z = 2 + index
                gameObjects.append(gameObject)
                paraList.append(gameObject)
            self.assertEqual(gameObjects, paraList)
            self.show_status("Created {}...".format(len(gameObjects)))
        while self.up_to_phase(0):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Delete first item.
            del gameObjects[0]
            count -= 1
            self.assertEqual(len(gameObjects), count)
            self.show_status("Deleted len:{}".format(len(gameObjects)))
        while self.up_to_phase(1):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Check that the game object is gone.
            with self.assertRaises(RuntimeError) as context:
                physicsID = paraList[0].getPhysicsId()
            self.assertEqual(str(context.exception), str(error))
            # Delete second and third items.
            del gameObjects[1:3]
            count -= 2
            self.assertEqual(len(gameObjects), count)
            self.show_status("Deleted len:{}".format(len(gameObjects)))
        # Wait for two ticks, then check the game objects are gone.
        for waitTick in range(2):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            with self.assertRaises(RuntimeError) as context:
                physicsID = paraList[2].getPhysicsId()
            self.assertEqual(str(context.exception), str(error))
            with self.assertRaises(RuntimeError) as context:
                physicsID = paraList[3].getPhysicsId()
            self.assertEqual(str(context.exception), str(error))
            paraList[1].physics = True
        while self.up_to_phase(2):
            with self.tick:
                pass

    def test_dict(self):
        self.add_phase_starts(2, 4, 5)
        keys = ('first', 'second', 'third')
        paraDict = {}
        error = RuntimeError(
            "KX_GameObject.RestoreDynamics() - Blender Game Engine data has"
            " been freed, cannot use this python variable")

        with self.application.mainLock:
            gameObjects = gameobjectcollection.GameObjectDict()
            for index, key in enumerate(keys):
                gameObject = self.add_test_object()
                gameObject.physics = False
                gameObject.rotation.z = radians(20 * index)
                gameObject.worldPosition.y -= float(index) * 1.5
                gameObjects[key] = gameObject
                paraDict[key] = gameObject
            self.assertEqual(gameObjects, paraDict)
            self.show_status("Created {}...".format(
                ",".join(gameObjects.keys())))
        while self.up_to_phase(0):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Delete an item.
            del gameObjects[keys[0]]
            self.assertEqual(len(gameObjects) + 1, len(paraDict))
            self.show_status("Deleted except {}".format(
                ",".join(gameObjects.keys())))
        while self.up_to_phase(1):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Check that the deleted game object is gone.
            with self.assertRaises(RuntimeError) as context:
                paraDict[keys[0]].physics = True
            self.assertEqual(str(context.exception), str(error))
            # Make the remaining objects fall, which is an implicit check that
            # they are still OK to access.
            for key in gameObjects.keys():
                paraDict[key].physics = True
        while self.up_to_phase(2):
            with self.tick:
                pass

    def test_rest_dict(self):
        self.add_phase_starts(3, 4, 5)
        keys = ('third', 'fourth', 'fifth')
        paraDict = {}
        error = RuntimeError(
            "KX_GameObject.RestoreDynamics() - Blender Game Engine data has"
            " been freed, cannot use this python variable")

        with self.application.mainLock:
            objectPath = list(self.objectRoot) + [None]
            for index, key in enumerate(keys):
                gameObject = self.add_test_object()
                gameObject.physics = False
                gameObject.rotation.z = radians(20 * (index + 5))
                gameObject.worldPosition.y -= 3 + (float(index) * 1.5)
                objectPath[-1] = key
                self.restInterface.rest_put(gameObject, objectPath)
                paraDict[objectPath[-1]] = gameObject
            gameObjects = self.restInterface.rest_get(self.objectRoot)
            self.assertIsInstance(
                gameObjects, gameobjectcollection.GameObjectDict, gameObjects)
            self.assertEqual(gameObjects, paraDict)
            self.show_status("Created {}...".format(
                ",".join(gameObjects.keys())))
        while self.up_to_phase(0):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Delete an item.
            objectPath[-1] = keys[0]
            gameObject = self.restInterface.rest_delete(objectPath)
            self.assertIs(gameObject, paraDict[keys[0]])
            self.assertEqual(
                len(self.restInterface.rest_get(self.objectRoot)) + 1
                , len(paraDict))
            gameObjects = self.restInterface.rest_get(self.objectRoot)
            self.show_status("Deleted except {}...".format(
                ",".join(gameObjects.keys())))
        while self.up_to_phase(1):
            with self.tick:
                pass
        with self.tick, self.application.mainLock:
            # Check that the deleted game object is gone.
            with self.assertRaises(RuntimeError) as context:
                gameObject.physics = True
            self.assertEqual(str(context.exception), str(error))
            # Make the remaining objects fall, by switching on physics in a
            # walk, which is an implicit check that they are still OK to access.
            def set_physics(point, path, results):
                point.physics = True
            self.restInterface.rest_walk(set_physics, self.objectRoot)

        while self.up_to_phase(2):
            with self.tick:
                pass

    def test_scale(self):
        self.add_phase_starts(6, 7, 8)
        with self.application.mainLock:
            gameObject = self.add_test_object()
            self.show_status("Created")

            gameObject.physics = False
            #
            # Initial scale in all axes should be the same as the template.
            objectName = self.get_class_and_name()[1]
            try:
                expectedScale = self.application.templates[objectName
                                                           ]['scale'][:]
            except:
                print(objectName, self.application.templates[objectName])
                raise
            self.assertAlmostEqual(
                expectedScale[0], pathstore.get(gameObject, ('worldScale', 0)))
            self.assertAlmostEqual(gameObject.worldScale[:], expectedScale)
            
            zAxis = (0, 0, 1)
            axisVector = gameObject.getAxisVect(zAxis).copy()
            self.assertSequenceEqual(zAxis, axisVector)
            
        scale = [expectedScale[0] * 12.0,
                 expectedScale[1] * 3.0,
                 expectedScale[2] * 4.0]
        while self.up_to_phase(0):
            with self.tick:
                pass
        with self.tick:
            with self.application.mainLock:
                pathstore.replace(gameObject, scale, 'worldScale')
                #
                # Test that changing scale doesn't change the axis vector.
                self.assertEqual(gameObject.getAxisVect((0, 0, 1))
                                 , axisVector)

        while self.up_to_phase(1):
            with self.tick:
                pass
        with self.tick:
            with self.application.mainLock:
                pathstore.replace(gameObject, expectedScale, 'worldScale')

        while self.up_to_phase(2):
            with self.tick:
                pass
        with self.tick:
            with self.application.mainLock:
                pathstore.merge(gameObject, scale, 'worldScale')

        with self.tick, self.application.mainLock:
            gameObject.physics = True
