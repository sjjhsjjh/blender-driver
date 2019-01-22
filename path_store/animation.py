#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for value animation.


Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for mathematical operations, used by angular animation.
# https://docs.python.org/3.5/library/math.html
from math import fmod
#
# Local imports, would go here.

class Animation(object):
    @property
    def startTime(self):
        return self._startTime
    @startTime.setter
    def startTime(self, startTime):
        self._startTime = startTime
        self._completeTime = None
    
    @property
    def implicitStart(self):
        """\
        If True, setting nowTime also sets startTime if startTime is None.
        If False, setting nowTime has no affect on startTime. This means that
        startTime must be set explicitly before the first call to get_value().
        """
        return self._implicitStart
    @implicitStart.setter
    def implicitStart(self, implicitStart):
        self._implicitStart = implicitStart
    
    @property
    def stopped(self):
        return self._stopped
    @stopped.setter
    def stopped(self, stopped):
        self._stopped = stopped
    
    @property
    def startValue(self):
        return self._startValue
    @startValue.setter
    def startValue(self, startValue):
        self._startValue = startValue
        self._completeTime = None
    
    @property
    def nowTime(self):
        return self._nowTime
    @nowTime.setter
    def nowTime(self, nowTime):
        if self.startTime is None and self.implicitStart:
            self.startTime = nowTime
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
        self._completeTime = None
        
    @property
    def userData(self):
        return self._userData
    @userData.setter
    def userData(self, userData):
        self._userData = userData
        
    @property
    def modulo(self):
        """\
        Set this to implement angular animations, as follows.
        
        -   360 for an angular degrees property.
        -   2.0 * pi or radians(360) for an angular radians property.
        -   0 or None for a linear property.
        """
        return self._modulo
    @modulo.setter
    def modulo(self, modulo):
        self._modulo = modulo
        self._completeTime = None
    
    @property
    def complete(self):
        """True if the animation has reached its target, or False otherwise."""
        return self._completeTime is not None
        
    @property
    def completionTime(self):
        """\
        The nowTime value from when the animation reached its target, or None.
        """
        return self._completeTime
        
    # This is unused in the current programming interface, and hence commented
    # out.
    # @property
    # def change(self):
    #     return (self.nowTime - self.startTime) * self._speed
    
    # Next thing isn't a property because getting its value has a side effect:
    # the completion time could be set.
    def get_value(self):
        """\
        Get the animated value be, based on all the following.
        
        -   Start value.
        -   Start time.
        -   Now time.
        -   Speed.
        -   Target value, if specified.
        
        If there is a target value, and it has been reached, sets the completion
        time.
        """
        #
        # Convenience variables.
        increment = (self.nowTime - self.startTime) * self.speed
        start = self.startValue
        target = self.targetValue
        modulo = self.modulo
        if modulo == 0:
            modulo = None
        #
        # Check whether this is a simple animation, i.e. one without a target or
        # one that will reach its target by repeated application of the
        # increment.
        simple = (
            (target is None)
            or (target > start and increment > 0)
            or (target < start and increment < 0))
        #
        # Negate the increment, if necessary.
        if (not simple) and (modulo is None):
            increment *= -1
        #
        # Generate a candidate animated value.
        nowValue = start + increment
        #
        # Apply the target value, if any.
        # Note that fmod is generally better but can return negative values,
        # whcih aren't wanted here. Every fmod is followed by a check for that.
        if target is None:
            if modulo is not None:
                nowValue = fmod(nowValue, modulo)
                if nowValue < 0.0:
                    nowValue += modulo
            # If target is None and modulo is None, the candidate value doesn't
            # need adjustment.
        else:
            if simple or (modulo is None):
                if (
                    (start <= target and nowValue >= target)
                    or (start >= target and nowValue <= target)
                ):
                    nowValue = target
                    self._completeTime = self.nowTime
            else:
                adjustedStart = fmod(start - target, modulo)
                if adjustedStart < 0.0:
                    adjustedStart += modulo
                adjustedNow = fmod(nowValue - target, modulo)
                if adjustedNow < 0.0:
                    adjustedNow += modulo

                if (
                    (adjustedStart == 0.0)
                    or (increment > 0.0 and adjustedNow <= adjustedStart)
                    or (increment < 0.0 and adjustedNow >= adjustedStart)
                ):
                    nowValue = target
                    self._completeTime = self.nowTime
        return nowValue

    def __init__(self):
        self._modulo = None
        self._userData = None
        
        self._speed = None
        self._startValue = None
        self._startTime = None
        self._implicitStart = True
        self._nowTime = None
        self._targetValue = None
        self._stopped = False

        self._completeTime = None
