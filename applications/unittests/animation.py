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
            self.add_phase_starts(addition / speed)
            self.add_phase_offsets(1.0)
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
            #
            # -   Retrieves the start value.
            # -   Clears the complete state.
            animationPath.append('startTime')
            self.restInterface.rest_put(
                self.application.tickPerf, animationPath)
            del animationPath[-1]
        
        while self.up_to_phase(1):
            with self.tick, self.application.mainLock:
                if self.up_to_phase(0):
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
        
        with self.tick, self.application.mainLock:
            # Next line makes the object fall away, which is nice.
            gameObject.physics = True

    def test_physics(self):
        '''Test that physics gets suspended during animation.'''
        zPosition = None
        gameObject = None
        self.add_phase_starts(1.0, 5.0, 10.0)
        turn = radians(135.0)
        animation = None
        animationPath = None
        
        with self.tick:
            lastTick = self.application.tickPerf
            with self.application.mainLock:
                gameObject = self.add_test_object()
                gameObject.physics = False
                gameObject.worldPosition.z = 6.0
                self.show_status("Created")
    
                self.restInterface.rest_put(gameObject, self.objectPath)
    
                valuePath = tuple(self.objectPath) + ('rotation', 'z')
                value = self.restInterface.rest_get(valuePath)
    
                #
                # Assemble the animation in a dictionary. Note that there is a
                # subjectPath so that physics gets suspended and resumed.
                animation = {
                    'modulo': radians(360.0),
                    'valuePath': valuePath,
                    'subjectPath': self.objectPath,
                    'speed': turn / (self.phases[1] - self.phases[0]),
                    'targetValue': value + turn}
                #
                # There is up to one animation for this test. It has to have a
                # number though, so that the point maker sees it as deep enough.
                animationPath = ['animations', self.id(), 0]

                zPosition = gameObject.worldPosition.z
                gameObject.physics = True
                self.show_status("Falling")

        while self.up_to_phase(0):
            with self.tick, self.application.mainLock:
                # Check that its z position is falling every tick.
                # Next is LessEqual because sometimes it doesn't fall.
                self.assertLessEqual(gameObject.worldPosition.z, zPosition)
                zPosition = gameObject.worldPosition.z
                lastTick = self.application.tickPerf

        with self.tick, self.application.mainLock:
            self.show_status("Animating")
            #
            # Insert the animation. The point maker will set the store
            # attribute and suspend physics.
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

        while self.up_to_phase(1):
            with self.tick, self.application.mainLock:
                #
                # Check that time marches on.
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf
                #
                # Check physics is suspended, literally, and in effect.
                self.assertFalse(gameObject.physics)
                self.assertAlmostEqual(
                    gameObject.worldPosition.z, zPosition)
                #
                # Check animation is still in progress.
                self.assertIsNotNone(
                    self.restInterface.rest_get(animationPath))
        #
        # There now follows a short intermission.
        #
        # Wait for some ticks. In theory maybe it should only ever have to wait
        # for one tick but in practice this test is sometimes ahead of the
        # application thread.
        for waitTick in range(3):
            with self.tick, self.application.mainLock:
                self.show_status("Waiting {}".format(waitTick))
                #
                # Check that time marches on.
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf
                #
                animationNow = self.restInterface.rest_get(animationPath)
                print("waitTick:{:d} {:.4f} {} {} {}".format(
                    waitTick, self.application.tickPerf, self.id()
                    , self.application.lastCompletion
                    , (None if animationNow is None else animationNow.complete)
                    ))
                #
                # Check if completions have been processed.
                lastCompletionTick = self.application.lastCompletionTick
                if lastCompletionTick is None:
                    continue
                if lastCompletionTick < self.application.tickPerf:
                    continue
                if animationNow is None:
                    break
        #
        # Intermission over. Resume checking.
        with self.tick, self.application.mainLock:
            #
            # Check animation has been discarded.
            self.assertIsNone(self.restInterface.rest_get(animationPath))
            #
            # Check physics has resumed, literally.
            self.assertTrue(gameObject.physics)
            self.show_status("Finishing")
        while self.up_to_phase(2):
            #
            # Check physics has resumed, in effect.
            with self.tick, self.application.mainLock:
                self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf
                #
                # Check that its z position is falling every tick.
                # Next is LessEqual because sometimes it doesn't fall. These are
                # called fall errors. They are scrutinised in a different unit
                # test: TestGameObject.test_physics
                self.assertLessEqual(gameObject.worldPosition.z, zPosition)
                zPosition = gameObject.worldPosition.z
