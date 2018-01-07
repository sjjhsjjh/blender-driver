#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""\
Path Store base module.

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
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log

def str_quote(str_, quote='"'):
    """Utility to add quotes to strings, but just stringify non-strings."""
    if isinstance(str_, str):
        return str_.join((quote, quote))
    else:
        return str(str_)

class PointType(Enum):
    LIST = 1
    DICTIONARY = 2
    ATTR = 3

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

def iterify(source):
    """\
    Either source.items(), for a dictionary, or enumerate(source), for a list or
    tuple.
    """
    try:
        # Dictionary.
        return PointType.DICTIONARY, source.items()
    except AttributeError:
        pass

    if isinstance(source, str):
        raise TypeError()

    # Assume source is a list or a tuple. If it isn't, the next line raises
    # TypeError, which is what we want.
    return PointType.LIST, enumerate(source)

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
    pointType = None
    if numeric:
        pointType = PointType.LIST
        try:
            point = parent[specifier]
        except IndexError:
            point = None
        except TypeError:
            pointType = None
            point = None
        except KeyError:
            pointType = None
            point = None
    else:
        pointType = PointType.DICTIONARY
        try:
            in_ = specifier in parent
        except TypeError:
            pointType = None
            in_ = False
        if in_:
            point = parent[specifier]
        elif hasattr(parent, specifier):
            point = getattr(parent, specifier)
            pointType = PointType.ATTR
        else:
            point = None
            
    return point, numeric, pointType

def get(parent, path=None):
    """Descend from the parent along the path. Returns the point descended to,
    or raises:
    
    -   IndexError if there was a missing point in a list or tuple.
    -   KeyError if there was a missing point in a dictionary.
    -   TypeError if descent was impossible for any other reason.
    
    If path is None or empty, returns the parent.
    """
    for leg in pathify(path):
        point, numeric, pointType = descend(parent, leg)
        if pointType is None:
            raise TypeError(" ".join((
                "Couldn't get point for", str_quote(leg), "in", str(parent))))
        if point is None:
            error = " ".join((
                "No point for", str_quote(leg), "in", str(parent)))
            raise IndexError(error) if numeric else KeyError(error)
        parent = point
    return parent

def walk(parent, editor, path=None, results=None, second=None
         , editIterable=False
         ):
    """\
    Descend from the parent along the path by calling get(), then walk the
    structure there and execute editor on the items there and below.
    
    -   If `editIterable` is false, the default, then the editor isn't called on
        lists, tuples, dictionaries, and other items that can be iterated.
    -   If `editIterable` is true, then the editor is called on every item. An
        iterable item will be passed to the editor before its child items. If
        the editor replaces the iterable, see below, then the replaced iterable
        is iterated.
    
    If `second` is None, the editor callable is invoked as follows.

        editor(point, path, results)

    Where:
    
    -   `point` is the item on the walk.
    -   `path` is the navigation path to reach it from the parent. The list gets
        modified during execution, so copy it if needed.
    -   `results` is the object passed to the walk function, which can be used
        to store and accumulate results.
    
    If `second` isn't None, then its structure is walked in parallel to the
    parent. The current point in the second structure is also passed to the
    editor callable, as a fourth parameter.
    
    The editor can return one of the following.
    
    -   (True, `value`) to replace the point object with `value`.
    -   (False, any) or just None or just False not to replace the point. The
        editor could have called a method on the point object that modified it
        in place but the object itself isn't replaced.
    
    Returns parent, which could be different to the input parameter, if the
    editor replaced the top level object.

    If editor raises StopIteration, then the walk ends.
    """
    log(DEBUG, "{} {} {}.", parent, editor, path)

    # Inner function for recursive descent. Returns a tuple:
    #
    # -   Flag for whether to stop now.
    # -   Sub-total.
    #
    def inner_walk(point, walkPath, secondPoint):
        
        result = [False, False, point]
        wasTuple = isinstance(point, tuple)

        def edit_one():
            try:
                editorResult = None
                if second is None:
                    editorResult = editor(point, walkPath, results)
                else:
                    editorResult = editor(point, walkPath, results, secondPoint)
                
                if not(editorResult is None or editorResult is False):
                    result[1:] = editorResult

            except StopIteration:
                result[0] = True

        if editIterable:
            edit_one()
            if result[1]:
                point = result[2]
            if result[0]:
                return result
        
        try:
            pointType, iterator = iterify(point)
            log(DEBUG, "iterator {} {}.", point, walkPath, results)
        except TypeError:
            iterator = None

        if iterator is None and not editIterable:
            edit_one()

        if iterator is None:
            return result

        for key, value in iterator:
            walkPath.append(key)
            secondValue = None
            if second is not None:
                secondValue = descend(secondPoint, key)[0]
            innerResult = inner_walk(value, walkPath, secondValue)
            del walkPath[-1]
            if innerResult[0]:
                result[0] = True
                break
            if innerResult[1]:
                assigned, point = _set(point, key, innerResult[2], pointType)
                if assigned:
                    result[1] = True
                    result[2] = point

        if result[1] and wasTuple and isinstance(point, list):
            result[2] = tuple(point)

        return result
    
    innerResult = inner_walk(get(parent, path)
                             , list(pathify(path))
                             , None if second is None else get(second, path))
    if innerResult[1]:
        parent = replace(parent, innerResult[2], path)
    
    return parent

def make_point(specifier, point=None):
    """\
    Make or create a suitable point that can hold specifier. If a point is
    specified as input, the new point is based on it.
    """
    log(DEBUG, "{} {}.", specifier, point)
    if specifier is None:
        return point
    elif isinstance(specifier, str):
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
    log(DEBUG, "{} {} {}.", path, index, point)
    return make_point(path[index], point)

def replace(parent, value, path=None, point_maker=default_point_maker):
    """\
    Descend from the parent along the path and replace whatever is there with a
    new value. Returns parent as modified.
    
    Elements on the path that don't exist will be created by invoking the
    point_maker.
    """
    log(DEBUG, "{} {} {}.", parent, path, value)
    return _insert(parent
                   , tuple(pathify(path))
                   , True
                   , value
                   , point_maker
                   , enumerate(pathify(path)))
    # There is a possible problem with the lambda in the above. Because it
    # returns None for the parent, it might discard whatever had been put in by
    # a custom point maker.

def merge(parent, value, path=None, point_maker=default_point_maker):
    """\
    Descend from the parent along the path and merge a specified value into
    whatever is there. Returns parent as modified.
    
    Elements on the path that don't exist will be created by invoking the
    point_maker.
    """
    log(DEBUG, "{} {} {}.", parent, path, value)
    
    return _insert(parent
                   , tuple(pathify(path))
                   , False
                   , value
                   , point_maker
                   , enumerate(pathify(path)))

def _insert(parent, path, replacing, value, point_maker, enumerator):
    try:
        index, leg = next(enumerator)
        stopping = False
    except StopIteration:
        stopping = True
    
    if stopping:
        if replacing:
            pathLen = len(path)
            #
            # If a made point would have the same type as value, discard it and
            # use value. Otherwise, _merge value into the point. If the value
            # isn't iterable, _merge will discard the parent anyway.
            if pathLen <= 0:
                parent = point_maker((None,), 0, None)
            else:
                parent = point_maker(path, pathLen - 1, None)
            if parent is None or type(parent) is type(value):
                return value
            else:
                parent = None
        return _merge(parent, value, point_maker, path)

    wasTuple = isinstance(parent, tuple)

# Could treat leg -1 as a special case here.
# If leg is -1, discard parent unless it is a list or tuple,
# and change leg to len(parent)

    point, numeric, pointType = descend(parent, leg)
    if numeric and isinstance(parent, str):
        # Sorry, hack to force descent into a string to fail if setting.
        point = None
    
    log(DEBUG, "{:d} {}\n  {}\n  {}\n  {} {}", index, str_quote(leg), parent
        , str_quote(point), str(numeric), str(pointType))

    if pointType is None or point is None:
        log(DEBUG, "about to point_maker({}, {}, {}).", path, index, parent)
        parent = point_maker(path, index, parent)
        log(DEBUG, "made point {} {}.", parent, parent.__class__)
        point, numeric, pointType = descend(parent, leg)

    if pointType is None:
        raise AssertionError("".join((
            "pointType was None twice at ", str(parent)
            ," path:", str(path), " index:", str(index)
            , " leg:", str_quote(leg), ".")))

    value = _insert(point, path, replacing, value, point_maker, enumerator)
    
    didSet, parent = _set(parent, leg, value, pointType)

    if not didSet:
        log(DEBUG, "setter optimised: {}.", pointType)

    if wasTuple and isinstance(parent, list):
        parent = tuple(parent)
    
    return parent

def _merge(parent, value, point_maker, pointMakerPath):
    log(DEBUG, "{} {} {}.", parent, value, pointMakerPath)
    if value is None:
        return parent
    try:
        legIterator = iterify(value)[1]
    except TypeError:
        legIterator = None

    if legIterator is None:
        return value
    #
    # The code reaches this point only if the value is iterable.
    #
    # Create a path that is definitely a list, and therefore mutable.
    path = list(pathify(pointMakerPath))
    #
    # Set the length into a variable to avoid recalculation later.
    pathLen = len(path)

    def enumerate_one(index, item):
        yield index, item
    
    for legKey, legValue in legIterator:
        log(DEBUG, "iteration {} {}", str_quote(legKey), legValue)
        # Not sure about this so it's commented out. It seems that it could skip
        # the point maker if a value happens to be None.
        # if legValue is None:
        #     continue
        path.append(legKey)
        parent = _insert(parent, path, False, legValue, point_maker
                         , enumerate_one(pathLen, legKey))
        path.pop()

    log(DEBUG, "return {}.", parent)
    return parent

def _set(parent, key, value, pointType):
    '''\
    Assign a value to a point within a parent, using a specified type of
    assignment.
    
    If the point is already the value, the assignment isn't made.
    
    If the parent is a tuple, and the point isn't already the value, the
    assignment is made into a list copy of the parent.
    
    Returns a tuple of:
    
    -   True in the first element, if the assignment was made, or False
        otherwise.
    -   The parent in the second element, which could be different, if a list
        copy had to be created.
    '''
    if pointType is PointType.ATTR:
        if getattr(parent, key) is value:
            return False, parent
        else:
            setattr(parent, key, value)
    elif pointType is PointType.DICTIONARY:
        if (key in parent) and (parent[key] is value):
            return False, parent
        else:
            parent[key] = value
    elif pointType is PointType.LIST:
        if parent[key] is value:
            return False, parent
        else:
            # If it's a tuple then make it into a list, and therefore mutable,
            # first.
            if isinstance(parent, tuple):
                parent = list(parent)
            parent[key] = value
    else:
        raise AssertionError(" ".join(("Unknown PointType:", str(pointType))))
    return True, parent
