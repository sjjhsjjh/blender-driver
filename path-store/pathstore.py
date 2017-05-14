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

def str_quote(str_, quote='"'):
    """Utility to add quotes to strings, but just stringify non-strings."""
    if isinstance(str_, str):
        return str_.join((quote, quote))
    else:
        return str(str_)

def pathify(path):
    """Generator that returns a list suitable for path store navigation:
    
    -   A zero-element list, if path is None.
    -   A one-element list, if path is a string or isn't iterable.
    -   A list of each item, otherwise.
    """
    if path is not None:
        if isinstance(path, str):
            yield path
        else:
            try:
                for item in path:
                    yield item
            except TypeError:
                yield path

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
    for leg in pathify(path):
        point, numeric, type = descend_one(parent, leg)
        if type is None:
            raise TypeError(" ".join((
                "Couldn't get point for", str_quote(leg), "in", str(parent))))
        if point is None:
            error = " ".join((
                "No point for", str_quote(leg), "in", str(parent)))
            raise IndexError(error) if numeric else KeyError(error)
        parent = point
    return parent

def iterify(source):
    try:
        # Dictionary.
        return source.items()
    except AttributeError:
        pass

    if isinstance(source, str):
        return None

    try:
        # List or tuple.
        return enumerate(source)
    except TypeError:
        return None

def make_point(specifier, point=None):
    """Make or create a suitable point that can hold specifier.
    If a point is specified as input, the new point is based on it.
    """
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

def default_point_maker(path, index, point=None):
    return make_point(path[index], point)

def default_logger_pass(origin__name__, *args):
    return False

def default_logger_print(origin__name__, *args):
    # Komodo Edit flags the next line as an error but it's fine.
    print(origin__name__, *args)
    return True

def insert(parent
           , path
           , value
           , point_maker=default_point_maker
           , logger=default_logger_pass
           ):

    # Concealed inner subroutine.
    def _insert(parent, path, value, point_maker, logger, enumerator):
        logger(__name__, 'insert()', parent, path, value)
        try:
            index, leg = next(enumerator)
        except StopIteration:
            if value is None:
                logger(__name__, 'insert merging None.')
                return parent
            legIterator = iterify(value)
            if legIterator is None:
                logger(__name__, 'insert replacing.')
                return value
            pathLen = len(path)
            for legKey, legValue in legIterator:
                logger(__name__, 'insert merge', str_quote(legKey), legValue)
                if legValue is None:
                    continue
                path.append(legKey)
                parent = _insert(parent, path, legValue, point_maker, logger
                                 , enumerate(pathify(legKey), pathLen))
                path.pop()
    
            return parent
    
        wasTuple = isinstance(parent, tuple)


# Could treat leg -1 as a special case here.
# If leg is -1, discard parent unless it is a list or tuple,
# and change leg to len(parent)


        point, numeric, type = descend_one(parent, leg)
        if numeric and isinstance(parent, str):
            # Sorry, hack to force descent into a string to fail if setting.
            point = None
        
        logger(__name__, "{:2d} {}\n  {}\n  {}\n  {} {}".format(
            index, str_quote(leg), parent, point, str(numeric), str(type)))
    
        if type is None or point is None:
            parent = point_maker(path, index, parent)
            logger(__name__, 'insert made point', parent)
            point, numeric, type = descend_one(parent, leg)
    
        if type is None:
            raise AssertionError("".join((
                "type was None twice at ", str(parent)
                ," path:", str(path), " index:", str(index)
                , " leg:", str_quote(leg), ".")))
    
        value = _insert(point, path, value, point_maker, logger, enumerator)
    
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

    return _insert(parent
                   , list(pathify(path))
                   , value
                   , point_maker
                   , logger
                   , enumerate(pathify(path)))

# def merge(source
#           , destination=None
#           , point_maker=default_point_maker
#           , logger=None):
#     # paths = []
#     # index = 0
# 
# 
# # If source is None, return destination.
# # If source is a simple type, return source.
# # Otherwise, go back to the vertical and insert each item in source into
# # destination.
# 
# 
# 
#     #
#     #  Assume source is a dictionary.
#     
#     for path, value in sourceIter:
#         destination = insert(destination, (path,), value, point_maker, logger)
# 
#     return destination
