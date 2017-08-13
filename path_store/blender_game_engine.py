#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for arctan.
# https://docs.python.org/3.5/library/math.html
from math import atan2, pow, sqrt
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine bge.types.KX_GameObject
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
# Can't be imported here because this module gets imported in the bpy context
# too, in which bge isn't available.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Matrix, Quaternion
#
# Local imports.
#
# RESTful interface.
# from rest import RestInterface
#
# Custom property for access to immutable properties in KX_GameObject.
from path_store.hosted import InterceptProperty

def get_game_object_subclass(bge):
    """Get a custom subclass of of KX_GameObject in which the Vector properties
    are mutable at the item level. For example:
    
        gameObject.worldScale[2] = 2.5 # Where 2.5 is the desired Y scale.
    
    Pass as a parameter a reference to the bge module.
    """
    
    KX_GameObject = bge.types.KX_GameObject
    
    class GameObject(KX_GameObject):
        @InterceptProperty()
        def worldScale(self):
            return super().worldScale
        @worldScale.intercept_getter
        def worldScale(self):
            return self._worldScale
        @worldScale.intercept_setter
        def worldScale(self, value):
            self._worldScale = value
        @worldScale.destination_setter
        def worldScale(self, value):
            # It'd be nice to do this:
            #
            #     super(self).worldScale = value
            #
            # But see this issue: http://bugs.python.org/issue14965
            # So instead, we have the following.
            KX_GameObject.worldScale.__set__(self, value)
    
        @InterceptProperty()
        def worldPosition(self):
            return super().worldPosition
        @worldPosition.intercept_getter
        def worldPosition(self):
            return self._worldPosition
        @worldPosition.intercept_setter
        def worldPosition(self, value):
            self._worldPosition = value
        @worldPosition.destination_setter
        def worldPosition(self, value):
            KX_GameObject.worldPosition.__set__(self, value)

        @property
        def rotation(self):
            return self._rotation
        @rotation.setter
        def rotation(self, rotation):
            self._rotation = Rotation(self, rotation)
        
        def __init__(self, oldOwner):
            self._rotation = Rotation(self)

    return GameObject
        
class Rotation(object):
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _set_list(self):
        """Set the list property from the rotation of the game object."""
        orientation = self._gameObject.worldOrientation
        #
        # Formula for decomposition of a 3x3 rotation matrix into x, y, and z
        # rotations comes from this page: http://nghiaho.com/?page_id=846
        self._list = [
            atan2(orientation[2][1], orientation[2][2]),
            atan2(orientation[2][0] * -1.0
                  , sqrt(pow(orientation[2][1], 2)
                         + pow(orientation[2][2], 2))),
            atan2(orientation[1][0], orientation[0][0])
        ]
        # ToDo: Cache the list probably. It seems like it might be quite an
        # expensive calculation.
    
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
        return self._list.__len__()

    def __getitem__(self, specifier):
        self._set_list()
        return self._list.__getitem__(specifier)
    
    def __setitem__(self, specifier, value):
        self._set_list()
        self._list.__setitem__(specifier, value)
        self._apply()
        
    def __repr__(self):
        return self._list.__repr__()
    
    def _apply(self):
        # Apply the rotation to the BGE object.
        #
        # Start by setting its rotation to none, i.e. identity matrix.
        self._gameObject.worldOrientation.identity()
        #
        # Apply the rotation in each dimension, in order.
        for dimension, value in enumerate(self._list):
            if value is None:
                continue
            self._gameObject.worldOrientation.rotate(
                Matrix.Rotation(value, 4, self.axes[dimension]))
    
    def __init__(self, gameObject, initialiser=None):
        self._gameObject = gameObject
        if initialiser is None:
            self._set_list()
        else:
            self[:] = list(initialiser)
            self._apply()

# -   BGE interface will be like: create a KXGameObject, create a wrapper around
#     it, set the wrapper as principal.
# 
# 
# class RestBGEObject(RestInterface):
#     
#     def rest_POST(self, parameters):
#         # Add an object to the scene.
#         # Make the object instance be self.restPrincipal
#         # call super().restPOST(parameters) which will set each thing in the
#         # parameters dictionary.
#         pass
# -   How to do applyImpulse? Maybe by POST to an "impulse" property, that gets
#     pushed down to a setter, that executes the applyImpulse and discards its
#     own value.
