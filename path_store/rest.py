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

def _generic_value(value):
    # The required test here is: can the value can be serialised into JSON?
    # That could be determined by attempting to serialise, for example by
    # calling json.dumps(value). It seems expensive to process the
    # serialisation, and then discard the result. Instead, the code just
    # checks the type of the value.
    if type(value) in (dict, list, tuple, str, int, float):
        return value
    if value is True or value is False or value is None:
        return value
    # Otherwise, assume it is a class instance and return an empty
    # dictionary.
    return {}
    
class RestInterface(object):
    """Class for a RESTful interface onto a principal object, implemented by
    Path Store.
    """
    @property
    def principal(self):
        return self._principal
    
    def get_generic(self, path=None):
        def populate(pointUnused, pathUnused, resultsUnused, second):
            return True, second

        if self.principal is not None:
            self._generic = pathstore.walk(
                self._generic, populate, path, second=self.principal)

        return pathstore.get(self._generic, path)

    def point_maker(self, path, index, point):
        """Default point_maker, which can be overridden so that a subclass can
        have custom points in the path store.
        """
        return pathstore.default_point_maker(path, index, point)
    
    def rest_patch(self, value, path=None):
        self._principal = pathstore.merge(
            self._principal, value, path, point_maker=self.point_maker)

    def rest_put(self, value, path=None):
        self._principal = pathstore.replace(
            self._principal, value, path, point_maker=self.point_maker)
        self._generic = pathstore.replace(
            self._generic, _generic_value(value), path)

    def rest_get(self, path=None):
        self._generic = pathstore.merge(self._generic, None, path)
        return pathstore.get(self.principal, path)
    
    def rest_walk(self, editor, path=None, results=None):
        return pathstore.walk(self.principal, editor, path, results)
    
    def __init__(self):
        self._principal = None
        self._generic = None

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
    
    |
    +-- 'animations'
    |   |
    |   +-- STRING
    |       |
    |       +-- STRING or NUMBER
    |           Individual animation.
    |
    +-- 'nowTime'
    |   Shorthand property, the setting of which sets the nowTime property in
    |   all the animations in the collection, above.
    |
    +-- 'root'
        Conventional item under which all the principal data sits.
    """
    
    # Override
    def point_maker(self, path, index, point):
        log(DEBUG, "({}, {}, {}) AnimatedRestInterface", path, index, point)
        #
        # Next line has index == 3, which is one more than the level at which
        # the animation object is to be created. The index < 3 levels can get a
        # None in order to build the array or dictionary.
        if path[0] == 'animations' and index == 3:
            if not isinstance(point, PathAnimation):
                point = PathAnimation()
            point.store = self.principal
            return point

        return super().point_maker(path, index, point)
    
    def set_now_times(self, nowTime):

        class Results:
            pass
        setResults = Results()
        setResults.completionsLog = None
        setResults.anyCompletions = False
        setResults.completions = []
            
        def set_now(point, path, results):
            if point is not None and not point.complete:
                # Setting nowTime has the side effect of applying the animation,
                # which could have the further side effect of completing the
                # animation.
                point.nowTime = nowTime
                if point.complete:
                    results.anyCompletions = True
                    results.completions.append((path[:], point))
            logValue = None if point is None else (
                "Complete" if point.complete else "Incomplete")
            results.completionsLog = pathstore.merge(
                results.completionsLog, logValue, path)
        
        error = None
        try:
            self.rest_walk(set_now, 'animations', setResults)
        except KeyError as keyError:
            # This error is raised if there isn't even an animations path, which
            # can be true during initialisation.
            error = keyError

        if setResults.anyCompletions:
            log(INFO, "Animations:{} {}.", error, setResults.completionsLog)
        
        return setResults.completions

# Do:
#
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.

# Import some classes from the Blender mathutils module, so that values of these
# types can be detected by GET. They need to be converted into list()s so that
# they can be JSON dumped.
# from mathutils import Vector, Matrix, Quaternion


