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
    
    def verbosely(self, origin__name__, *args):
        """Print, if verbose. Always pass __name__ as the first argument."""
        if not self.verbose:
            return False
        print(origin__name__, *args)
        return True

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

    @property
    def principal(self):
        return self._principal
    @principal.setter
    def principal(self, principal):
        self._principal = principal
    
    # For POST and PUT only?
    principalClass = None
    
    def rest_get(self):
        if self.principal is not None:
            return self.principal
        
        if self._list is not None:
            return list(
                (None if _ is None else _.rest_get()) for _ in self._list)
        
        if self._dict is not None:
            return_ = {}
            for key in self._dict:
                return_[key] = self._dict[key].rest_get()
            return return_
        
        return None
    
    @staticmethod
    def get_key_attr(object, specifier):
        if hasattr(object, specifier):
            return getattr(object, specifier), True
        else:
            return object[specifier], False
    
    def rest_put(self, value, paths=None):
        self.verbosely('rest_put', value, paths)
        point = self
        length = (0 if paths is None else
                  # 1 if isinstance(paths, str) else
                  len(paths))
        parent = None
        leg = None
        point = self
        setattr_ = False
        restDescent = True
        for index in range(length):
            leg = paths[index]
            legStr = leg.join(('"', '"')) if isinstance(leg, str) else str(leg)
            self.verbosely(
                "{:2d} {}\n  {}\n  {}\n   {}".format(
                index, legStr, parent, point, point._list))

            parent = point
            
            # Check is point has leg.
            # If it doesn't, create a suitable point that can contain leg.
            
            
            if isinstance(leg, str):
                if restDescent:
                    if point.principal is None:
                        if point._dict is None:
                            self.verbosely('Adding dictionary', id(point))
                            point._dict = {}
                        if leg not in point._dict:
                            point._dict[leg] = RestInterface()
                        point = point._dict[leg]
                    else:
                        restDescent = False
                        parent = point.principal
                        point, setattr_ = RestInterface.get_key_attr(
                            parent, leg)
                else:
                    point, setattr_ = RestInterface.get_key_attr(point, leg)
            else:
                # Assume integer.
                setattr_ = False
                if restDescent:
                    if point.principal is None:
                        if point._list is None:
                            self.verbosely('Adding list', id(point))
                            point._list = []
                        if len(point._list) <= leg:
                            self.verbosely('Extending list', id(point))
                            point._list.extend([None] * (
                                (leg - len(point._list)) + 1))
                        if point._list[leg] is None:
                            point._list[leg] = RestInterface()
                        point = point._list[leg]
                    else:
                        # Assume principal is a list and descend into it.
                        restDescent = False
                        parent = point.principal
                        point = point.principal[leg]
                else:
                    point = point[leg]
                    

        if setattr_:
            setattr(parent, leg, value)
        else:
            if restDescent:
                point.principal = value
            else:
                parent[leg] = value
            

    def __init__(self):
        self.verbose = False
        self._dict = None
        self._list = None
        self._principal = None

    # def __str__(self):
    #     return str(self.restPrincipal)

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