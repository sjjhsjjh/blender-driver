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
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Module for mathematical operations needed to decompose a rotation matrix.
# https://docs.python.org/3.5/library/math.html
from math import atan2, pow, sqrt, degrees, radians, atan, isclose, fabs
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
    """\
    Get a custom subclass of of KX_GameObject in which the Vector properties are
    mutable at the item level. For example:
    
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
        def physics(self):
            return not self.isSuspendDynamics
        @physics.setter
        def physics(self, physics):
            if physics:
                self.restoreDynamics()
            else:
                self.suspendDynamics(True)

        @property
        def rotation(self):
            return self._rotation
        @rotation.setter
        def rotation(self, rotation):
            if rotation is None:
                # This allows a REST put of None to relinquish control of
                # rotation.
                del self._rotation[:]
            else:
                self._rotation[:] = tuple(rotation)
        @rotation.deleter
        def rotation(self):
            del self._rotation[:]
        
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
        worldOrientation = self._gameObject.worldOrientation.copy()
        worldOrientation.identity()
        #
        # Apply the rotation in each dimension, in order.
        any = False
        for dimension, value in enumerate(self._list):
            if value is not None:
                worldOrientation.rotate(Quaternion(self.axes[dimension], value))
                any = True

        if any:
            self._gameObject.worldOrientation = worldOrientation
    
    def __init__(self, gameObject):
        self._gameObject = gameObject
        self._orientationCache = None
                
        self._set_list_game_object()
        self._listLength = len(self._listGameObject)
        self._list = []
        self._usingList = False

def get_game_text_subclass(bge, GameObject):
    """\
    Get a custom subclass of of KX_FontObject with similar characteristics to
    the KX_GameObject subclass returned by get_game_object_subclass().
    
    This is a function so that this file can be imported outside the context of
    Blender Game Engine. Pass as parameters:
    
    -   A reference to the bge module.
    -   The subclass returned by a previous call to get_game_object_subclass().
    """
    
    class GameText(bge.types.KX_FontObject, GameObject):
        pass

    # KX_FontObject is a very light subclass of KX_GameObject. It seems like it
    # should be possible to instiate a KX_GameObject subclass from an existing
    # KX_FontObject instance, but it isn't allowed. The existing KX_FontObject
    # instance must be passed to a KX_FontObject subclass.
    # The above declaration uses multiple inhertance to give the KX_FontObject
    # subclass all the extra methods in the KX_GameObject subclass without any
    # code.
    
    return GameText

class Cursor(object):
    #
    # Handy constants
    zAxis = Vector((0,0,1))
    #
    # Infrastructure properties and methods.
    #
    @property
    def subjectPath(self):
        return self._subjectPath
    @subjectPath.setter
    def subjectPath(self, subjectPath):
        self._subjectPath = subjectPath
        self._update(True)
    #
    @property
    def restInterface(self):
        return self._restInterface
    @restInterface.setter
    def restInterface(self, restInterface):
        self._restInterface = restInterface
        self._update(True)
    #
    @property
    def add_visualiser(self):
        return self._add_visualiser
    @add_visualiser.setter
    def add_visualiser(self, add_visualiser):
        self._add_visualiser = add_visualiser
        self._update(False)
    #
    @property
    def add_empty(self):
        return self._add_empty
    @add_empty.setter
    def add_empty(self, add_empty):
        self._add_empty = add_empty
        self._update(False)
    @property
    #
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, visible):
        self._visible = visible
        self._update(False)
    #
    # Properties that define the cursor.
    #
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset):
        self._offset = offset
        self._update(False)
    #
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, length):
        self._length = length
        self._update(False)
    #
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, radius):
        self._radius = radius
        if radius is not None:
            self._radiusVector = Vector((radius, 0, 0))
        self._update(False)
    #
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update(False)
    #
    # Helper properties, read-only and based on the subject plus an offset from
    # cache. The offset is updated by setting other properties.
    #
    @property
    def origin(self):
        return self._get_helper(0)
    @property
    def end(self):
        return self._get_helper(1)
    @property
    def point(self):
        return self._get_helper(2)
    #
    def _get_helper(self, index):
        if self._helpers is None:
            return None
        return self._helpers[index].worldPosition.copy()
        
    def _update(self, changedSubject):
        if changedSubject:
            self._subject = None

        if (self._subject is None
            and self._subjectPath is not None
            and self._restInterface is not None
            ):
            self._subject = self.restInterface.rest_get(self.subjectPath)

        subject = self._subject
        if subject is None:
            return None
        #
        # Set the offset properties.
        axisVector = subject.getAxisVect(self.zAxis)
        self._originOffset = (
            None if self._offset is None else self._offset * axisVector)
        if self._originOffset is None:
            self._endOffset = None
        else:
            self._endOffset = self._originOffset.copy()
            if self._length is not None:
                self._endOffset += self._length * axisVector
        if self._endOffset is None:
            self._pointOffset = None
        else:
            self._pointOffset = self._endOffset.copy()
            if self._radius is not None:
                if self._rotation is None:
                    self._pointOffset += subject.getAxisVect(self._radiusVector)
                else:
                    quaternion = Quaternion(self.zAxis, self._rotation)
                    rotationVector = self._radiusVector.copy()
                    rotationVector.rotate(quaternion)
                    self._pointOffset += subject.getAxisVect(rotationVector)
        #
        # Create the helper objects, if they don't exist and can be created now.
        created = False
        if self._helpers is None and self.add_empty is not None:
            created = True
            self._helpers = tuple(self._add_empty() for _ in range(3))
        if self._helpers is not None and (changedSubject or created):
            for helper in self._helpers:
                helper.setParent(subject.tether)
        #
        # Position the helper objects.
        if self._helpers is not None:
            offsets = (self._originOffset, self._endOffset, self._pointOffset)
            for index, helper in enumerate(self._helpers):
                worldPosition = subject.worldPosition.copy()
                if offsets[index] is not None:
                    worldPosition += offsets[index]
                helper.worldPosition = worldPosition

        if self._visible:
            created = False
            if self._visualisers is None and self._add_visualiser is not None:
                self._visualisers = tuple(
                    self._add_visualiser() for _ in range(3))
                created = True

            if self._visualisers is not None and (changedSubject or created):
                for visualiser in self._visualisers:
                    visualiser.setParent(subject.tether)

            if self._visualisers is not None:
                self._visualisers[0].make_vector(self.origin, self.end)
                self._visualisers[1].make_vector(self.end, self.point)
                self._visualisers[2].make_vector(self.point, self.origin)

        # ToDo: End the visualisers if not visible, and set self._visualisers = None.

    def __init__(self):
        self._subject = None
        self._visualisers = None
        self._helpers = None

        self._subjectPath = None
        self._restInterface = None
        self._add_visualiser = None
        self._add_empty = None
        self._visible = False

        self._offset = None
        self._length = None
        self._radius = None
        self._rotation = None

        self._radiusVector = None
        self._originOffset = None
        self._endOffset = None
        self._pointOffset = None
        
def get_camera_subclass(bge, GameObject):
    KX_Camera = bge.types.KX_Camera
    
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
            
        @property
        def animationPath(self):
            '''Where the camera will put tracking animations that it creates.'''
            return self._animationPath
        @animationPath.setter
        def animationPath(self, animationPath):
            self._animationPath = animationPath
            self._pointAtSubject()
            
        @property
        def selfPath(self):
            return self._selfPath
        @selfPath.setter
        def selfPath(self, selfPath):
            self._selfPath = selfPath
            self._pointAtSubject()
            
        @property
        def trackSpeed(self):
            return self._trackSpeed
        @trackSpeed.setter
        def trackSpeed(self, trackSpeed):
            self._trackSpeed = trackSpeed
            self._small = trackSpeed * 0.1
            self._pointAtSubject()
        
        def _get_subject(self):
            if (self._subject is None
                and self._subjectPath is not None
                and self._restInterface is not None
            ):
                self._subject = self.restInterface.rest_get(self.subjectPath)
            
            return self._subject

        def _pointAtSubject(self):
            """\
            Calculate the rotation needed to make the camera point at its
            subject, and then apply it.
            """
            subject = self._get_subject()
            if subject is None:
                return False
            #
            # Get an offset vector in world coordinates from the camera to the
            # target. The offset vector is normalised.
            (dist, worldv, localv) = self.getVectTo(subject.point)
            #
            # This looks pretty expensive, even for a debug, so it's commented
            # out.
            # log(DEBUG
            #     , "Camera 0 {} {} ({:.2f}, {:.2f}, {:.2f})"
            #     " ({:.2f}, {:.2f}, {:.2f}) point{} position{}"
            #     , degrees(atan2(1.0, 0)), degrees(atan2(-1.0, 0))
            #     , *tuple(dist * _ for _ in worldv)
            #     , *tuple(degrees(_) for _ in self.rotation)
            #     , subject.point, self.worldPosition[:])
            #
            # Convenience variables for the offset in each dimension.
            ox = worldv[0]
            oy = worldv[1]
            oz = worldv[2]
            #
            # Variables for the rotation in each dimension.
            # In the calculation as it is now, Y will always be zero.
            rotx = 0.0
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
            log(DEBUG, 'ox {:.2f} {:.2f} {:.2f}'
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
            #
            # What the code does is to negate the atan portion if oy is
            # negative. Could there be a calculation that generates a negative
            # value, if oy is negative? I haven't found one.
            if oy < 0.0:
                rotx = radians(90.0) - atan2(oz, oy)
                log(DEBUG, 'oy negative {:.2f} {:.2f} {:.2f} {:.2f}'
                    , oz, oy, degrees(atan2(oz, oy)), degrees(rotx))
            else:
                rotx = radians(90.0) + atan2(oz, oy)
                log(DEBUG, 'oy positive {:.2f} {:.2f} {:.2f} {:.2f}'
                    , oz, oy, degrees(atan2(oz, oy)), degrees(rotx))
            #
            # Apply it, either directly or by pending an animation.
            self._apply_rotation(rotx, 0.0, rotz)
            log(DEBUG, 'New rotation {:.2f} {:.2f} {:.2f} {:.2f}'
                , rotx, degrees(rotx), rotz, degrees(rotz))
        
        def _apply_rotation(self, rotX, rotY, rotZ):
            if (self.animationPath is None
                or self.restInterface is None
                or self.selfPath is None
            ):
                self.rotation = (rotX, rotY, rotZ)
                self._trackRotation = None
            else:
                self._trackRotation = (rotX, rotY, rotZ)
        
        def tick(self, tickPerf):
            # Rotate the camera, either directly or by animation.
            #
            # If there isn't a pending rotation from a setter, the camera still
            # might need to rotate, if its subject is moving.
            if self._trackRotation is None:
                self._pointAtSubject()
            #
            # If it isn't possible to animate, do nothing.
            if (self.animationPath is None
                or self.restInterface is None
                or self.selfPath is None
            ):
                return

            if self._trackRotation is None:
                # ToDo: Tidy up completed track animations by setting to None.
                # Also reset animated rotations, like this:
                # self.rotation[:] = (None, None, None)
                return

            if self._trackRotationLast is None:
                # Initialise the last rotation sent to be a copy of the current
                # rotation.
                self._trackRotationLast = self.rotation[:]

            animationPath = list(self.animationPath)
            for index, target in enumerate(self._trackRotation):
                #
                # Convenience variables for this dimension.
                rotation = self.rotation[index]
                last = self._trackRotationLast[index]
                animationPath.append(index)
                #
                # A change will be considered small, and done directly without
                # an animation, if it would be done within a fraction of a
                # second.
                log(DEBUG
                    , 'track rotation [{}] {:.2f} {:.2f} {:.2f} {:.2f}'
                    , index, degrees(target), degrees(rotation), degrees(last)
                    , degrees(self._small))
                #
                # If the new target is the same as the last target, do nothing.
                # If the new target is close to the current rotation, apply
                # directly, unless it's very close, in which case do nothing.
                # Otherwise, load an animation.
                if (last is not None
                    and isclose(target, last, abs_tol=radians(0.1))
                ):
                    log(DEBUG, '[{}] same.', index)
                else:
                    speed, change = self._get_speed(rotation, target)
                    if speed is None:
                        log(DEBUG, '[{}] small.', index)
                        self.restInterface.rest_put(None, animationPath)
                        #
                        # If the required rotation isn't very small, apply it.
                        if fabs(change) > radians(0.1):
                            self.rotation[index] = target
                    else:
                        log(DEBUG, '[{}] large {:.2f} {:.2f} {:.2f}'
                            , index, degrees(change), degrees(speed)
                            , degrees(self.trackSpeed))
                        #
                        # Assemble the animation in a dictionary.
                        animation = {
                            'valuePath': tuple(self.selfPath) + ('rotation', index),
                            'targetValue': target, 'speed': speed,
                            'modulo': radians(360)
                        }
                        #
                        # Insert the animation. The point maker will set the
                        # store attribute.
                        self.restInterface.rest_put(animation, animationPath)
                        #
                        # Set the start time, which has the following side
                        # effects:
                        # -   Retrieves the start value.
                        # -   Clears the complete state.
                        animationPath.append('startTime')
                        self.restInterface.rest_put(tickPerf, animationPath)
                        del animationPath[-1]
                        self._trackRotationLast[index] = target
                del animationPath[-1]
            
            self._trackRotation = None
        
        def _get_speed(self, current, target):
            change = target - current
            trackSpeed = self.trackSpeed
            if change > radians(0.0):
                if change > radians(180.0):
                    change = radians(360) - change
                    trackSpeed *= -1.0
            else:
                if change > radians(-180.0):
                    trackSpeed *= -1.0
                else:
                    change += radians(360)

            return (None if fabs(change) < self._small else trackSpeed, change)

        @property
        def orbitDistance(self):
            """\
            Distance from the camera to its subject, or None if there is no
            subject.
            """
            subject = self._get_subject()
            if subject is None:
                return None
            #
            # Extract the distance part of the getVectTo, which is the first
            # value in the returned tuple.
            return self.getVectTo(subject.point)[0]
        @orbitDistance.setter
        def orbitDistance(self, orbitDistance):
            subject = self._get_subject()
            if subject is None:
                return
            #
            # Getter for the next line will give this code a copy of the Vector.
            point = subject.point
            #
            # Extract the normalised vector offset part of the getVectTo, which
            # is the second value in the returned tuple.
            vector = self.getVectTo(point)[1]
            #
            # Negative distance values are treated as zero. Maybe they should
            # raise ValueError instead.
            if orbitDistance > 0:
                #
                # Direction of vector is from the camera to the subject. Deduct
                # it from the point in order to negate it, so moving from the
                # point towards the camera current position.
                point -= vector * orbitDistance
            self.worldPosition = point

        @property
        def orbitAngle(self):
            """\
            Current angle in radians of orbit of the camera around the subject,
            supposing an orbit with a Z axis, or None if there is no subject.
            """
            subject = self._get_subject()
            if subject is None:
                return None
            (distance, worldVector, _) = self.getVectTo(subject.point)
            # Originally had a line like the following, but it caused a Blender
            # crash.
            # flatVector = (worldVector * distance).resized(2)
            # It's probably less efficient anyway, because it allocates a new
            # Vector object or two.
            worldVector *= distance
            worldVector.resize(2)
            xZero = Vector((worldVector.magnitude, 0))
            return xZero.angle_signed(worldVector, 0.0)
        @orbitAngle.setter
        def orbitAngle(self, orbitAngle):
            subject = self._get_subject()
            if subject is None:
                return
            #
            # Getter for the next line will give this code a copy of the Vector.
            point = subject.point
            (distance, vector, _) = self.getVectTo(point)
            vector *= distance
            flatVector = vector.resized(2)
            xZero = Vector((flatVector.magnitude, 0))
            currentAngle = xZero.angle_signed(flatVector, 0)
            changeAngle = orbitAngle - currentAngle
            quaternion = Quaternion((0.0, 0.0, -1.0), changeAngle)
            vector.rotate(quaternion)
            self.worldPosition = point - vector
            self._pointAtSubject()

        def __init__(self, *args):
            self._subjectPath = None
            self._restInterface = None
            self._animationPath = None
            self._trackSpeed = None
            self._selfPath = None
            
            self._subject = None
            self._trackRotation = None
            self._trackRotationLast = None
            self._small = None

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
