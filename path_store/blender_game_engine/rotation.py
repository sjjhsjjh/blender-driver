#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for mathematical operations needed to decompose a rotation matrix.
# https://docs.python.org/3/library/math.html
from math import atan2, pow, sqrt, isclose
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Quaternion
#
# Local imports, would go here.
#

def _decompose(matrix):
    #
    # Formula for decomposition of a 3x3 rotation matrix into x, y, and z
    # rotations comes from this page: http://nghiaho.com/?page_id=846
    return (
        atan2(matrix[2][1], matrix[2][2]),
        atan2(matrix[2][0] * -1.0
              , sqrt(pow(matrix[2][1], 2) + pow(matrix[2][2], 2))),
        atan2(matrix[1][0], matrix[0][0])
    )

class RotationXYZ(object):
    """Class to represent the x,y,z rotation of a Blender game object."""

    @property
    def x(self):
        return self[0]
    @x.setter
    def x(self, x):
        self[0] = x
    
    @property
    def y(self):
        return self[1]
    @y.setter
    def y(self, y):
        self[1] = y
    
    @property
    def z(self):
        return self[2]
    @z.setter
    def z(self, z):
        self[2] = z
    
    def __len__(self):
        return self._listLength

    # Each instance of this class has two lists:
    #
    # -   _listGameObject, which is created with maths from the rotation matrix
    #     of the game object.
    # -   _list, the elements of which are either copied from the game object
    #     list or set externally. This list can also be empty.
    #
    # The lists are maintained by the getters and setters of the class.
    #
    # The set list is needed to support users that control some axes of
    # rotation, and require consistent results, such as returning a value just
    # set.
    #
    # For example, suppose a user makes repeated increments to the X rotation.
    # The game object list will echo the increments to a point, but could switch
    # direction, of the X rotation, at the point that it passes 90 degrees. At
    # the switch, the Y and Z rotations will change, even if they haven't been
    # set.
    #
    # Usage:
    #
    # -   When an instance of this class is constructed, the set list will be
    #     empty. Instances are generally constructed by constructing a
    #     GameObject, see above. Every instance is linked to one game object.



    # -   Setting any item when the list is empty first causes the game object
    #     list elements to be copied to the set list. After that, the item is
    #     set in the set list, and the rotation represented by the set list is
    #     applied to the linked game object.
    # -   Getting an item gets it from the set list, unless the set list is
    #     empty, in which case it gets it from the game object list.
    # -   Deleting any item effectively empties the set list.
    #
    # To rotate an object repeatedly, make repeated settings of an item in its
    # rotation property, then delete the set list in the rotation property, as
    # in:
    #
    #     del gameObject.rotation[:]
    #
    
    # Cache and update the last decomposed values when set_item.
    
    class _RotationPiece:
        pass
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _get_base(self):
        """Set the list property from the rotation of the host."""
        self._base = self._get_orientation().copy()
        del self._pieces[:]
        
        if self._base != self._baseCache:
            self._baseCache = self._base.copy()
            self._decomposed = _decompose(self._base)
            self._setCache = list(self._decomposed)
        
    def __getitem__(self, specifier):
        if not self._setting:
            self._get_base()

        # ? Change to self._setCache.__getitem__(specifier)            
        if isinstance(specifier, slice):
            return [self._setCache[dimension] for
                    dimension in range(*specifier.indices(self._listLength))]
        else:
            return self._setCache[specifier]
    
    @property
    def fromIdentity(self):
        return self._fromIdentity
    @fromIdentity.setter
    def fromIdentity(self, fromIdentity):
        self._fromIdentity = fromIdentity

    def __setitem__(self, specifier, value):
        if not self._setting:
            self._get_base()
            self._setting = True

        if isinstance(specifier, slice):
            for index, dimension in enumerate(
                range(*specifier.indices(self._listLength))
            ):
                self._set1(dimension, value[index])
        else:
            self._set1(specifier, value)
        
        orientation = (self._orientationIdentity.copy() if self.fromIdentity
                       else self._base.copy())
        if self.fromIdentity:
            for dimension, rotation in enumerate(self._setCache):
                orientation.rotate(Quaternion(self.axes[dimension], rotation))
        else:
            for piece in self._pieces:
                orientation.rotate(Quaternion(
                    self.axes[piece.dimension], piece.radians))

        self._decomposed = _decompose(orientation)
        # Next line is a super fudge to replace the setCache every tick.
        # self._setCache = list(self._decomposed)
        self._set_orientation(orientation)

    def _set1(self, dimension, value):
        needPiece = True
        increment = value - self._decomposed[dimension]
        for piece in self._pieces:
            if piece.dimension == dimension:
                piece.radians += increment
                needPiece = False
                break
        
        if needPiece:
            piece = self._RotationPiece()
            piece.dimension = dimension
            piece.radians = increment
            self._pieces.append(piece)

        self._setCache[dimension] = value
    
    def __delitem__(self, specifier):
        # print('rotation.__delitem__({}) {}'.format(specifier, self))
        
        # Following line means that the next getitem or setitem will _get_base
        self._setting = False
        del self._pieces[:]
        
    def __repr__(self):
        if not self._setting:
            self._get_base()
        
        return {
            '_setCache': self._setCache,
            '_base': self._base,
            '_decomposed': self._decomposed,
            '_pieces': tuple(piece.__dict__ for piece in self._pieces)
        }.__repr__()
        
    def __init__(self, get_orientation, set_orientation):
        self._get_orientation = get_orientation
        self._set_orientation = set_orientation
        
        self._fromIdentity = False

        self._baseCache = None
        self._setCache = None
        self._decomposed = None
        self._pieces = []

        self._setting = False
        self._get_base()
        
        self._orientationIdentity = self._base.copy()
        self._orientationIdentity.identity()

        # Always three but formally, the number of dimensions.
        self._listLength = len(self._decomposed)

class Rotation(object):
    """Class to represent the x,y,z rotation of a Blender game object."""
    
    # Constants
    _orders = ('YZX', 'ZXY', 'XYZ')

    @property
    def x(self):
        return self[0]
    @x.setter
    def x(self, x):
        self[0] = x
    
    @property
    def y(self):
        return self[1]
    @y.setter
    def y(self, y):
        self[1] = y
    
    @property
    def z(self):
        return self[2]
    @z.setter
    def z(self, z):
        self[2] = z
    
    def __len__(self):
        return self._listLength
    
    @property
    def euler(self):
        return self._get_euler()
    
    @property
    def order(self):
        return self._get_euler().order
    @order.setter
    def order(self, order):
        euler = self._get_euler()
        if euler.order == order:
            return
        matrix = euler.to_matrix()
        self._euler = matrix.to_euler(order)
    
    def _get_euler(self, dimension=None):
        if self._euler is None:
            if dimension is None:
                dimension = 2 if self._savedOrder is None else self._savedOrder
            self._euler = (
                self._get_orientation().to_euler(self._orders[dimension]))
        else:
            if (dimension is not None
                and not self._euler.order.endswith(
                    self._orders[dimension][-1])
            ):
                matrix = self._euler.to_matrix()
                self._euler = matrix.to_euler(self._orders[dimension])
                # print('_get_euler change for', dimension
                #       , self._orders[dimension], matrix, self._euler)
        return self._euler

    def __getitem__(self, specifier):
        return self._get_euler().__getitem__(specifier)

    def __setitem__(self, specifier, value):
        if isinstance(specifier, slice):
            for index, dimension in enumerate(
                range(*specifier.indices(3))
            ):
                self._set1(dimension, value[index])
        else:
            self._set1(specifier, value)
        
        # print('__setitem__', self._euler)
        self._set_orientation(self._euler.to_matrix())
    
    def __delitem__(self, specifier):
        # Discard the Euler when anything is deleted. This will force getting a
        # new Euler on the next access.
        self._savedOrder = self._get_euler().order[:]
        self._euler = None
        
    def _set1(self, dimension, value):
        # The increment code works if the value was set like this:
        #
        #     rot.x += radians(45
        #
        # However, it doesn't work for plain setting, so it's commented out. The
        # order property must be used instead.
        # increment = value - self._get_euler(None)[dimension]
        # euler = self._get_euler(dimension)
        # self._euler[dimension] += increment
        self._get_euler()[dimension] = value

    def __init__(self, get_orientation, set_orientation):
        self._get_orientation = get_orientation
        self._set_orientation = set_orientation
        
        self._euler = None
        self._savedOrder = None
