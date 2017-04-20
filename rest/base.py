#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""RESTful interfaces module.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)


#
# Module for enum type.
# https://docs.python.org/3.5/library/enum.html
from enum import Enum


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
    
    def rest_traverse1(self, path, creating=False):
        """Get one item."""
        pass
    
    def rest_traverse(self, paths, creating=False):
        """Descend the structure."""
        pass


    def rest_PATCH(self, valueDict):
        for key, value in valueDict:
            if hasattr(self.restPrincipal, key):
                setattr(self.restPrincipal, key, value)
            else:
                # If key is numeric
                # If my dictionary has it
                pass
        pass

    
    restPrincipal = None
    
    # For POST and PUT only?
    principalClass = None 

    def __init__(self):
        self._restMap = None


# RestInterface with dictionary and array in each node, or RestDictionary and
# RestArray as subclasses? Could even have RestDictionary and RestArray as
# principals.


class RestBGEObject(RestInterface):
    
    def rest_POST(self, parameters):
        # Add an object to the scene.
        # Make the object instance be self.restPrincipal
        # call super().restPOST(parameters) which will set each thing in the
        # parameters dictionary.
        pass


# Do:
#
# -   Test module in the same directory.
# -   Principal objects can't be hierarchical. To create hierarchies with types
#     and property names, create a RestInterface subclass. Although, it would be
#     possible to descend by getattr(). 
# -   Test: Create a RestInterface and attach another object as principal.
# -   Test: Build an array, by setting [0] as path.
# -   Double traversal by setting restParent when creating a RestInterface.
# -   restGetCache that contains only data that has been accessed through the
#     RestInterface. But have an API to load the cache maybe.
# -   BGE interface will be like: create a KXGameObject, create a wrapper around
#     it, set the wrapper as principal.
# -   How to do applyImpulse? Maybe by POST to an "impulse" property, that gets
#     pushed down to a setter, that executes the applyImpulse and discards its
#     own value.