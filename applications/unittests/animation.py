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
        '''\
        Test basic linear animation and replacement of the animation object
        by None on completion.
        '''
        with self.application.mainLock:
            gameObject = self.add_test_object()
            self.show_status("Created")

            # ToDo: Change this to use a STATIC object.
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
            # Assemble the animation in a dictionary. Note there is no
            # subjectPath so that physics don't get resumed.
            animation = {
                'modulo': 0,
                'valuePath': valuePath,
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
        
        while self.application.tickPerf < phases[1]:
            with self.tick:
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
                        self.assertAlmostEqual(
                            gameObject.worldPosition.z, target)
                        #
                        # Check animation has been discarded.
                        self.assertIsNone(
                            self.restInterface.rest_get(animationPath))
        
        with self.application.mainLock:
            # Next line makes the object fall away, which is nice.
            gameObject.physics = True

    def test_physics(self):
        '''Test that physics gets suspended during animation.'''
        lastTick = None
        zPosition = None
        interval = 0.05
        gameObject = None
        phases = (1.0, 5.0, 5 + interval, 6.0)
        turn = radians(135.0)
        animation = None
        animationPath = None
        tickStart = None
        
        with self.tick:
            with self.application.mainLock:
                gameObject = self.add_test_object()
                gameObject.physics = False
                gameObject.worldPosition.z = 6.0
                self.show_status("Created")
    
                self.restInterface.rest_put(gameObject, self.objectPath)
    
                tickStart = self.application.tickPerf 
    
                valuePath = tuple(self.objectPath) + ('rotation', 'z')
                value = self.restInterface.rest_get(valuePath)
    
                #
                # Assemble the animation in a dictionary. Note that there is a
                # subjectPath so that physics gets suspended and resumed.
                animation = {
                    'modulo': radians(360.0),
                    'valuePath': valuePath,
                    'subjectPath': self.objectPath,
                    'speed': turn / (phases[1] - phases[0]),
                    'targetValue': value + turn}
                #
                # There is up to one animation for this test. It has to have a
                # number though, so that the point maker sees it as deep enough.
                animationPath = ['animations', self.id(), 0]

                zPosition = gameObject.worldPosition.z
                gameObject.physics = True
                self.show_status("Falling")
            lastTick = self.application.tickPerf

        while self.application.tickPerf <= tickStart + phases[0]:
            with self.tick:
                if self.application.tickPerf - lastTick >= interval:
                    with self.application.mainLock:
                        # Check that its z position is falling every tick.
                        self.assertLess(
                            gameObject.worldPosition.z, zPosition
                            , "{:.4f} {:.4f} {:.4f}".format(
                                lastTick, self.application.tickPerf
                                , self.application.tickPerf - lastTick))
                        zPosition = gameObject.worldPosition.z
                    lastTick = self.application.tickPerf

        with self.tick:
            # print(self.application.tickPerf)
            with self.application.mainLock:
                self.show_status("Animating")
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
                zPosition = gameObject.worldPosition.z

        while self.application.tickPerf <= tickStart + phases[1]:
            with self.tick:
                with self.application.mainLock:
                    #
                    # Check physics is suspended, literally, and in effect.
                    self.assertFalse(gameObject.physics)
                    self.assertAlmostEqual(
                        gameObject.worldPosition.z, zPosition)
                    #
                    # Check animation is still in progress.
                    self.assertIsNotNone(
                        self.restInterface.rest_get(animationPath))
        with self.tick:
            lastTick = self.application.tickPerf

        while self.application.tickPerf <= tickStart + phases[2]:
            with self.tick:
                pass

        with self.tick:
            with self.application.mainLock:
                self.show_status("Finishing")
                #
                # Check physics has resumed, literally.
                self.assertTrue(
                    gameObject.physics
                    , "phase:{:.4f} last:{:.4f} current:{:.4f} {:.4f}".format(
                        tickStart + phases[2]
                        , lastTick, self.application.tickPerf
                        , self.application.tickPerf - lastTick))
                #
                # Check animation has been discarded.
                self.assertIsNone(self.restInterface.rest_get(animationPath))

        while self.application.tickPerf <= tickStart + phases[3]:
            with self.tick:
                if self.application.tickPerf - lastTick >= interval:
                    with self.application.mainLock:
                        #
                        # Check physics has resumed, in effect.
                        self.assertLess(
                            gameObject.worldPosition.z, zPosition
                            , "{:.4f} {:.4f} {:.4f}".format(
                                lastTick, self.application.tickPerf
                                , self.application.tickPerf - lastTick))
                        zPosition = gameObject.worldPosition.z
                    lastTick = self.application.tickPerf
