#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
# Blender Driver application with HTTP server.
import blender_driver.application.http

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
    _instructions = (
        "Ctrl-Q to terminate; space, numeric plus, minus,"
        "\nor 0 to move left object; < or > to rotate it;"
        "\nplus Ctrl to move right object. Middle object doesn't move."
        "\no, p, x, y, z to move the camera, or a to stop it."
        "\nTAB to move the cursor. s or S to change sizes.")

    # Location of the UI cursor.
    _cursorPath = ['root', 'cursors', 0]
    
    # Start position for the camera.
    _cameraStartOffset = (0.0, 2.0, 0.0)
    _cameraStartPosition = [None] * len(_cameraStartOffset)
    # Default starting values for the camera, which don't get used actually.
    _cameraStartOrientation = (radians(90.0), 0.0, radians(45.0))
    #
    # Camera speed.
    _cameraLinear = 9.0
    _cameraAngular = radians(_cameraLinear * 15.0)

    # Overriden.
    def game_initialise(self):
        # Base class initialise will instantiate the restInterface and add the
        # game objects.
        super().game_initialise()
        
        with self.mainLock:
            #
            # Add tethers and cursors to game objects.
            #
            # Working paths.
            path = list(self.gameObjectPath)
            #
            # Loop for each object, by number.
            for index in range(self._objectCount):
                #
                # Any object could have a cursor, so every object needs a
                # tether. Tethers don't need to be accessible to the path store.
                path.append(index)
                object_ = self._restInterface.rest_get(path)
                object_.tether = self._add_empty()
                #
                # Revert the working path.
                del path[-1:]
            #
            # Add the cursor to this object, and insert it into the path
            # store.
            #
            # Set the working paths and create a new Cursor object.
            path.append(1)
            cursor = self.game_add_cursor()
            #
            # Put the cursor in the path store.
            self._restInterface.rest_put(cursor, self._cursorPath)
            #
            # Set all its parameters except visibility in a big patch. Then
            # set visibility in a single put, so that it gets set last.
            self._restInterface.rest_patch({
                    'subjectPath': tuple(path),
                    'origin': (0, 0, 0), 'offset':1.0, 'length':4.0,
                    'radius': 2.0, 'rotation': 0.0,
                    'selfPath': self._cursorPath
                }, self._cursorPath)
            self._cursorPath.append('visible')
            self._restInterface.rest_put(True, self._cursorPath)
            #
            # Revert the working paths.
            del path[-1:]
            del self._cursorPath[-1:]
            #
            # Set what will be the camera starting position as an offset from
            # the cursor.
            self._cameraStartPosition = tuple(
                sum(zip_) for zip_ in zip(cursor.point
                                          , self._cameraStartOffset))
            #
            # Add the floor object, which is handy to stop objects dropping out
            # of sight due to gravity.
            object_ = self._GameObject(self.game_add_object('floor'))
            path[-1] = 'floor'
            self._restInterface.rest_put(object_, path)
            # Note that path now points to floor.
            #
            # Create the camera object, based on the default camera.
            object_ = self.Camera(self.gameScene.active_camera)
            object_.restInterface = self._restInterface
            path[-1] = 'camera'
            self._restInterface.rest_put(object_, path)
            # By the way, if any of the properties set in the following
            # rest_patch haven't been set in the __init__ then it somehow stops
            # being a camera and becomes a dictionary. 
            self._restInterface.rest_patch(
                {
                    'animationPath': ('animations', 'cameraTracking'),
                    'selfPath': path[:],
                    'trackSpeed': self._cameraAngular,
                    'worldPosition': self._cameraStartPosition,
                    'rotation': self._cameraStartOrientation
                }, path)
            path.append('subjectPath')
            self._restInterface.rest_put(self._cursorPath, path)
            # Note that path now points to the camera subjectPath.
        
    # Override.
    # Only point of the override is to force the method resolution order to
    # start with the http application.
    def game_terminate(self):
        super().game_terminate()

    # Override.
    def game_tick_run(self):
        super().game_tick_run()
        self.mainLock.acquire()
        try:
            #
            # Bodge the camera.
            camera = self._restInterface.rest_get(('root', 'camera'))
            camera.tick(self.tickPerf)
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
        elif keyString == "\t":
            self.move_cursor()
        else:
            return inSuper
        
        return True
    
    def stop_camera(self, dimensions=range(5)):
        for dimension in dimensions:
            animationPath = self._animation_path(dimension)
            self._restInterface.rest_put(None, animationPath)
    
    def _animation_path(self, dimension):
        return ['animations', 'camera', dimension]
    
    def move_camera(self, dimension, direction):
        #
        # Convenience variable.
        restInterface = self._restInterface
        #
        # Path to the camera's position in the specified dimension.
        valuePath = self.gameObjectPath[:-1]
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
        # There is no subjectPath because the camera doesn't get physics.
        animation = {'valuePath': valuePath}
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
        restInterface.rest_put(animation, animationPath)
        #
        # Set the start time, which has the following side effects:
        # -   Retrieves the start value.
        # -   Clears the complete state.
        animationPath.append('startTime')
        restInterface.rest_put(self.tickPerf, animationPath)
    
    def move_cursor(self):
        self._cursorPath.append('subjectPath')
        subjectPath = list(self._restInterface.rest_get(self._cursorPath))
        subjects = len(self._restInterface.rest_get(subjectPath[:-1]))
        subjectPath[-1] = (subjectPath[-1] + 1) % subjects
        self._restInterface.rest_put(subjectPath, self._cursorPath)
        del self._cursorPath[-1:]
        # ToDo maybe: Force the camera to update to point to the new location.
        # It doesn't seem necessary, because the camera checks whether its
        # subject has moved every tick anyway.
