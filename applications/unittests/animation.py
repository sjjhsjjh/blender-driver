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
# Module for mathematical operations, only used for degree to radian conversion.
# https://docs.python.org/3/library/math.html
from math import degrees, radians
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication

class TestAnimation(TestCaseWithApplication):
    def test_linear(self):
        with self.application.mainLock:
            gameObject = self.add_test_object()
            self.show_status("Created")

            gameObject.physics = False
            self.restInterface.rest_put(gameObject, self.objectPath)
            #
            # Path to the object's Z value.
            valuePath = list(self.objectPath) + ['worldPosition', 2]
            #
            # Get the current value.
            value = self.restInterface.rest_get(valuePath)
            addition = 2.0
            speed = 1.0
            target = value + addition
            phases = (
                self.application.tickPerf + (addition / speed),
                self.application.tickPerf + (addition / speed) + 1.0)
            #
            # Assemble the animation in a dictionary.
            animation = {
                'modulo': 0,
                'valuePath': valuePath,
                # 'subjectPath': self.objectPath,
                'speed': speed,
                'targetValue': target}
            #
            # There is up to one animation for this test. It has to have a
            # number though, so that the point maker sees it as deep enough.
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
            del animationPath[-1]
        
        while(self.application.tickPerf < phases[1]):
            with self.tickLock:
                with self.application.mainLock:
                    if self.application.tickPerf < phases[0]:
                        #
                        # Check object hasn't reached its destination.
                        self.assertLess(gameObject.worldPosition.z, target)
                        #
                        # Check animation is still in progress.
                        self.assertIsNotNone(
                            self.restInterface.rest_get(animationPath))
                    else:
                        #
                        # Check object has reached its destination.
                        self.assertAlmostEqual(gameObject.worldPosition.z, target)
                        #
                        # Check animation has been discarded.
                        self.assertIsNone(
                            self.restInterface.rest_get(animationPath))
        
        with self.application.mainLock:
            # Next line makes the object fall away, which is nice.
            gameObject.physics = True
