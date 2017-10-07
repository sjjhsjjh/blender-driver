#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

This code illustrates:

-   Use of the Animation base class and PathAnimation subclass.

This module can only be used from within the Blender Game Engine."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
# The import isn't needed because this class uses the base class to get an
# object.
# import argparse
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Module for degrees to radian conversion.
# https://docs.python.org/3.5/library/math.html
from math import degrees, radians
#
# Third party modules, in alphabetic order.
#
# Blender library imports, in alphabetic order.
#
# Main Blender Python interface, which is used to get the size of a mesh.
# Import isn't needed because the base class keeps a reference to the interface
# object.
# import bpy
#
# Blender Game Engine KX_GameObject
# Import isn't needed because this class gets an object that has been created
# elsewhere.
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
#
# Blender Game Engine maths utilities, which can only be imported if running
# from within the Blender Game Engine.
# Import isn't needed because this class gets a Vector from the bpy layer.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Matrix, Quaternion
#
# Local imports.
#
# Blender Driver application with background banner.
from . import restanimation
#
# Wrapper for Blender game object that is easy to make RESTful.
from path_store.blender_game_engine import get_camera_subclass, Cursor
#
# RESTful interface base class and Animation subclass for pathstore.
from path_store.rest import AnimatedRestInterface

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(restanimation.Application):
    
    templates = {
        'cube': {
            'subtype':'Cube', 'physicsType':'RIGID_BODY',
            'location': (0, 0, 0)},
        'visualiser': {
            'subtype':'Cube', 'physicsType':'NO_COLLISION',
            'location': (0, 0, 0), 'scale': (0.1, 0.1, 0.1)},
        'empty': {
            'subtype':'Empty', 'physicsType':'NO_COLLISION',
            'location': (0, 0, 0)},
        'floor': {
            'subtype':'Cube', 'physicsType':'STATIC',
            'location': (0, 0, -4.0), 'scale': (10, 10, 0.1)}
    }

    # Override.
    _instructions = "\n".join((
        "Ctrl-Q to terminate; space, plus, minus, or 0 to move object 0;"
        , "< or > to rotate it;"
        , "plus Ctrl to move object 2. Object 1 doesn't move. TBD"))

    # Override.
    _objectRootPath = ('root','objects')
    
    # Default starting values for the camera, which don't get used actually.
    _cameraStartPosition = [0.0, 2.0, 0.0]
    _cameraStartOrientation = (radians(90.0), 0.0, radians(45.0))
    #
    # Camera speed.
    _cameraLinear = 9.0
    _cameraAngular = radians(_cameraLinear * 15.0)

    def _add_visualiser(self):
        return self._GameObject(self.game_add_object('visualiser'))
    def _add_empty(self):
        return self._GameObject(self.game_add_object('empty'))

    # Overriden.
    def game_initialise(self):
        # Base class initialise will instantiate the restInterface and add the
        # game objects.
        super().game_initialise()
        
        self.mainLock.acquire()
        try:
            #
            # Add tethers and cursors to game objects.
            #
            # Working paths.
            path = list(self._objectRootPath)
            cursorPath = ['root', 'cursors']
            #
            # Loop for each object, by number.
            for index in range(self._objectCount):
                #
                # Every object will have a cursor, so every object needs a
                # tether. Tethers don't need to be accessible to the path store.
                path.append(index)
                object_ = self._restInterface.rest_get(path)
                object_.tether = self._add_empty()
                #
                # Add the cursor to this object, and insert it into the path
                # store.
                #
                # Set the cursor working path and create a new Cursor object.
                cursorPath.append(index)
                cursor = Cursor()
                #
                # Give the cursor the means to add necessary objects.
                cursor.add_visualiser = self._add_visualiser
                cursor.add_empty = self._add_empty
                #
                # Cursor needs a restInterface to get an object from the path.
                cursor.restInterface = self._restInterface
                #
                # Put the cursor in the path store.
                self._restInterface.rest_put(cursor, cursorPath)
                #
                # Set all its parameters except visibility in a big patch. Then
                # set visibility in a single put, so that it gets set last.
                self._restInterface.rest_patch({
                    'subjectPath': tuple(path),
                    'offset': 3.0, 'length': 4.0, 'radius': 2.0,
                    'rotation': radians(90)
                }, cursorPath)
                cursorPath.append('visible')
                self._restInterface.rest_put(True, cursorPath)
                #
                # Revert the working paths.
                del cursorPath[-2:]
                del path[-1:]
                
                if index == 0:
                    for index, value in enumerate(cursor.point):
                        self._cameraStartPosition[index] += value
            #
            # Add the floor object, which is handy to stop objects dropping out
            # of sight due to gravity.
            object_ = self._GameObject(self.game_add_object('floor'))
            path[-1] = 'floor'
            self._restInterface.rest_put(object_, path)
            # Note that path now points to floor.
            
            self._Camera = get_camera_subclass(self.bge)
            object_ = self._Camera(self.gameScene.active_camera)
            object_.restInterface = self._restInterface
            path[-1] = 'camera'
            self._restInterface.rest_put(object_, path)
            self._restInterface.rest_patch(
                {
                    'worldPosition': self._cameraStartPosition,
                    'rotation': self._cameraStartOrientation
                }, path)
            path.append('subjectPath')
            self._restInterface.rest_put(cursorPath + [0], path)
            # Note that path now points to the camera subjectPath.
            
            log(INFO, "Objects, cursors, floor, camera: {}"
                , self._restInterface.rest_get())
            
        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        # Base class tick isn't run.
        # super().game_tick_run()
        self.mainLock.acquire()
        try:
            # Same as in the base class but here we will do something with the
            # completions.
            completions = self._restInterface.set_now_times(self.tickPerf)
            for specifier, completed in completions:
                userData = completed.userData
                log(DEBUG, 'Complete "{}" {}', specifier, userData)
                #
                # Check if there are still other animations going on for this
                # object.
                animations = self._restInterface.rest_get('animations')
                still = False
                for _, animation in animations.items():
                    if animation is None:
                        continue
                    otherData = animation.userData
                    if (
                        otherData is not None and userData is not None
                        and otherData['number'] == userData['number']
                        and not animation.complete
                    ):
                        still = True
                #
                # If there are no other animations: restore physics to the
                # object and reset its rotation overrides.
                if not still and userData is not None:
                    object_ = self._restInterface.rest_get(userData['path'])
                    log(INFO, "Restoring {}.", userData['path'])
                    object_.restoreDynamics()
                    object_.rotation[:] = (None, None, None)
                #
                # Discard the completed animation object, so that the above and
                # other loops can run faster.
                self._restInterface.rest_put(None, ('animations', specifier))

            #
            # Update all cursors, by updating all physics objects.
            gameObjects = self._restInterface.rest_get(self._objectRootPath)
            for gameObject in gameObjects:
                gameObject.update()
            
            
            # Bodge the camera.
            self._restInterface.rest_put(
                ('root', 'cursors', 0), ('root', 'camera', 'subjectPath'))

        finally:
            self.mainLock.release()

    # Override.
    # No override for game_keyboard but there is for this.
    def _keyboard_command(self, keyString, objectNumber):
        #
        # First, do whatever the base class does.
        inSuper = super()._keyboard_command(keyString, objectNumber)
        #
        # Then do what this class does.
        if keyString == "0":
            for dimension, _ in enumerate(self._cameraStartPosition):
                self.move_camera(dimension, 0)
        elif keyString == "a":
            self.stop_camera()
            self._restInterface.rest_put(
                ('root', 'cursors', 0), ('root', 'camera', 'subjectPath'))
        elif keyString == "o":
            self.move_camera(3, 1)
        elif keyString == "O":
            self.move_camera(3, -1)
        elif keyString == "p":
            self.move_camera(4, 1)
        elif keyString == "P":
            self.move_camera(4, -1)
        elif keyString == "x":
            self.move_camera(0, 1)
        elif keyString == "X":
            self.move_camera(0, -1)
        elif keyString == "y":
            self.move_camera(1, 1)
        elif keyString == "Y":
            self.move_camera(1, -1)
        elif keyString == "z":
            self.move_camera(2, 1)
        elif keyString == "Z":
            self.move_camera(2, -1)
        else:
            return inSuper
        
        return True
    
    def stop_camera(self, dimensions=range(5)):
        valuePath = self._objectRootPath[:-1] + ('camera', 'orbitAngle')
        log(INFO, "Camera orbitAngle: {:.2f}"
            , degrees(self._restInterface.rest_get(valuePath)))
        for dimension in dimensions:
            animationPath = self._animation_path(dimension)
            self._restInterface.rest_put(None, animationPath)
    
    def _animation_path(self, dimension):
        return ['animations', 'camera_{:d}'.format(dimension)]
    
    def move_camera(self, dimension, direction):
        #
        # Convenience variable.
        restInterface = self._restInterface
        #
        # Path to the camera's position in the specified dimension.
        valuePath = self._objectRootPath[:-1]
        #
        # Set the value path and stop any incompatible movement.
        # X, Y, and Z (dimensions 0, 1, and 2) are incompatible with 3.
        # X and Y are incompatible with 4.
        if dimension < 3:
            valuePath += ('camera', 'worldPosition', dimension)
            if dimension == 2:
                self.stop_camera((3,))
            else:
                self.stop_camera(range(3,5))
        elif dimension == 3:
            valuePath += ('camera', 'orbitDistance')
            self.stop_camera(range(3))
        elif dimension == 4:
            valuePath += ('camera', 'orbitAngle')
            self.stop_camera(range(2))
        else:
            raise ValueError()
        #
        # Assemble the animation in a dictionary, starting with this.
        animation = {'path': valuePath}
        #
        # Set a target value, if needed.
        if direction == 0:
            animation['targetValue'] = self._cameraStartPosition[dimension]
        elif dimension == 3 and direction < 0:
            # Make it zoom in, but only to a distance of 1.0, so that it never
            # gets to be in the same place as the thing it's trying to point at.
            animation['targetValue'] = 1.0
        #
        # Set a speed and modulo.
        if dimension == 4:
            animation['modulo'] = radians(360)
            animation['speed'] = self._cameraAngular * float(direction)
        else:
            animation['modulo'] = 0
            if direction == 0:
                animation['speed'] = self._cameraLinear * 2.0
            else:
                animation['speed'] = self._cameraLinear * float(direction)
        #
        # There is up to one camera movement per dimension.
        animationPath = self._animation_path(dimension)
        #
        # Insert the animation. The point maker will set the store
        # attribute.
        log(DEBUG, 'Patching {} {}', animationPath, animation)
        restInterface.rest_put(animation, animationPath)
        #
        # Set the start time, which has the following side effects:
        # -   Retrieves the start value.
        # -   Clears the complete state.
        animationPath.append('startTime')
        restInterface.rest_put(self.tickPerf, animationPath)
        log(INFO, "Animations {}"
            , self._restInterface.rest_get(('animations',)))
    
    # Override.
    def _prepare_animation(self, animation):
        # Override the animation preparation to do things needed when there is
        # Physics.
        objectPath = animation['userData']['path']
        object_ = self._restInterface.rest_get(objectPath)
        log(INFO, "Suspending {}.", objectPath)
        object_.suspendDynamics(True)
        # ToDo: Near here, copy all the rotation values into the setList in case
        # one of them is being animated. Or maybe do that in the Rotation class.
        #
        # This could maybe be moved to the GameObject class and included in a
        # setter for suspendPhysics.
