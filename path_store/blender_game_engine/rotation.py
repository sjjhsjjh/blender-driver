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
    return [
        atan2(matrix[2][1], matrix[2][2]),
        atan2(matrix[2][0] * -1.0
              , sqrt(pow(matrix[2][1], 2) + pow(matrix[2][2], 2))),
        atan2(matrix[1][0], matrix[0][0])
    ]

class Rotation(object):
    """Class to represent the x,y,z rotation of a Blender game object."""

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
    
    def _set_base(self):
        """Set the list property from the rotation of the host."""
        self._base = self._get_orientation().copy()
        self._pieces = []
        
        if self._base == self._baseCache:
            self._decomposed = self._decomposedCache[:]
            # print('rotation._set_base() Cached {} {}'.format(
            #     self._base, self._decomposed))
        else:
            self._decomposed = _decompose(self._base)
            # print('rotation._set_base() not cached {} {}'.format(
            #     self._base, self._baseCache))
            self._baseCache = self._base.copy()
            self._decomposedCache = self._decomposed[:]
        
        # Always three but formally, the number of dimensions.
        return len(self._decomposed)
        
        # if self._orientationCache == orientation:
        #     return
        # #
        # # Cache the orientation because the list setting looks like quite an
        # # expensive calculation.
        # self._orientationCache = orientation.copy()
        # #
        # # Formula for decomposition of a 3x3 rotation matrix into x, y, and z
        # # rotations comes from this page: http://nghiaho.com/?page_id=846
        # self._listGameObject = (
        #     atan2(orientation[2][1], orientation[2][2]),
        #     atan2(orientation[2][0] * -1.0
        #           , sqrt(pow(orientation[2][1], 2)
        #                  + pow(orientation[2][2], 2))),
        #     atan2(orientation[1][0], orientation[0][0]))
    
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

    def __getitem__(self, specifier):
        if not self._setting:
            self._set_base()
        
        if isinstance(specifier, slice):
            return_ = []
            for dimension in range(*specifier.indices(self._listLength)):
                return_.append(self._decomposed[dimension])
            return return_
        else:
            return self._decomposed[specifier]

    def __setitem__(self, specifier, value):
        # print('rotation.__setitem__(,{},{})'.format(specifier, value))
        if not self._setting:
            self._set_base()
            self._setting = True

        if isinstance(specifier, slice):
            for index, dimension in enumerate(
                range(*specifier.indices(self._listLength))
            ):
                self._set1(dimension, value[index])
        else:
            self._set1(specifier, value)

        orientation = self._base.copy()
        for piece in self._pieces:
            orientation.rotate(Quaternion(
                self.axes[piece.dimension], piece.radians))

        self._decomposed = _decompose(orientation)
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

        # self._decomposed[dimension] = value
    
    def __delitem__(self, specifier):
        # print('rotation.__delitem({}) {}'.format(specifier, self))
        self._setting = False
        self._pieces = []
        
    def __repr__(self):
        if not self._setting:
            self._set_base()
        
        def _all():
            yield self._base.__repr__()
            for piece in self._pieces:
                yield piece.__dict__.__repr__()

        return tuple(_all()).__repr__()
    
    def __init__(self, get_orientation, set_orientation):
        self._get_orientation = get_orientation
        self._set_orientation = set_orientation

        self._baseCache = None
        self._decomposedCache = None
        
        self._listLength = self._set_base()
        self._setting = False

