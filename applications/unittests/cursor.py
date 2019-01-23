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
    def test_twist(self):
        twistTime = 2
        twistMargin = 1
        if twistMargin >= twistTime:
            raise AssertionError(
                'The twistMargin must be less than the twistTime.')
        self.add_phase_starts(twistTime)
        self.add_phase_offsets(twistTime, twistTime, 3)
        animation = None
        animationPath = None
        subjectLocation = None
        lastTick = None
        
        def _do_move(move):
            self.restInterface.rest_put(
                move['preparation']['value'], move['preparation']['path'])
            animation = dict(move['animation'])
            animation['speed'] = (
                fabs(animation['delta'])
                / (float(twistTime) - float(twistMargin)))
            self.restInterface.rest_put(animation, animationPath)

        with self.application.mainLock:
            gameObject = self.add_test_object()
            gameObject.physics = False
            self.show_status("Created object")
            self.restInterface.rest_put(gameObject, self.objectPath)
            subjectLocation = gameObject.worldPosition
            
            cursor = self.application.game_add_cursor()
            self.show_status("Created cursor")
            cursorPath = ['root', 'cursors', 0]
            self.restInterface.rest_put(cursor, cursorPath)
            self.restInterface.rest_patch({
                    'subjectPath': tuple(self.objectPath),
                    'origin': (0, 0, 0), 'offset':0.25, 'length':1.0,
                    'radius': 0.5, 'rotation': 0.0,
                    'selfPath': cursorPath,
                    'visualiserCalibre': 0.03
                }, cursorPath)
            self.restInterface.rest_put(True, cursorPath + ['visible'])
            self.show_status("Cursor visible")
            
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
            _do_move(cursor.moves[0])
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
            _do_move(cursor.moves[2])
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
            _do_move(cursor.moves[0])
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
