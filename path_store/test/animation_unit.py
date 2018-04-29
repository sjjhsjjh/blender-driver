#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestAnimation
"""
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
# Module under test.
from animation import Animation

# The name of this file should be animation.py but that clashes with the above
# module under test, so it's animation_unit.py instead.

class TestAnimation(unittest.TestCase):
    def test_exceptions(self):
        animation = Animation()
        with self.assertRaises(TypeError):
            animation.get_value()
        
        animation.startValue = 1.0
        with self.assertRaises(TypeError):
            animation.get_value()

        animation.speed = 2.0
        with self.assertRaises(TypeError):
            animation.get_value()
        
        animation.startTime = 3.0
        with self.assertRaises(TypeError):
            animation.get_value()
        
        animation.nowTime = 4.0
        self.assertAlmostEqual(3.0, animation.get_value())

    def test_complete(self):
        animation = Animation()
        self.assertFalse(animation.complete)
        self.assertIsNone(animation.completionTime)

        # Parameters will reach the target in 1.0 time unit.
        target = 3.0
        animation.startValue = 1.0
        animation.speed = 2.0
        animation.targetValue = target
        self.assertFalse(animation.complete)

        animation.startTime = 0.1
        animation.nowTime = 1.1
        #
        # Completion time is only set when get_value is called.
        self.assertFalse(animation.complete)
        self.assertIsNone(animation.completionTime)
        self.assertAlmostEqual(target, animation.get_value())
        self.assertTrue(animation.complete)
        self.assertEqual(1.1, animation.completionTime)

        animation.startTime = 0.1
        #
        # Setting startTime resets the completion flag.
        self.assertFalse(animation.complete)
        self.assertIsNone(animation.completionTime)
        animation.nowTime = 0.8
        self.assertFalse(animation.complete)
        self.assertIsNone(animation.completionTime)
        self.assertLess(animation.get_value(), target)
        self.assertFalse(animation.complete)
        self.assertIsNone(animation.completionTime)
        #
        # Target value is imposed as a limit.
        animation.nowTime = 12.0
        self.assertFalse(animation.complete)
        self.assertAlmostEqual(target, animation.get_value())
        self.assertTrue(animation.complete)
        self.assertTrue(animation.complete)
        self.assertEqual(12.0, animation.completionTime)
