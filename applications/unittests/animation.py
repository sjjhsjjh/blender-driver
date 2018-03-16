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
# https://docs.python.org/3.5/library/math.html
from math import degrees, radians
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication

class TestAnimation(TestCaseWithApplication):
    def test_linear(self):
        self.application.mainLock.acquire()
        try:
            gameObject, created = self.get_test_object()
            self.status = "Created"
            if created:
                gameObject.physics = False
                self.restInterface.rest_put(gameObject, self.objectPath)
                
                #
                # Path to the object's Z value.
                valuePath = list(self.objectPath) + ['worldPosition', 2]
                #
                # Get the current value.
                value = self.restInterface.rest_get(valuePath)
                addition = 2.0
                speed = 0.2
                self.store['target'] = value + addition
                self.store['phases'] = (
                    self.application.tickPerf + (addition / speed),
                    self.application.tickPerf + (addition / speed) + 1.0)
                #
                # Assemble the animation in a dictionary.
                animation = {
                    'modulo': 0,
                    'path': valuePath,
                    'speed': speed,
                    'targetValue': self.store['target']
                }
                #
                # There is up to one animation for this test.
                # It has to have a number though, so that the point maker sees
                # it as deep enough.
                animationPath = ['animations', self.id(), 0]
                #
                # Insert the animation. The point maker will set the store
                # attribute.
                self.restInterface.rest_put(animation, animationPath)
                #
                # Set the start time, which has the following side effects:
                # -   Retrieves the start value.
                # -   Clears the complete state.
                animationPath.append('startTime')
                self.restInterface.rest_put(
                    self.application.tickPerf, animationPath)
            
            if self.application.tickPerf < self.store['phases'][0]:
                self.assertLess(
                    gameObject.worldPosition.z, self.store['target'])
            else:
                self.assertAlmostEqual(
                    gameObject.worldPosition.z, self.store['target'])

            if self.application.tickPerf < self.store['phases'][1]:
                return
            
            self.status = None
            self.skipTest("Finished")
        finally:
            self.application.mainLock.release()
