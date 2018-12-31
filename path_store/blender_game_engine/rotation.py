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
# https://docs.python.org/3.5/library/math.html
from math import atan2, pow, sqrt
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
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _set_list_game_object(self):
        """Set the list property from the rotation of the game object."""
        orientation = self._get_orientation()
        if self._orientationCache == orientation:
            return
        #
        # Cache the orientation because the list setting looks like quite an
        # expensive calculation.
        self._orientationCache = orientation.copy()
        #
        # Formula for decomposition of a 3x3 rotation matrix into x, y, and z
        # rotations comes from this page: http://nghiaho.com/?page_id=846
        self._listGameObject = (
            atan2(orientation[2][1], orientation[2][2]),
            atan2(orientation[2][0] * -1.0
                  , sqrt(pow(orientation[2][1], 2)
                         + pow(orientation[2][2], 2))),
            atan2(orientation[1][0], orientation[0][0]))
    
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
        if self._usingList:
            return self._list.__getitem__(specifier)
        else:
            self._set_list_game_object()
            return self._listGameObject.__getitem__(specifier)
    
    def __setitem__(self, specifier, value):
        if not self._usingList:
            self._set_list_game_object()
            self._list[:] = self._listGameObject[:]
            self._usingList = True

        self._list.__setitem__(specifier, value)
        self._apply()
    
    def __delitem__(self, specifier):
        if self._usingList:
            self._list.__delitem__(specifier)
            self._usingList = False
        
    def __repr__(self):
        if self._usingList:
            return self._list.__repr__()
        else:
            self._set_list_game_object()
            return self._listGameObject.__repr__()
    
    def _apply(self):
        # Apply the rotation to the BGE object.
        #
        # Start with an identity matrix of the same size as the world
        # orientation.
        worldOrientation = self._get_orientation().copy()
        worldOrientation.identity()
        #
        # Apply the rotation in each dimension, in order.
        any = False
        for dimension, value in enumerate(self._list):
            if value is not None:
                worldOrientation.rotate(Quaternion(self.axes[dimension], value))
                any = True

        if any:
            self._set_orientation(worldOrientation)
    
    def __init__(self, get_orientation, set_orientation):
        self._get_orientation = get_orientation
        self._set_orientation = set_orientation
        self._orientationCache = None
                
        self._set_list_game_object()
        self._listLength = len(self._listGameObject)
        self._list = []
        self._usingList = False

