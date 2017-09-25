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
from math import atan2, pow, sqrt, degrees, radians, atan
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine KX_Camera
# https://docs.blender.org/api/blender_python_api_current/bge.types.KX_Camera.html
# Can't be imported here because this module gets imported in the bpy context
# too, in which bge isn't available.
#
# Blender Game Engine KX_GameObject
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
    
    This is a function so that this file can be imported outside the context of
    Blender Game Engine. Pass as a parameter a reference to the bge module.
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
        def tether(self):
            return self._tether
        @tether.setter
        def tether(self, tether):
            self._tether = tether
            self.update()
            
        def update(self):
            if self.tether is not None:
                self.tether.worldPosition = self.worldPosition.copy()
                self.tether.worldOrientation = self.worldOrientation.copy()

        @property
        def rotation(self):
            return self._rotation
        @rotation.setter
        def rotation(self, rotation):
            self._rotation[:] = tuple(rotation)
        
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
            self._tether = None

    return GameObject
        
class Rotation(object):
    """Class to represent the x,y,z rotation of a Blender game object."""

    # Each instance of this class has three lists:
    #
    # -   _listGameObject, which is created with maths from the rotation matrix
    #     of the game object.
    # -   _listSet, which only has elements that have been set externally.
    # -   _list, which is a cache in which each element is the _listSet value,
    #     if it has been set, or the _listGameObject value otherwise.
    #
    # The game object and cache lists are maintained by the getters and setters
    # of the class.
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
    # ToDo: A better model could be as follows.
    #
    # -   Indicate relinquishment of control by deleting from the list, actually
    #     the set list.
    # -   In principle, if the game object list is longer than the set list, the
    #     excess elements fill in the blanks. In practice, the set list will
    #     either have zero elements or the same number of elements as the game
    #     object list.
    # -   When any element is set and the set list isn't long enough, copy the
    #     game object list to the set list.
    
    axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    
    def _set_list_game_object(self, cache):
        """Set the list property from the rotation of the game object."""
        orientation = self._gameObject.worldOrientation
        if self._orientationCache == orientation:
            log(DEBUG, 'Used orientationCache')
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
            atan2(orientation[1][0], orientation[0][0])
        )
        #
        # Apply it to the cache.
        if cache:
            self._update_list()

    def _update_list(self):
        for index, setValue in enumerate(self._listSet):
            self._list[index] = (
                self._listGameObject[index] if setValue is None else setValue)
    
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
        self._set_list_game_object(True)
        return self._list.__getitem__(specifier)
    
    def __setitem__(self, specifier, value):
        self._listSet.__setitem__(specifier, value)
        self._update_list()
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
        any = False
        for dimension, value in enumerate(self._listSet):
            if value is not None:
                worldOrientation.rotate(Quaternion(self.axes[dimension], value))
                any = True

        if any:
            self._gameObject.worldOrientation = worldOrientation
    
    def __init__(self, gameObject):
        self._gameObject = gameObject
        self._orientationCache = None
        
        self._set_list_game_object(False)
        self._listSet = [None] * len(self._listGameObject)
        self._list = self._listSet[:]
        self._update_list()

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
    # Helper properties, read-only from cache updated by setting other
    # properties.
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
                visualOrigin.make_vector(self._origin, self._end)
                visualEnd = self._add_visualiser()
                visualEnd.make_vector(self._end, self._point)
                visualPoint = self._add_visualiser()
                visualPoint.make_vector(self._point, self._origin)

                self._visualisers = (visualOrigin, visualEnd, visualPoint)
                for visualiser in self._visualisers:
                    visualiser.setParent(subject.tether)
                

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
        
def get_camera_subclass(bge):
    KX_Camera = bge.types.KX_Camera
    GameObject = get_game_object_subclass(bge)
    
    class Camera(GameObject, KX_Camera):
        
        # Hmm. Both Cursor and Camera have the following two properties. This
        # class has a different update, and is a subclass of GameObject. Its
        # subject is a Cursor, not a GameObject.
        
        @property
        def restInterface(self):
            return self._restInterface
        @restInterface.setter
        def restInterface(self, restInterface):
            self._restInterface = restInterface
            self._pointAtSubject()

        @property
        def subjectPath(self):
            return self._subjectPath
        @subjectPath.setter
        def subjectPath(self, subjectPath):
            self._subjectPath = subjectPath
            self._pointAtSubject()
        
        def _pointAtSubject(self):
            """
            Calculate the rotation needed to make the camera point at its subject,
            and then apply it. Returns a Boolean for whether any rotation was
            needed.
            """
            if self._subjectPath is None or self.restInterface is None:
                return False
            subject = self.restInterface.rest_get(self.subjectPath)
            #
            # Get an offset vector in world coordinates from the camera to the
            # target. The offset vector is normalised.
            (dist, worldv, localv) = self.getVectTo(subject.point)
            #
            # Get the current camera rotation. It's used to check whether any
            # rotation is needed to point at the object, which happens at the end of
            # the method but it's nice to dump it here if in diagnostic mode.
            rotation = self.rotation[:]
            log(DEBUG
                , "Camera 0 {} {} ({:.2f}, {:.2f}, {:.2f})"
                " ({:.2f}, {:.2f}, {:.2f}) point{} position{}"
                , degrees(atan2(1.0, 0)), degrees(atan2(-1.0, 0))
                , *tuple(dist * _ for _ in worldv)
                , *tuple(degrees(_) for _ in rotation)
                , subject.point, self.worldPosition[:])
            #
            # Convenience variables for the offset in each dimension.
            ox = worldv[0]
            oy = worldv[1]
            oz = worldv[2]
            #
            # Variables for the rotation in each dimension.
            # In the calculation as it is now, Y will always be zero.
            rotx = 0.0
            roty = 0.0
            rotz = 0.0
            #
            # Calculate the Z rotation, based on the X and Y offsets.
            #
            # Using atan2 instead of atan is better in a couple of ways:
            # -   Doesn't attempt to divide by zero if ox == 0.
            # -   Sign of the output is based on the signs of the inputs.
            #
            # The intention is to rotate the camera without flipping over, i.e.
            # not like a flight simulator.
            # Crib sheet:
            # -   atan(zero) is zero.
            # -   atan(infinity) is 90 degrees.
            rotz = atan2(oy, ox) - radians(90.0)
            log(INFO, 'ox {:.2f} {:.2f} {:.2f}'
                , ox, oy/ox if ox < 0.0 or ox > 0.0 else oy, degrees(rotz))
            #
            # Rotate the offset about the Z axis in such a way that the X offest
            # will be zero. This is necessary to normalise the X axis rotation
            # calculation. Think of the subject as being on the surface of a
            # sphere, and the camera at the centre of the sphere. The
            # normalisation has the effect of moving the target along a line of
            # latitude on the sphere.
            worldv.rotate(Matrix.Rotation(rotz * -1.0, 4, 'Z'))
            log(DEBUG, 'normz {} {:.2f}', worldv, degrees(rotz * -1.0))
            #
            # Reset the convenience variables, from the normalised offset vector.
            # X offset will always be zero in the adjusted vector.
            oy = worldv[1]
            oz = worldv[2]
            #
            # Calculate the X rotation, based on the normalised Z and Y offsets.
            #
            # If the camera is either directly above or below the target, oy
            # will be zero. In that case, we either look up or down, depending
            # on oz. If oy is zero then atan(oz, oy) is either 90 degrees or -90
            # degrees, depending on whether oz is positive or negative. So, no
            # special case is needed.
            if oy < 0.0:
                rotx = radians(90.0) - atan2(oz, oy)
                log(INFO, 'oy negative {:.2f} {:.2f} {:.2f} {:.2f}'
                    , oz, oy, degrees(atan2(oz, oy)), degrees(rotx))
            else:
                rotx = radians(90.0) + atan2(oz, oy)
                log(INFO, 'oy positive {:.2f} {:.2f} {:.2f} {:.2f}'
                    , oz, oy, degrees(atan2(oz, oy)), degrees(rotx))


            #
            # Check if any rotation was needed to point the camera at the target.
            return_ = \
                  abs( rotation[0] - rotx ) > 0.001 or \
                  abs( rotation[1] - roty ) > 0.001 or \
                  abs( rotation[2] - rotz ) > 0.001
            #
            # Apply the rotation.
            newRotation = (rotx, roty, rotz)
            log(INFO, 'New rotation {} {} {}', return_, newRotation
                , tuple(degrees(_) for _ in newRotation))
            self.rotation = newRotation
            #
            # Return true if any rotation was needed.
            return return_

        def __init__(self, *args):
            self._subjectPath = None
            self._restInterface = None

            super().__init__(*args)
    
    return Camera

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
