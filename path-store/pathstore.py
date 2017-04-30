#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store base module.

Path Store is a module for hierarchical data structures. It supports mixed
hierarchies of dictionary, list, and objects.

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

def str_quote(str_, quote):
    """Utility to add quotes to strings."""
    if isinstance(str_, str):
        return str_.join((quote, quote))
    else:
        return str(str_)

def pathify(path, quote='"'):
    """Generator that returns tuples of: path[N], str_quote(path[N])."""
    if path is not None:
        if isinstance(path, str):
            yield path, str_quote(path, quote)
        else:
            try:
                for item in path:
                    yield item, str_quote(item, quote)
            except TypeError:
                # Not a string, also not iterable. Probably a number.
                yield path, str(path)

class PointType(Enum):
    LIST = 1
    DICTIONARY = 2
    ATTR = 3

def descend_one(parent, specifier):
    if specifier is None:
        raise TypeError("Specifier must be string or numeric, but is None.")
    numeric = not isinstance(specifier, str)
    type = None
    if numeric:
        type = PointType.LIST
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
        type = PointType.DICTIONARY
        try:
            in_ = specifier in parent
        except TypeError:
            type = None
            in_ = False
        if in_:
            point = parent[specifier]
        elif hasattr(parent, specifier):
            point = getattr(parent, specifier)
            type = PointType.ATTR
        else:
            point = None
            
    return point, numeric, type

def descend(parent, path):
    for leg, legStr in pathify(path):
        point, numeric, type = descend_one(parent, leg)
        if type is None:
            raise TypeError(" ".join((
                "Couldn't get point for", legStr, "in", str(parent))))
        if point is None:
            error = " ".join(("No point for", legStr, "in", str(parent)))
            raise IndexError(error) if numeric else KeyError(error)
        parent = point
    return parent

def make_point(specifier, point=None):
    """Make or create a suitable point that can hold specifier."""
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

def insert(parent
           , path
           , value
           , enumerator=None
           , logger=None
           , point_maker=None
           ):
    def no_log(origin__name__, *args):
        pass
    if logger is None:
        logger = no_log
    logger(__name__, 'insert()', parent, path, value)
    
    def default_point_maker(path, index, point):
        return make_point(path[index], point)
    if point_maker is None:
        point_maker = default_point_maker

    if enumerator is None:
        enumerator = enumerate(pathify(path))

    try:
        index, (leg, legStr) = next(enumerator)
    except StopIteration:
        return value
    
    wasTuple = isinstance(parent, tuple)

    point, numeric, type = descend_one(parent, leg)
    if numeric and isinstance(parent, str):
        # Sorry, hack to force descent into a string to fail if setting.
        point = None
    
    logger(__name__, "{:2d} {}\n  {}\n  {}\n  {} {}".format(
        index, legStr, parent, point, str(numeric), str(type)))

    if type is None or point is None:
        parent = point_maker(path, index, parent)
        logger(__name__, 'insert made point', parent)
        point, numeric, type = descend_one(parent, leg)

    if type is None:
        raise AssertionError("".join((
            "type was None twice at ", str(parent)
            ," path:", str(path), " index:", str(index)
            , " leg:", legStr, ".")))

    value = insert(point, path, value, enumerator, logger, point_maker)

    # ToDo: optimise to set only if new value is different to current value.
    if type == PointType.ATTR:
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
