#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for value animation.


Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for enum type.
# https://docs.python.org/3.5/library/enum.html
from enum import Enum
#
# Module for mathematical operations, used by angular animation.
# https://docs.python.org/3.5/library/math.html
from math import fmod, pi
#
# Local imports, would go here.

class AnimationType(Enum):
    LINEAR = 1
    ANGULAR = 2

class Animation(object):
    @property
    def animationType(self):
        return self._animationType
    @animationType.setter
    def animationType(self, animationType):
        """\
        Set to an AnimationType or the name of one of them: "LINEAR" or
        "ANGULAR".
        """
        if not isinstance(animationType, AnimationType):
            # Assume it's a string and the name of a type.
            animationType = AnimationType[animationType.upper()]
        
        self._animationType = animationType

    @property
    def startTime(self):
        return self._startTime
    @startTime.setter
    def startTime(self, startTime):
        self._startTime = startTime
        self._complete = False
    
    @property
    def startValue(self):
        return self._startValue
    @startValue.setter
    def startValue(self, startValue):
        self._startValue = startValue
        self._complete = False
    
    @property
    def nowTime(self):
        return self._nowTime
    @nowTime.setter
    def nowTime(self, nowTime):
        self._nowTime = nowTime
        
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, speed):
        self._speed = speed
        
    @property
    def targetValue(self):
        return self._targetValue
    @targetValue.setter
    def targetValue(self, targetValue):
        self._targetValue = targetValue
        self._complete = False
        
    @property
    def complete(self):
        """True if the animation has reached its target, or False otherwise."""
        return self._complete
        
    # This is unused in the current programming interface, and hence commented
    # out.
    # @property
    # def change(self):
    #     return (self.nowTime - self.startTime) * self._speed
    
    # Next thing isn't a property because getting its value has a side effect:
    # the complete flag could be set.
    def get_value(self):
        """Get the animated value be, based on:
        
        -   Start value.
        -   Start time.
        -   Now time.
        -   Speed.
        -   Target value, if specified.
        
        If there is a target value, and it has been reached, sets the complete
        flag.
        """
        #
        # Convenience variables.
        increment = (self.nowTime - self.startTime) * self.speed
        start = self.startValue
        target = self.targetValue
        #
        # Negate the increment, if necessary.
        if self.animationType is AnimationType.LINEAR and target is not None:
            if (
                (target > start and increment < 0)
                or (target < start and increment > 0)
            ):
                increment *= -1
        #
        # Generate a candidate animated value.
        nowValue = start + increment
        #
        # Apply the target value, if any.
        if target is not None:
            if self.animationType is AnimationType.ANGULAR:
                mod = pi * 2.0
                adjustedStart = fmod(start - target, mod)
                if adjustedStart < 0.0:
                    adjustedStart += mod
                adjustedNow = fmod(nowValue - target, mod)
                if adjustedNow < 0.0:
                    adjustedNow += mod

                if (
                    (adjustedStart == 0.0)
                    or (increment > 0.0 and adjustedNow <= adjustedStart)
                    or (increment < 0.0 and adjustedNow >= adjustedStart)
                ):
                    nowValue = target
                    self._complete = True
            elif self.animationType is AnimationType.LINEAR:
                if (
                    (start <= target and nowValue >= target)
                    or (start >= target and nowValue <= target)
                ):
                    nowValue = target
                    self._complete = True
            else:
                raise AssertionError(
                    "Unknown animation type:{}".format(self.animationType))
        return nowValue

    def __init__(self):
        # Default to linear animation.
        self._animationType = AnimationType.LINEAR

        self._speed = None
        self._startValue = None
        self._startTime = None
        self._nowTime = None
        self._targetValue = None

        self._complete = False

# class AnimationAngular(Animation):
#     
#     # Override.
#     def get_value(self):
#         #
#         # Convenience variables.
#         increment = (self.nowTime - self.startTime) * self.speed
#         start = self.startValue
#         target = self.targetValue
#         #
#         # Generate a candidate animated value.
#         nowValue = start + increment
#         #
#         # Apply the target value, if any.
#         if target is not None:
#         return nowValue
