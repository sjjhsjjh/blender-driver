#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store REST module.


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
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Local imports.
#
# Path Store module.
try:
    import path_store.pathstore
    pathstore = path_store.pathstore
except ImportError:
    import pathstore

from path_store.animation import Animation

class RestMethod(Enum):
    DELETE = 1
    GET    = 2
    PATCH  = 3
    POST   = 4
    PUT    = 5

class RestInterface(object):
    """Class for a RESTful interface onto a principal object, implemented by
    Path Store.
    """
    @property
    def principal(self):
        return self._principal

    def point_maker(self, path, index, point):
        """Default point_maker, which can be overridden so that a subclass can
        have custom points in the path store.
        """
        return pathstore.default_point_maker(path, index, point)
    
    def rest_patch(self, value, path=None):
        log(DEBUG, '({}, {})', value, path)
        self._principal = pathstore.merge(
            self._principal, value, path, point_maker=self.point_maker)

    def rest_put(self, value, path=None):
        log(DEBUG, '({}, {})', value, path)
        self._principal = pathstore.replace(
            self._principal, value, path, point_maker=self.point_maker)

    def rest_get(self, path=None):
        return pathstore.get(self.principal, path)
    
    def __init__(self):
        self._principal = None

class PathAnimation(Animation):

    @property
    def store(self):
        return self._store
    @store.setter
    def store(self, store):
        self._store = store
    
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, path):
        self._path = path

    # Override the setter for startTime to get the startValue.
    def _startTimeSetter(self, startTime):
        self.startValue = pathstore.get(self.store, self.path)
        Animation.startTime.fset(self, startTime)
    startTime = property(Animation.startTime.fget, _startTimeSetter)

    # Override the setter for nowTime to apply the animation.
    def _nowTimeSetter(self, nowTime):
        Animation.nowTime.fset(self, nowTime)
        pathstore.replace(self.store, self.get_value(), self.path)
    nowTime = property(Animation.nowTime.fget, _nowTimeSetter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._store = None
        self._path = None

    # It could be handy to cache the parent of the animated point, in order to
    # minimise the number of path descents. However, it might be the case that
    # an object in the path has been replaced in between iterations of the
    # animation. That would stymie caching.


class AnimatedRestInterface(RestInterface):
    """RestInterface with the following items at the top level.
    
    -   'animations' is a collection of animations.
    -   'nowTime' is a shorthand, the setting of which sets the nowTime in all
        the animations in the collection.
    -   'root' is the conventional item for the principal data.
    """
    
    # Override
    def point_maker(self, path, index, point):
        log(DEBUG, "({}, {}, {}) AnimatedRestInterface", path, index, point)
        #
        # Next line has index == 2, which is one more than the level at which
        # the animation object is to be created. The index == 1 level can get a
        # None in order to build the array or dictionary.
        if path[0] == 'animations' and index == 2:
            if not isinstance(point, PathAnimation):
                point = PathAnimation()
            point.store = self.principal
            return point

        return super().point_maker(path, index, point)
    
    @property
    def nowTime(self):
        return self._nowTime
    @nowTime.setter
    def nowTime(self, nowTime):
        self._nowTime = nowTime
        try:
            animations = self.rest_get('animations')
        except KeyError:
            animations = tuple()
        completions = 0
        for animation in animations:
            if animation is not None and not animation.complete:
                # Setting nowTime has the side effect of applying the animation.
                animation.nowTime = nowTime
                if animation.complete:
                    completions += 1
        if completions > 0:
            log(INFO, "Animations:{}.".format(list(
                None if _ is None else "Complete" if _.complete else "Incomplete" for _ in animations)))

# Do:
#
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.

# Import some classes from the Blender mathutils module, so that values of these
# types can be detected by GET. They need to be converted into list()s so that
# they can be JSON dumped.
# from mathutils import Vector, Matrix, Quaternion


