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
from mathutils import Matrix, Quaternion
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
    

    # Copy the orientation in _set_list...
    # Only append Quaternion rotations to the in-progress list.
    
    class _RotationPiece:
        pass
    
    
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _base_orientation(self):
        """Set the list property from the rotation of the game object."""
        self._baseOrientation = self._get_orientation().copy()

        self._pieces = []
        # for dimension, amount in enumerate(
        #     self._decompose(self._baseOrientation)
        # ):
        #     if isclose(amount, 0.0):
        #         continue
        #     piece = self._RotationPiece()
        #     piece.dimension = dimension
        #     piece.readOnly = True
        #     piece.radians = amount
        #     self._pieces.append(piece)
        self._baseDecomposed = _decompose(self._baseOrientation)
        print('rotation._base_orientation() {} {}'.format(
            self._baseOrientation, self._baseDecomposed))
        
        # Always three but formally, the number of dimensions.
        return len(self._baseDecomposed)
        
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
        if not self._usingList:
            self._base_orientation()
        
        effective = _decompose(self._effective_orientation())
        
        
        if isinstance(specifier, slice):
            return_ = []
            for dimension in range(*specifier.indices(self._listLength)):
                return_.append(effective[dimension])
            return return_
        else:
            return effective[specifier]

        
        # if self._usingList:
        #     return self._list.__getitem__(specifier)
        # else:
        #     self._set_list_game_object()
        #     return self._listGameObject.__getitem__(specifier)
    
    # def _get_dimension(self, dimension):
    #     amount = 0.0
    #     lastPiece = None
    #     for piece in self._pieces:
    #         if piece.dimension == dimension:
    #             lastPiece = piece
    #             amount += piece.radians
    #     return amount, lastPiece
    
    def __setitem__(self, specifier, value):
        print('rotation.__setitem__(,{},{})'.format(specifier, value))
        if not self._usingList:
            self._base_orientation()
            # self._list[:] = self._listGameObject[:]
            self._usingList = True

        effective = _decompose(self._effective_orientation())

        if isinstance(specifier, slice):
            for index, dimension in enumerate(range(*specifier.indices(self._listLength))):
                self._increment(
                    dimension, value[index] - effective[dimension])
        else:
            self._increment(specifier, value - effective[specifier])
            # self._set_dimension(specifier, value)
        # self._list.__setitem__(specifier, value)

        self._apply()

    def _increment(self, dimension, value):
        for piece in self._pieces:
            if piece.dimension == dimension:
                piece.radians += value
                return

        # current, piece = self._get_dimension(dimension)
        # if piece is None or piece.readOnly:
        piece = self._RotationPiece()
        piece.dimension = dimension
        # piece.readOnly = False
        piece.radians = value
        self._pieces.append(piece)
    
    def __delitem__(self, specifier):
        print('rotation.__delitem({}) {}'.format(specifier, self))
        if self._usingList:
            # self._list.__delitem__(specifier)
            self._usingList = False
        
    def __repr__(self):
        if not self._usingList:
            self._base_orientation()
        
        def _all():
            yield self._baseOrientation.__repr__()
            for piece in self._pieces:
                yield piece.__dict__.__repr__()

        # [self._get_dimension(dimension)[0]
        #  for dimension in range(self._listLength)]
        return tuple(_all()).__repr__()
    
    def _apply(self):
        # Apply the rotation to the BGE object.
        #
        # Start with an identity matrix of the same size as the world
        # orientation.
        # orientation = self._get_orientation().copy()
        # orientation.identity()
        #
        # Apply the rotation in each dimension, in order.
        any = True #False
        # for dimension, value in enumerate(self._list):
        #     if value is not None:
        #         worldOrientation.rotate(Quaternion(self.axes[dimension], value))
        #         any = True

        # if any:
        #     self._set_orientation(orientation)
        effective = self._effective_orientation()
        decomposed = _decompose(effective)
        self._set_orientation(effective)
        print('rotation._apply() {} {} {}'.format(self, effective, decomposed))
    
    def _effective_orientation(self):
        orientation = self._baseOrientation.copy()
        
        for piece in self._pieces:
            orientation.rotate(Quaternion(
                self.axes[piece.dimension], piece.radians))
        return orientation
        
    
    def __init__(self, get_orientation, set_orientation):
        self._get_orientation = get_orientation
        self._set_orientation = set_orientation
        self._orientationCache = None
        
        self._listLength = self._base_orientation()
        #len(self._listGameObject)
        # self._list = []
        self._usingList = False

