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

# Do:
#
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.
# -   Animation
