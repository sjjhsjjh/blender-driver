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
            # It would be super-neat to do this by try:ing the len() and then
            # except TypeError: to set length zero. The problem is that all
            # iterables are OK for len(), so string and dictionary values don't
            # generate the exception.
            length = 0
            if isinstance(point, (tuple, list)):
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
        self.verbosely(__name__, '_set_path()', parent, path, value)

        try:
            index, (leg, legStr) = next(enumerator)
        except StopIteration:
            return value
        
        wasTuple = isinstance(parent, tuple)

        point, numeric, type = RestInterface.get_point(parent, leg)
        if numeric and isinstance(parent, str):
            # Sorry, hack to force descent into a string to fail if setting.
            point = None
        
        self.verbosely(__name__,
            "{:2d} {}\n  {}\n  {}\n  {} {}".format(
                index, legStr, parent, point, str(numeric), str(type)))

        if type is None or point is None:
            parent = self.make_point(path, index, parent)
            self.verbosely(__name__, '_set_path made point', parent)
            point, numeric, type = RestInterface.get_point(parent, leg)

        if type is None:
            raise AssertionError("".join((
                "type was None twice at ", str(parent)
                ," path:", str(path), " index:", str(index)
                , " leg:", legStr, ".")))

        value = self._set_path(point, path, value, enumerator)

        # ToDo: optimise to set only if new value is different to current value.
        if type == RestInterface.PointType.ATTR:
            setattr(parent, leg, value)
        else:
            # leg could be numeric or string; parent could be list or dict ...
            #
            # ... or tuple. If it's a tuple then make it into a list, and
            # therefore mutable, first.
            if isinstance(parent, tuple):
                parent = list(parent)
            parent[leg] = value

        if wasTuple and isinstance(parent, list):
            parent = tuple(parent)
        
        return parent
    
    def set_path(self, parent, path, value):
        return self._set_path(
            parent, path, value, enumerate(RestInterface.pathify(path)))

    def rest_put(self, value, path=None):
        self.verbosely(__name__, 'rest_put', value, path)
        self.principal = self.set_path(self.principal, path, value)

    def rest_get(self, path=None):
        return RestInterface.get_path(self.principal, path)
    
    def __init__(self):
        self.verbose = False
        self._principal = None

    # def __str__(self):
    #     return str(self.principal)


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