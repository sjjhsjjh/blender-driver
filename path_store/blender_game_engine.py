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
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Module for mathematical operations needed to decompose a rotation matrix.
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
        """\
        Subclass with intercept properties for worldScale, worldPosition, and in
        future other array properties whose elements are immutable in the base
        class.
        """
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
        
        def make_vector(self, startVector, endVector, calibre=0.1):
            vector = endVector - startVector
            if vector.magnitude == 0.0:
                self.worldScale = (calibre, calibre, calibre)
            else:
                self.worldScale = (calibre, calibre, vector.magnitude/2.0)
            self.worldPosition = startVector + vector/2.0
            if vector.magnitude != 0.0:
                self.alignAxisToVect(vector)

        def __init__(self, oldOwner):
            self._rotation = Rotation(self)



    return GameObject
        
class Rotation(object):
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _set_list(self):
        """Set the list property from the rotation of the game object."""
        orientation = self._gameObject.worldOrientation
        if self._orientationCache == orientation:
            log(DEBUG, 'Used orientationCache')
            return
        #
        # Cache the orientation because the self._list setting looks like quite
        # an expensive calculation.
        self._orientationCache = orientation.copy()
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
        # Start with an identity matrix of the same size as the world
        # orientation.
        worldOrientation = self._gameObject.worldOrientation.copy()
        worldOrientation.identity()
        #
        # Apply the rotation in each dimension, in order.
        for dimension, value in enumerate(self._list):
            worldOrientation.rotate(Quaternion(self.axes[dimension], value,))
        self._gameObject.worldOrientation = worldOrientation
    
    def __init__(self, gameObject, initialiser=None):
        self._gameObject = gameObject
        self._orientationCache = None
        if initialiser is None:
            self._set_list()
        else:
            # Next statement invokes __setitem__ which will invoke _set_list
            # anyway.
            self[:] = list(initialiser)
            self._apply()

class Cursor(object):
    @property
    def subjectPath(self):
        return self._subjectPath
    @subjectPath.setter
    def subjectPath(self, subjectPath):
        self._subjectPath = subjectPath
        self._update()
    
    @property
    def restInterface(self):
        return self._restInterface
    @restInterface.setter
    def restInterface(self, restInterface):
        self._restInterface = restInterface
        self._update()
        
    @property
    def add_visualiser(self):
        return self._add_visualiser
    @add_visualiser.setter
    def add_visualiser(self, add_visualiser):
        self._add_visualiser = add_visualiser
        self._update()
    
    @property
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, visible):
        self._visible = visible
        self._update()

    #
    # Properties that define the cursor.
    #
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset):
        self._offset = offset
        self._update()
    #
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, length):
        self._length = length
        self._update()
    #
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, radius):
        self._radius = radius
        self._update()
    #
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update()

    #
    # Helper properties, read-only but updated by setting other properties.
    #
    @property
    def origin(self):
        return self._origin
    @property
    def end(self):
        return self._end
    @property
    def point(self):
        return self._point
    

    def _update(self):
        if self._subjectPath is not None and self._restInterface is not None:
            self._subject = self.restInterface.rest_get(self.subjectPath)
        subject = self._subject

        if subject is not None:
            zAxis = Vector((0,0,1))
            axisVector = subject.getAxisVect(zAxis)
            
            self._origin = subject.worldPosition.copy()
            if self._offset is not None:
                self._origin += self._offset * axisVector
            self._end = self._origin.copy()
            if self._length is not None:
                self._end += self._length * axisVector
            self._point = self._end.copy()
            if self._radius is not None:
                rotationVector = Vector((self._radius, 0, 0))
                if self._rotation is not None:
                    quaternion = Quaternion(zAxis, self._rotation)
                    rotationVector.rotate(quaternion)
                radiusVector = subject.getAxisVect(rotationVector)
            
                self._point += radiusVector

        if self._visible and subject is not None:
            if self._visualisers is None and self._add_visualiser is not None:
                visualOrigin = self._add_visualiser()
                visualOrigin.setParent(subject)
                visualOrigin.make_vector(self._origin, self._end)
                visualEnd = self._add_visualiser()
                visualEnd.setParent(subject)
                visualEnd.make_vector(self._end, self._point)
                visualPoint = self._add_visualiser()
                visualPoint.setParent(subject)
                visualPoint.make_vector(self._point, self._origin)
                self._visualisers = (visualOrigin, visualEnd, visualPoint)
                

        # ToDo: End the visualiser if not visible.
            
    def __init__(self):
        self._subject = None
        self._visualisers = None

        self._subjectPath = None
        self._restInterface = None
        self._add_visualiser = None
        self._visible = False

        self._offset = None
        self._length = None
        self._radius = None
        self._rotation = None

        self._origin = None
        self._end = None
        self._point = None
        

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
