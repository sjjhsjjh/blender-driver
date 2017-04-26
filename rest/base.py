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
    
    def rest_traverse(self, path, creating=False):
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
            return self._list
            # return list(
            #     (None if _ is None else _.rest_get()) for _ in self._list)
        
        if self._dict is not None:
            return self._dict
            # return_ = {}
            # for key in self._dict:
            #     return_[key] = self._dict[key].rest_get()
            # return return_
        
        return None
    
    class PointType(Enum):
        LIST = 1
        DICTIONARY = 2
        ATTR = 3
    
    @staticmethod
    def get_point(parent, specifier):
        if specifier is None:
            raise TypeError("Specifier must be string or numeric,"
                            " cannot be None.")
        numeric = not isinstance(specifier, str)
        type = None
        if numeric:
            type = RestInterface.PointType.LIST
            try:
                point = parent[specifier]
            except IndexError:
                point = None
            except TypeError:
                type = None
                point = None
        else:
            type = RestInterface.PointType.DICTIONARY
            try:
                in_ = specifier in parent
            except TypeError:
                type = None
                in_ = False
            if in_:
                point = parent[specifier]
            elif hasattr(parent, specifier):
                point = getattr(parent, specifier)
                type = RestInterface.PointType.ATTR
            else:
                point = None
                
        return point, numeric, type
    
    def create_point(self, path, index, numeric, parent=None):
        """
        Default create_point, which can be overridden.
        """
        if numeric:
           return []
        else:
            return {}
        # return None
    
    def create_tree(self, value, path, index, numeric):
        parent = self.create_point(path, index, numeric)
        # Recurse if parent is None.
        pass
    
    def rest_put(self, value, path=None):
        self.verbosely('rest_put', value, path)
        length = (0 if path is None else
                  # 1 if isinstance(path, str) else
                  len(path))



        parent = self.principal
        leg = None
        point = None
        type = None
        for index in range(length):
            leg = path[index]
            legStr = leg.join(('"', '"')) if isinstance(leg, str) else str(leg)
            self.verbosely(
                "{:2d} {}\n  {}\n  {}".format(index, legStr, parent, point))


            # It's OK for parent to be None when index is zero.


            point, numeric, type = RestInterface.get_point(parent, leg)
            
            if type is None:
                value = self.create_tree(value, path, index, numeric)
                self.verbosely("Inserting", tree)
                # if index == 0:
                #     self.principal = tree
                #     # if tree is None:
                #     #     if numeric:
                #     #         self.verbosely('Inserting list.')
                #     #         self._list = point
                #     #         parent = self._list
                #     #     else:
                #     #         self.verbosely('Inserting dictionary.')
                #     #         self._dict = point
                #     #         parent = self._dict
                #     # else:
                #     #     self.principal = point
                #     #     parent = self.principal
                # else:
                #     # leg is numeric or string.
                #     parent[leg] = point
                break

                # point, numeric, type = RestInterface.get_point(parent, leg)

            # if type is None:
            #     raise AssertionError("type was None twice.")
            
            if point is None:
                if type == RestInterface.PointType.LIST:
                    self.verbosely('Extending list.')
                    parent.extend([None] * ((leg - len(parent)) + 1))
                else:
                    raise NotImplementedError()
                # elif type == RestInterface.PointType.DICTIONARY:
                    # self.verbosely('Extending dictionary.')
                    # parent[leg] = None
                point, numeric, type = RestInterface.get_point(parent, leg)

            if type is None:
                raise AssertionError("type was None after point was None.")
            
            

            
            # If it doesn't, create a suitable point that can contain leg.
            # Default suitable point is determined by the type of leg:
            # -   dict if string.
            # -   list if numeric.
            # Have an overridable function that returns the new point.
            # Maybe make RestInterface override all the __getitem__ family so
            # that it can present as an array or dictionary.
            
            
            # if isinstance(leg, str):
            #     if restDescent:
            #         if point.principal is None:
            #             if point._dict is None:
            #                 self.verbosely('Adding dictionary', id(point))
            #                 point._dict = {}
            #             if leg not in point._dict:
            #                 point._dict[leg] = RestInterface()
            #             point = point._dict[leg]
            #         else:
            #             restDescent = False
            #             parent = point.principal
            #             point, setattr_ = RestInterface.get_key_attr(
            #                 parent, leg)
            #     else:
            #         point, setattr_ = RestInterface.get_key_attr(point, leg)
            # else:
            #     # Assume integer.
            #     setattr_ = False
            #     if restDescent:
            #         if point.principal is None:
            #             if point._list is None:
            #                 self.verbosely('Adding list', id(point))
            #                 point._list = []
            #             if len(point._list) <= leg:
            #                 self.verbosely('Extending list', id(point))
            #                 point._list.extend([None] * (
            #                     (leg - len(point._list)) + 1))
            #             if point._list[leg] is None:
            #                 point._list[leg] = RestInterface()
            #             point = point._list[leg]
            #         else:
            #             # Assume principal is a list and descend into it.
            #             restDescent = False
            #             parent = point.principal
            #             point = point.principal[leg]
            #     else:
            #         point = point[leg]

        if type is None:
            parent.principal = value
        elif type == RestInterface.PointType.ATTR:
            setattr(parent, leg, value)
        else:
            # leg could be numeric or string; parent could be list or dict.
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