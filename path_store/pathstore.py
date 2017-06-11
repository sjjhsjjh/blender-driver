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

def descend(parent, specifier):
    """Descend one level, either by array index, dictionary key, or object
    attribute. Returns a tuple of:
    
    0.  The point descended to, or None.
    1.  True if the specifier is numeric, or False otherwise.
    2.  pathstore.PointType value for the type of descent used, or None if
        descent wasn't possible.
    """
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

def get(parent, path=None):
    """Descend from the parent along the path. Returns the point descended to,
    or raises:
    
    -   IndexError if there was a missing point in a list or tuple.
    -   KeyError if there was a missing point in a dictionary.
    -   TypeError if descent was impossible for any other reason.
    
    If path is None or empty, returns the parent.
    """
    for leg in pathify(path):
        point, numeric, type = descend(parent, leg)
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
    """Generator function that returns either source.items(), for a dictionary,
    or enumerate(source), for a list or tuple.
    """
    try:
        # Dictionary.
        return source.items()
    except AttributeError:
        pass

    if isinstance(source, str):
        raise TypeError()

    # Assume list or tuple. The next line raises TypeError if source isn't a
    # list or tuple, which is what we want.
    return enumerate(source)

def make_point(specifier, point=None):
    """Make or create a suitable point that can hold specifier.
    If a point is specified as input, the new point is based on it.
    """
    if isinstance(specifier, str):
        # The if on the next line might be unnecessary. It might be the case
        # that hasattr(None, specifier) is False for all specifier. For safety
        # and perhaps readability, however, it seems better to make a special
        # check for None.
        if point is None:
            return {}
        if isinstance(point, dict) or hasattr(point, specifier):
            return point
        return {}
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

def replace(parent
            , value
            , path=None
            , point_maker=default_point_maker
            , logger=default_logger_pass
            ):
    """Descend from the parent along the path and replace whatever is there with
    a new value.
    """
    logger(__name__, 'replace()', parent, path, value)
    return _insert(parent
                   , tuple(pathify(path))
                   , value
                   , point_maker
                   , logger
                   , enumerate(pathify(path))
                   , True)

def merge(parent
          , value
          , path=None
          , point_maker=default_point_maker
          , logger=default_logger_pass
          ):
    """Descend from the parent along the path and merge a specified value into
    whatever is there.
    """
    logger(__name__, 'merge()', parent, path, value)
    return _insert(parent
                   , tuple(pathify(path))
                   , value
                   , point_maker
                   , logger
                   , enumerate(pathify(path))
                   , False)

def _insert(parent, path, value, point_maker, logger, enumerator, setReplace):
    try:
        index, leg = next(enumerator)
    except StopIteration:
        if setReplace:
            parent = None
        return _merge(parent, value, point_maker, path, logger)

    wasTuple = isinstance(parent, tuple)

# Could treat leg -1 as a special case here.
# If leg is -1, discard parent unless it is a list or tuple,
# and change leg to len(parent)

    point, numeric, type = descend(parent, leg)
    if numeric and isinstance(parent, str):
        # Sorry, hack to force descent into a string to fail if setting.
        point = None
    
    logger(__name__, "{:2d} {}\n  {}\n  {}\n  {} {}".format(
        index, str_quote(leg)
        , parent, str_quote(point), str(numeric), str(type)))

    if type is None or point is None:
        parent = point_maker(path, index, parent)
        logger(__name__, 'made point', parent)
        point, numeric, type = descend(parent, leg)

    if type is None:
        raise AssertionError("".join((
            "type was None twice at ", str(parent)
            ," path:", str(path), " index:", str(index)
            , " leg:", str_quote(leg), ".")))

    value = _insert(
        point, path, value, point_maker, logger, enumerator, setReplace)
    
    didSet, parent = _set(parent, leg, value, type)

    if not didSet:
        logger(__name__, "setter optimised:", type)

    if wasTuple and isinstance(parent, list):
        parent = tuple(parent)
    
    return parent

def _merge(parent, value, point_maker, pointMakerPath, logger):
    logger(__name__, '_merge()', parent, value, pointMakerPath)
    if value is None:
        logger(__name__, '_merge None.')
        return parent
    try:
        legIterator = iterify(value)
    except TypeError:
        logger(__name__, '_merge replacing.')
        return value

    path = list(pathify(pointMakerPath))
    pathLen = len(path)
    
    def enumerate_one(index, item):
        yield index, item
    
    for legKey, legValue in legIterator:
        logger(__name__, '_merge iteration', str_quote(legKey), legValue)
        if legValue is None:
            continue
        path.append(legKey)
        parent = _insert(parent, path, legValue, point_maker, logger
                         , enumerate_one(pathLen, legKey), False)
        path.pop()

    logger(__name__, '_merge return', parent)
    return parent

def _set(parent, key, value, type):
    if type is PointType.ATTR:
        if getattr(parent, key) is value:
            return False, parent
        else:
            setattr(parent, key, value)
    elif type is PointType.DICTIONARY:
        if (key in parent) and (parent[key] is value):
            return False, parent
        else:
            parent[key] = value
    elif type is PointType.LIST:
        if parent[key] is value:
            return False, parent
        else:
            # If it's a tuple then make it into a list, and therefore mutable,
            # first.
            if isinstance(parent, tuple):
                parent = list(parent)
            parent[key] = value
    else:
        raise AssertionError(" ".join(("Unknown PointType:", str(type))))
    return True, parent
