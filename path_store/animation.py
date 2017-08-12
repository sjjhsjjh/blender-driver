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
# Local imports, would go here.

class Animation(object):

    # def restAnimate(self, animation):
    #     """Execute one cycle of an animation. Return True if the animation
    #     should continue after this cycle, or False otherwise."""
    #     ret = True
    #     val = getattr(self, animation['property'])
    #     inc = animation['increment']
    #     target = None
    #     if 'target' in animation:
    #         target = animation['target']
    # 
    #     if animation['property'] in self.restPropertiesAngular:
    #         newval = val + inc
    #         if target is not None:
    #             adjval = (val - target) % 360
    #             adjnewval = (newval - target) % 360
    #     
    #             if \
    #                 adjval == 0 or \
    #                 (inc > 0 and adjnewval <= adjval) or \
    #                 (inc < 0 and adjnewval >= adjval) \
    #             :
    #                 newval = target
    #                 ret = False
    # 
    #     else:
    #     setattr(self, animation['property'], newval)


#     Animation class has following properties ...
#
#     -   Type of animation: linear or angular.
#

    
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
        increment = (self.nowTime - self.startTime) * self.speed
        start = self.startValue
        target = self.targetValue
        if target is not None:
            if (
                (target > start and increment < 0)
                or (target < start and increment > 0)
               ):
                increment *= -1

        nowValue = start + increment

        if target is not None:
            if (
                (start <= target and nowValue >= target)
                or (start >= target and nowValue <= target)
               ):
                nowValue = target
                self._complete = True
    
        return nowValue

    def __init__(self):
        # self._type = None

        self._speed = None
        self._startValue = None
        self._startTime = None
        self._nowTime = None
        self._targetValue = None

        self._complete = False
