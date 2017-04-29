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
    
    @staticmethod
    def str_quote(str_, quote):
        if isinstance(str_, str):
            return str_.join((quote, quote))
        else:
            return str(str_)
    
    @staticmethod
    def pathify(path, quote='"'):
        if path is not None:
            if isinstance(path, str):
                yield path, RestInterface.str_quote(path, quote)
            else:
                try:
                    for item in path:
                        yield item, RestInterface.str_quote(item, quote)
                except TypeError:
                    # Not a string, also not iterable. Probably a number.
                    yield path, str(path)
    
    class PointType(Enum):
        LIST = 1
        DICTIONARY = 2
        ATTR = 3
    
    @staticmethod
    def get_point(parent, specifier):
        if specifier is None:
            raise TypeError("Specifier must be string or numeric, but is None.")
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
            except KeyError:
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
    
    @staticmethod
    def get_path(parent, path):
        for leg, legStr in RestInterface.pathify(path):
            point, numeric, type = RestInterface.get_point(parent, leg)
            if type is None:
                raise TypeError(" ".join((
                    "Couldn't get point for ", legStr, "in", str(parent))))
            if point is None:
                error = " ".join((
                    "No point for", legStr, "in", str(parent)))
                raise IndexError(error) if numeric else KeyError(error)
            parent = point
        
        return parent
    
    def make_point(self, path, index, point=None):
        """
        Default make_point, which can be overridden.
        """
        specifier = path[index]
        if isinstance(specifier, str):
            try:
                if specifier not in point:
                    point[specifier] = None
                return point
            except TypeError:
                # None, or not a dictionary, so create a dictionary.
                return {specifier: None}
        else:
            # It would be super-neat to do this be try:ing the len() and then
            # except TypeError: to set length zero. The problem is that all
            # iterables are OK for len(), so string and dictionary values don't
            # generate the exception.
            length = 0
            if isinstance(point, tuple) or isinstance(point, list):
                length = len(point)
                if length > specifier:
                    return point
            extension = (None,) * ((specifier - length) + 1)
            if isinstance(point, tuple):
                return point + extension
            try:
                point.extend(extension)
                return point
            except AttributeError:
                # None or not a list, so create a list.
                return list(extension)
    
    def _set_path(self, parent, path, value, enumerator):
        self.verbosely(__name__, 'set_path()', parent, path, value)
        point0 = None
        point1 = parent
        return_ = None
        type = None
        lastLeg = None
        while True:
            try:
                index, (leg, legStr) = next(enumerator)
                lastLeg = leg
            except StopIteration:
                break

            point0 = point1
            point1, numeric, type = RestInterface.get_point(point0, leg)
            if numeric and isinstance(point0, str):
                # Sorry, have to force descent into a string to fail.
                point1 = None
            self.verbosely(
                "{:2d} {}\n  {}\n  {}\n  {} {}".format(
                    index, legStr, point0, point1 , str(numeric), str(type)))

            if type is None or point1 is None:
                point0 = self.make_point(path, index, point0)
                point1, numeric, type = RestInterface.get_point(point0, leg)

            if type is None:
                raise AssertionError("".join((
                    "type was None twice at ", str(point0)
                    ," path:", str(path), " index:", index
                    , " leg:", legStr, ".")))
            
            if return_ is None:
                return_ = point0
                self.verbosely(__name__, 'set_path set return', return_)

            if point1 is None:
                # Nowhere to descend.
                #
                # Generate a new tree, recursively.
                value = self._set_path(None, path, value, enumerator)
                #
                # Break out of the loop so that the value setting code inserts
                # the new tree.
                break

        self.verbosely(__name__, 'set_path loop finished'
                       , lastLeg, point0, return_)
        if lastLeg is None:
            return_ = value
        elif type == RestInterface.PointType.ATTR:
            setattr(point0, lastLeg, value)
        else:
            # leg could be numeric or string; parent could be list or dict ...
            #
            # ... or tuple. If it's a tuple then make it into a list, and
            # therefore mutable, first. Also, if the tuple is what we were going
            # to return, change that too.
            wasReturn = (point0 is return_)
            if isinstance(point0, tuple):
                point0 = list(point0)
                if wasReturn:
                    return_ = point0
                    self.verbosely(__name__, 'set_path set wasReturn', return_)
            point0[lastLeg] = value

        if isinstance(parent, tuple) and isinstance(return_, list):
            return_ = tuple(return_)
        return return_
    
    def set_path(self, parent, path, value):
        return self._set_path(
            parent, path, value, enumerate(RestInterface.pathify(path)))

    def rest_put(self, value, path=None):
        self.verbosely('rest_put', value, path)

        self.principal = self.create_tree(self.principal, path, value)

        parent = None
        leg = None
        point = self.principal
        type = None
        for index, leg in enumerate(paths(path)):
            legStr = leg.join(('"', '"')) if isinstance(leg, str) else str(leg)
            self.verbosely(
                "{:2d} {}\n  {}\n  {}".format(index, legStr, parent, point))


            # It's OK for parent to be None when index is zero.
            parent = point


            point, numeric, type = RestInterface.get_point(parent, leg)
            
            if type is None:
                value = self.create_tree(value, path, index, numeric)
                self.verbosely("Tree value", value)
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
                raise NotImplementedError()
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

        if parent is None:
            self.principal = value
        elif type == RestInterface.PointType.ATTR:
            setattr(parent, leg, value)
        else:
            # leg could be numeric or string; parent could be list or dict.
            parent[leg] = value

    def rest_get(self, path=None):
        return RestInterface.get_path(self.principal, path)
    
    def __init__(self):
        self.verbose = False
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