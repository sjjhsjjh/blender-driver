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
# https://docs.python.org/3/library/math.html
from math import atan2, degrees, radians, fabs, fmod, pi
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine KX_Camera
# https://docs.blender.org/api/blender_python_api_current/bge.types.KX_Camera.html
# Can't be imported here because this module gets imported in the bpy context
# too, in which bge isn't available.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Matrix, Quaternion

_TwoPI = pi * 2.0

def angular_move(current, target, speed=1.0):
    def positive_angle(angle):
        angle = fmod(angle, _TwoPI)
        return _TwoPI + angle if angle < 0.0 else angle

    change = positive_angle(positive_angle(target) - positive_angle(current))
    if change > pi:
        speed *= -1.0
        change = change - _TwoPI
    
    return speed, current + change, fabs(change)

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
            # self._small = fabs(trackSpeed * 0.1)
            self._animateThreshold = fabs(trackSpeed * 0.1)
            self._pointAtSubject()

        # Override the setter to normalise the rotation Euler.
        def _beingAnimatedSetter(self, beingAnimated):
            if self._beingAnimated and not beingAnimated:
                # vector, angle = self._to_subject()
                # print('camera animation end.'
                #       , vector, degrees(angle), self.rotation)
                del self.rotation
                # vector, angle = self._to_subject()
                # print('camera rotation deleted.'
                #       , vector, degrees(angle), self.rotation)
            self._beingAnimated = beingAnimated

        beingAnimated = property(
            GameObject.beingAnimated.fget, _beingAnimatedSetter)
        
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
            worldv, angle = self._to_subject()
            if worldv is None:
                return False

            # if angle >= self._directThreshold:
            #     print('point at', degrees(angle), degrees(self._directThreshold)
            #           , '<' if angle < self._directThreshold else '')
            
            
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
            
            # This calculation generates two values that are suitable to apply
            # in the order X rotation, then Z rotation. The default Euler order
            # is XYZ, so the calculation is compatible with that and the order
            # never needs to be changed.
            #
            # Apply the values, either directly or by animation.
            self._apply_rotation(rotx, 0.0, rotz)
            log(DEBUG, 'New rotation {:.2f} {:.2f} {:.2f} {:.2f}'
                , rotx, degrees(rotx), rotz, degrees(rotz))
            
            return True
        
        def _to_subject(self):
            subject = self._get_subject()
            if subject is None:
                return None, None
            #
            # Get an offset vector in world coordinates from the camera to the
            # target. The offset vector is normalised.
            worldv = self.getVectTo(subject.point)[1]
            # If worldv is zero-length, angle will be 0.
            angle = fabs(
                self.getAxisVect(Vector((0, 0, -1))).angle(worldv, 0.0))
            return worldv, angle
        
        def _apply_rotation(self, rotX, rotY, rotZ):
            unapplied = 0
            
            # If rotation cannot be animated yet, apply directly.
            if (self.animationPath is None
                or self.restInterface is None
                or self.selfPath is None
            ):
                self.rotation = (rotX, rotY, rotZ)
                return unapplied

            # Retrieve the incumbent tracking animations, if any.
            try:
                animations = self.restInterface.rest_get(self.animationPath)
            except KeyError:
                animations = (None, None, None)

            # Create a mutable path that can be used to put an animation object
            # into each dimension.
            animationPath = [None]
            animationPath[0:0] = self.animationPath

            # Convenience variable for the current rotation, if needed.
            rotation = None

            for dimension, newTarget in enumerate((rotX, rotY, rotZ)):
                # Get the current rotation, which could be an animation target.
                #
                # It could be argued that it isn't worth getting the current
                # rotation if the change in this dimension isn't going to be
                # animated. Getting the rotation could incur some maths in the
                # Rotation instance. However setting the value could incur maths
                # too. Getting the value makes it possible to check the delta
                # and then avoid setting if unnecessary.
                if animations[dimension] is None:
                    if rotation is None:
                        rotation = self.rotation[:]
                    currentTarget = rotation[dimension]
                else:
                    currentTarget = animations[dimension].targetValue

                # Calculate the required move.
                speed, effectiveTarget, change = angular_move(
                    currentTarget, newTarget, self._trackSpeed)
                
                animation = None
                message = None
                if change < self._animateThreshold:
                    if change < self._applyThreshold:
                        message = 'Below apply threshold'
                        unapplied += 1
                    else:
                        if animations[dimension] is None:
                            message = 'Setting {:.2f}'.format(
                                degrees(effectiveTarget))
                            self.rotation[dimension] = effectiveTarget
                        else:
                            # The code gets here if there is a current animation
                            # that doesn't reach the required value but isn't
                            # far off. Leave it to finish, after which it will
                            # be removed and adjustments can be made.
                            message = 'Leaving'
                            unapplied += 1
                else:
                    if animations[dimension] is None:
                        message = 'Animating to {:.2f}'.format(
                            degrees(effectiveTarget))
                        animation = {
                            'subjectPath': self.selfPath[:],
                            'valuePath': tuple(self.selfPath
                                               ) + ('rotation', dimension),
                            'targetValue': effectiveTarget, 'speed': speed,
                            'modulo': radians(360)
                        }
                        # Rely on implicitStart, which is True by default.
                    else:
                        # The code gets here if there is an incumbent animation
                        # whose target is significantly different to the
                        # required value. This could be due to the camera
                        # moving, or the subject moving, or both.
                        # Stop the incumbent animation so that it gets culled
                        # and this code can create a new animation next tick.
                        message = 'Stopping'
                        unapplied += 1
                        animations[dimension].stopped = True
                        
                        # A previous version of this code attempted to manage
                        # the incumbent animation, for example by changing its
                        # target value, or by reversing its speed. It gets too
                        # tricky to modify running animations, because they are
                        # simple structures that just set a value based on
                        # elapsed time.

                # if change > self._applyThreshold:
                #     print('_apply_rotation [{}] {} from {:.2f} to {:.2f} e:{:.2f}'
                #           ' s:{:.2f} c:{:.2f} {}.'.format(
                #             dimension, self.beingAnimated
                #             , degrees(currentTarget), degrees(newTarget)
                #             , degrees(effectiveTarget), degrees(speed)
                #             , degrees(change), message))
                #             # , ' ' if animations[dimension] is None else "\n"
                #             # , (None if animations[dimension] is None else
                #             #    animations[dimension].__dict__)
                #             # , ' ' if animation is None else "\n", animation))

                # Insert the animation. The point maker will set the store
                # attribute.
                if animation is not None:
                    animationPath[-1] = dimension
                    self.restInterface.rest_patch(animation, animationPath)
                
            return unapplied
        
        def tick(self, tickPerf):
            # Rotate the camera, either directly or by animation. This must be
            # called by the Application, in game_tick_run.
            #
            # If there isn't a pending rotation from a setter, the camera still
            # might need to rotate, if its subject is moving.
            self._pointAtSubject()
        
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
            distance, worldVector = self.getVectTo(subject.point)[0:2]
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
            self._applyThreshold = radians(0.1)
            
            # It seems like the orientation of the camera isn't initialised, or
            # isn't initialised to the identity, by BGE. Make sure it is
            # initialised here.
            self.worldOrientation.identity()

            super().__init__(*args)
    
    return Camera
