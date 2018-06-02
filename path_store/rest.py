#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
from path_store.blender_game_engine.gameobjectcollection import \
    GameObjectDict, GameObjectList

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
    
    def rest_delete(self, path):
        pathstore.delete(self._generic, path)
        return pathstore.delete(self.principal, path)
    
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
    def valuePath(self):
        return self._valuePath
    @valuePath.setter
    def valuePath(self, valuePath):
        self._valuePath = valuePath
    
    @property
    def subjectPath(self):
        return self._subjectPath
    @subjectPath.setter
    def subjectPath(self, subjectPath):
        self._subjectPath = subjectPath
        
    @property
    def subject(self):
        return self._subject

    # Override the setter for startTime to get the startValue.
    def _startTimeSetter(self, startTime):
        self.startValue = pathstore.get(self.store, self.valuePath)
        if self.subjectPath is not None:
            self._subject = pathstore.get(self.store, self.subjectPath)
            #
            # Next line will switch off physics.
            self._subject.beingAnimated = True
        Animation.startTime.fset(self, startTime)
    startTime = property(Animation.startTime.fget, _startTimeSetter)

    # Override the setter for nowTime to apply the animation.
    def _nowTimeSetter(self, nowTime):
        Animation.nowTime.fset(self, nowTime)
        pathstore.replace(self.store, self.get_value(), self.valuePath)
    nowTime = property(Animation.nowTime.fget, _nowTimeSetter)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._store = None
        self._valuePath = None
        self._subjectPath = None
        self._subject = None
    
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
    +-- 'root' Conventional item under which all the principal data sits.
        |
        +-- 'gameObjects' GameObjectList or GameObjectDict
            |
            +-- STRING or NUMBER
                Individual game objects.
    """
    
    @property
    def levels(self):
        return self._levels
    @levels.setter
    def levels(self, levels):
        self._levels = levels
    
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

        # if path[0] == self._gameObjectPath[0] and index == 3:
        #     if not isinstance(point, self.GameObject):
        #         point = self.GameObject()

        # Next check is for all the following conditions.
        #
        # -   We are creating a point for the root of the game object tree.
        # -   We know what type of path specifiers will be used at the next
        #     level down: strings or numbers.
        depth = self._gameObjectPathLen + self.levels
        if index == depth and len(path) > depth:
            # ToDo: Change this to access path[depth] and catch IndexError.
            check = True
            for checkIndex, checkPath in enumerate(self._gameObjectPath):
                if path[checkIndex] != checkPath:
                    check = False
                    break
            if check:
                pointType = (GameObjectDict if isinstance(path[depth], str)
                             else GameObjectList)
                if not isinstance(point, pointType):
                    point = pointType()
            # Don't return here, so that the super point_maker can populate the
            # collection with None placeholders if necessary.

        return super().point_maker(path, index, point)
    
    # Empty class for results of walk().
    class WalkResults:
        pass

    def _process_completed_animations(self, completions):
        for path, completed in completions:
            #
            # Replace completed animation objects with None in the path store,
            # for optimisation.
            self.rest_put(None, path)
            #
            # Check if there are still other animations going on for the same
            # subject.
            #
            # Check that there even is a subject.
            subject = completed.subject
            if subject is None:
                continue
            #
            # There is a subject. The code will walk the animations to see if
            # there are any more for the same subject. Whatever is discovered
            # will be set in a results object. (The other attributes of the walk
            # results object will still be set from the set_now_times first
            # walk.)
            self._walkResults.still = False
            self._walkResults.subject = subject
            #
            # Checking subroutine that can be passed to walk().
            def check(point, path, results):
                if point is None:
                    return
                if point.subject is results.subject and not point.complete:
                    results.still = True
                    raise StopIteration
            self.rest_walk(check, self._animationPath, self._walkResults)
            #
            # If there are no other animations: restore physics to the subject
            # and reset its rotation overrides.
            if not self._walkResults.still:
                subject.beingAnimated = False

    def set_now_times(self, nowTime):
        '''\
        Applies nowTime to everything under the 'animations' path. Returns a
        tuple of:
        
        -   Boolean for whether there were any completions this time.
        -   A copy of the animation path store structure with either None,
            "Complete", or "Incomplete" at each node.
        '''
        #
        # The code will walk the animations store twice. First to set the now
        # time, second to remove any completed animations. The walk results
        # object is used to collect the outcome.
        #
        # `completions` will be a list of tuples representing animations that
        # completed due to setting the now time. In each tuple:
        #
        # -   First element is the path, as a list.
        # -   Second element is the Animation instance.
        self._walkResults.completions = []
        #
        # `completionsLog` will be a copy of the animation path store structure
        # with either None, "Complete", or "Incomplete" at each node.
        self._walkResults.completionsLog = None
        #
        self._walkResults.anyCompletions = False
        #
        # Checking subroutine that will be passed to walk().
        def set_now(point, path, results):
            if point is not None and not point.complete:
                # Setting nowTime in a PathAnimation has the side effect of
                # applying the animation, which could have the further side
                # effect of completing the animation.
                point.nowTime = nowTime
                if point.complete:
                    results.anyCompletions = True
                    results.completions.append((path[:], point))
            logValue = None if point is None else (
                "Complete" if point.complete else "Incomplete")
            results.completionsLog = pathstore.merge(
                results.completionsLog, logValue, path)
        self.rest_walk(set_now, self._animationPath, self._walkResults)
        #
        # In theory, the processing in the following could be done in the
        # previous walk. However, it uses walk() to check for other animations
        # of the same subject, and it seemed a bit hazardous to kick off other
        # walks within a walk. Anyway, this is the second walk.
        self._process_completed_animations(self._walkResults.completions)
        
        return (
            self._walkResults.anyCompletions, self._walkResults.completionsLog)
    
    @property
    def animationPath(self):
        return self._animationPath

    # No point having a class here actually because a GameObject can only be
    # constructed with a bge.types.KX_GameObject instance.
    #
    # @property def GameObject(self):
    #     return self._GameObject
    # @GameObject.setter
    # def GameObject(self, GameObject):
    #     self._GameObject = GameObject
    
    @property
    def gameObjectPath(self):
        return self._gameObjectPath
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._GameObject = None
        self._levels = 0
        
        self._walkResults = self.WalkResults()
        #
        # Set and populate conventional paths.
        self._animationPath = ('animations',)
        self._gameObjectPath = ('root', 'gameObjects')
        self._gameObjectPathLen = len(self._gameObjectPath)
        for path in (self.animationPath, ): #self.gameObjectPath):
            self.rest_put(None, path)


# Do:
#
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.

# Import some classes from the Blender mathutils module, so that values of these
# types can be detected by GET. They need to be converted into list()s so that
# they can be JSON dumped.
# from mathutils import Vector, Matrix, Quaternion


