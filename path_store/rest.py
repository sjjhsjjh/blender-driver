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
# Local imports.
#
# Path Store module.
from . import pathstore



# Import some classes from the Blender mathutils module, so that values of these
# types can be detected by GET. They need to be converted into list()s so that
# they can be JSON dumped.
# from mathutils import Vector, Matrix, Quaternion

class RestMethod(Enum):
    DELETE = 1
    GET    = 2
    PATCH  = 3
    POST   = 4
    PUT    = 5

class RestInterface(object):
    @property
    def principal(self):
        return self._principal

    def verbosely(self, origin__name__, *args):
        """Print, if verbose. Always pass __name__ as the first argument."""
        if not self.verbose:
            return False
        # Komodo Edit flags the next line as an error but it's fine.
        print(origin__name__, *args)
        return True

    def point_maker(self, path, index, point):
        """Default point_maker, which can be overridden so that a subclass can
        have custom points in the path store.
        """
        return pathstore.default_point_maker(path, index, point)
    
    def rest_patch(self, value, path=None):
        self.verbosely(__name__, 'rest_patch', value, path)
        self._principal = pathstore.merge(
            self._principal, value, path
            , point_maker=self.point_maker, logger=self.verbosely)

    def rest_put(self, value, path=None):
        self.verbosely(__name__, 'rest_put', value, path)
        self._principal = pathstore.replace(
            self._principal, value, path
            , point_maker=self.point_maker, logger=self.verbosely)

    def rest_get(self, path=None):
        return pathstore.get(self.principal, path)
    
    def __init__(self):
        self.verbose = False
        self._principal = None


class RestBGEObject(RestInterface):
    
    def rest_POST(self, parameters):
        # Add an object to the scene.
        # Make the object instance be self.restPrincipal
        # call super().restPOST(parameters) which will set each thing in the
        # parameters dictionary.
        pass


# Do:
#
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.
# -   BGE interface will be like: create a KXGameObject, create a wrapper around
#     it, set the wrapper as principal.
# -   How to do applyImpulse? Maybe by POST to an "impulse" property, that gets
#     pushed down to a setter, that executes the applyImpulse and discards its
#     own value.