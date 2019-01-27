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

import json

#
# Module for mathematical operations needed to decompose a rotation matrix.
# https://docs.python.org/3/library/math.html
from math import degrees, radians, fabs
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
# No need to import here because it is already imported by the Custom TestCase,
# see below.
# import unittest
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Euler, Vector
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication
#
# Modules under test: 
from path_store.blender_game_engine.cursor import Cursor

class TestCursor(TestCaseWithApplication):
    def _add_object_cursor(self, pathSuffix=None):
        gameObject = self.add_test_object()
        gameObject.physics = False
        self.show_status("Created object")
        objectPath = (tuple(self.objectPath)
                      if pathSuffix is None
                      else tuple(self.objectRoot) + tuple(pathSuffix))
        self.restInterface.rest_put(gameObject, objectPath)
        
        cursor = self.application.game_add_cursor()
        self.show_status("Created cursor")
        cursorPath = ['root', 'cursors', self.id()]
        if pathSuffix is not None:
            cursorPath.extend(pathSuffix)
        self.restInterface.rest_put(cursor, cursorPath)
        self.restInterface.rest_patch({
                'subjectPath': objectPath,
                'origin': (0, 0, 0), 'offset':0.25, 'length':1.0,
                'radius': 0.5, 'rotation': 0.0,
                'selfPath': cursorPath,
                'visualiserCalibre': 0.03
            }, cursorPath)
        self.restInterface.rest_put(True, cursorPath + ['visible'])
        self.show_status("Cursor visible")
        return gameObject, cursor
    
    def _do_move(self, move, animationPath, speedFactor=1.0):
        for preparation in move['preparation']:
            self.restInterface.rest_put(
                preparation['value'], preparation['path'])
        animation = dict(move['animation'])
        animation['speed'] = fabs(animation['delta']) / speedFactor
        self.restInterface.rest_put(animation, animationPath)

    def test_twist(self):
        transitionTime = 2
        transitionMargin = 1
        if transitionMargin >= transitionTime:
            raise AssertionError(
                'The transitionMargin must be less than the transitionTime.')
        transitionFactor = float(transitionTime) - float(transitionMargin)
        self.add_phase_starts(transitionTime)
        self.add_phase_offsets(transitionTime, transitionTime, 3)
        animation = None
        animationPath = None
        subjectLocation = None
        lastTick = None
        
        with self.application.mainLock:
            gameObject, cursor = self._add_object_cursor()
            subjectLocation = gameObject.worldPosition
            #
            # There is up to one animation for this test. It has to have a
            # number though, so that the point maker sees it as deep enough.
            animationPath = ['animations', self.id(), 0]
            
        with self.tick, self.application.mainLock:
            cursor.rotation = radians(180)
            point = cursor.point
            self.assertEqual(point.x, subjectLocation.x - cursor.radius)
            self.assertEqual(point.y, subjectLocation.y)
            self.assertEqual(point.z, subjectLocation.z
                             + cursor.offset + cursor.length)

            cursor.rotation = 0
            point = cursor.point
            self.assertEqual(point.x, subjectLocation.x + cursor.radius)
            self.assertEqual(point.y, subjectLocation.y)
            self.assertEqual(point.z, subjectLocation.z
                             + cursor.offset + cursor.length)
                        
        with self.tick, self.application.mainLock:
            self._do_move(cursor.moves[2], animationPath, transitionFactor)
            self.show_status("Twisting 0")
        while self.up_to_phase(0):
            with self.tick, self.application.mainLock:
                animation = self.restInterface.rest_get(animationPath)
                if animation is None:
                    self.assertFalse(cursor.beingAnimated)
                else:
                    self.assertTrue(cursor.beingAnimated)

        with self.tick, self.application.mainLock:
            self.assertFalse(cursor.beingAnimated)
            self._do_move(cursor.moves[1], animationPath, transitionFactor)
            self.show_status("Twisting 1")
        while self.up_to_phase(1):
            with self.tick, self.application.mainLock:
                animation = self.restInterface.rest_get(animationPath)
                if animation is None:
                    self.assertFalse(cursor.beingAnimated)
                else:
                    self.assertTrue(cursor.beingAnimated)

        with self.tick, self.application.mainLock:
            self.assertFalse(cursor.beingAnimated)
            self._do_move(cursor.moves[3], animationPath, transitionFactor)
            self.show_status("Twisting 2")
        while self.up_to_phase(2):
            with self.tick, self.application.mainLock:
                animation = self.restInterface.rest_get(animationPath)
                if animation is None:
                    self.assertFalse(cursor.beingAnimated)
                else:
                    self.assertTrue(cursor.beingAnimated)
                lastTick = self.application.tickPerf

        with self.tick, self.application.mainLock:
            point = cursor.point
            print(point, subjectLocation)
            self.assertEqual(point.x, subjectLocation.x)
            self.assertEqual(point.y, subjectLocation.y + cursor.radius)
            self.assertEqual(point.z, subjectLocation.z
                             - (cursor.offset + cursor.length))
            zPosition = cursor.point.z
            gameObject.physics = True
            self.show_status("Dropping")

        while self.up_to_phase(3):
            with self.tick, self.application.mainLock:
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf
                #
                # Check that the cursor's Z position is falling every tick. See
                # the notes on the check for this type of thing at the end of
                # the TestAnimation.test_physics test.
                self.assertLessEqual(cursor.point.z, zPosition)
                zPosition = cursor.point.z

    def test_grow(self):
        transitionTime = 2
        transitionMargin = 1
        if transitionMargin >= transitionTime:
            raise AssertionError(
                'The transitionMargin must be less than the transitionTime.')
        transitionFactor = float(transitionTime) - float(transitionMargin)
        self.add_phase_starts(transitionTime)
        self.add_phase_offsets(
            transitionTime, transitionTime, transitionTime, 1, 1)
        animation = None
        animationPath = None
        subjectLocation = None
        lastTick = None
        
        def _do_grow(grow):
            for key, item in grow.items():
                animation = dict(item)
                # animation['delta'] *= self.application.cubeScale
                animation['speed'] = (
                    fabs(animation['delta'])
                    / (float(transitionTime) - float(transitionMargin)))
                animationPath[-1] = key
                self.restInterface.rest_put(animation, animationPath)

        with self.application.mainLock:
            gameObject, cursor = self._add_object_cursor(('main',))
            subjectLocation = gameObject.worldPosition.copy()
            gameObject0, cursor0 = self._add_object_cursor(('reference',))
            gameObject0.worldPosition.y -= self.application.cubeScale * 2.0
            #
            # There are a number of animations for this test. The None is a
            # placeholder to be overwritten.
            animationPath = ['animations', self.id(), None]
            
        with self.tick, self.application.mainLock:
            origin = cursor.origin[:]
            _do_grow(cursor.grow)
            self.show_status("Growing 1")
        while self.up_to_phase(0):
            with self.tick, self.application.mainLock:
                self.assertGreaterEqual(cursor.origin[2], origin[2])
                origin[2] = cursor.origin[2]
                self.assertSequenceEqual(cursor.origin[0:1], origin[0:1])
                # animations = self.restInterface.rest_get(animationPath[:-1])
                # for key, item in animations.items():
                #     if item is None:
                #         animation = None
                #     else:
                #         animation = dict(item.__dict__)
                #         del animation['_store']
                #     print(key, animation)
                if gameObject.physics:
                    gameObject.physics = False
                    gameObject.worldPosition.z = (
                        subjectLocation.z + self.application.cubeScale)
            
        with self.tick, self.application.mainLock:
            origin = cursor.origin[:]
            _do_grow(cursor.grow)
            self.show_status("Growing 2")
        while self.up_to_phase(1):
            with self.tick, self.application.mainLock:
                self.assertGreaterEqual(cursor.origin[2], origin[2])
                origin[2] = cursor.origin[2]
                self.assertSequenceEqual(cursor.origin[0:1], origin[0:1])
                if gameObject.physics:
                    gameObject.physics = False
                    gameObject.worldPosition.z = (
                        subjectLocation.z + 2.0 * self.application.cubeScale)

        with self.tick, self.application.mainLock:
            animationPath[-1] = 'move'
            self._do_move(cursor.moves[2], animationPath, transitionFactor)
            self.show_status("Twisting 1")
        while self.up_to_phase(2):
            with self.tick, self.application.mainLock:
                if gameObject.physics:
                    gameObject.physics = False
            
        with self.tick, self.application.mainLock:
            origin = cursor.origin[:]
            _do_grow(cursor.grow)
            self.show_status("Growing 3")
        while self.up_to_phase(3):
            with self.tick, self.application.mainLock:
                self.assertGreaterEqual(cursor.origin[0], origin[0])
                origin[0] = cursor.origin[0]
                self.assertSequenceEqual(cursor.origin[1:], origin[1:])
                if gameObject.physics:
                    gameObject.physics = False
                    gameObject.worldPosition.z = (
                        subjectLocation.z + 2.0 * self.application.cubeScale)

        while self.up_to_phase(4):
            with self.tick, self.application.mainLock:
                if gameObject.physics:
                    gameObject.physics = False

        with self.tick, self.application.mainLock:
            gameObject.physics = True
            gameObject0.physics = True
            self.show_status("Dropping")

        while self.up_to_phase(5):
            with self.tick, self.application.mainLock:
                pass
