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
from math import atan2, degrees, radians, isclose, fabs
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Matrix, Quaternion

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
