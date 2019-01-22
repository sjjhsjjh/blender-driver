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
# Unit test module.
# https://docs.python.org/3/library/unittest.html
# No need to import here because it is already imported by the Custom TestCase,
# see below.
# import unittest
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication
#
# Modules under test: 
from path_store.blender_game_engine import camera

from diagnostic.analysis import fall_analysis

class TestRotation(TestCaseWithApplication):
    def test_angular_move(self):
        def angular_move(current, target, speed=None):
            speedSign, targetRadians, changeRadians = (
                camera.angular_move(radians(current), radians(target))
                if speed is None else
                camera.angular_move(radians(current), radians(target), speed))
            return speedSign, degrees(targetRadians), degrees(changeRadians)
        
        speed, target, change = angular_move(0.0, 10.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 10.0)
        self.assertAlmostEqual(change, 10.0)

        speed, target, change = angular_move(0.0, -10.0)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, -10.0)
        self.assertAlmostEqual(change, 10.0)
        
        speed, target, change = angular_move(350, -5.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 355.0)
        self.assertAlmostEqual(change, 5.0)
        
        speed, target, change = angular_move(-10, -5.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -5.0)
        self.assertAlmostEqual(change, 5)
        
        speed, target, change = angular_move(0, 185)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, -175)
        self.assertAlmostEqual(change, 175)

        speed, target, change = angular_move(5, 190, 10)
        self.assertEqual(speed, -10)
        self.assertAlmostEqual(target, -170)
        self.assertAlmostEqual(change, 175)

        speed, target, change = angular_move(165, -230, 1)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, 130)
        self.assertAlmostEqual(change, 35)

        speed, target, change = angular_move(-178, -7)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -7)
        self.assertAlmostEqual(change, 171)

        speed, target, change = angular_move(180, -2)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 358)
        self.assertAlmostEqual(change, 178)

        speed, target, change = angular_move(-180, -2)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -2)
        self.assertAlmostEqual(change, 178)
