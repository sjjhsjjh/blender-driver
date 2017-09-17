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
from path_store.blender_game_engine import get_game_object_subclass, Cursor
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

    def _add_visualiser(self):
        return self._GameObject(self.game_add_object('visualiser'))

    # Overriden.
    def game_initialise(self):
        # Base class initialise will have instantiated the restInterface and
        # added the game objects.
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
                empty = self.game_add_object('empty')
                object_.tether = empty
                #
                # Add the cursor to this object, and insert it into the path
                # store.
                #
                # Set the cursor working path and create a new Cursor object.
                cursorPath.append(index)
                cursor = Cursor()
                #
                # Give the cursor the means to add visualiser objects.
                cursor.add_visualiser = self._add_visualiser
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
            #
            # Add the floor object, which is handy to stop objects dropping out
            # of sight due to gravity.
            object_ = self._GameObject(self.game_add_object('floor'))
            path[-1] = 'floor'
            self._restInterface.rest_put(object_, path)
            # Note that path now points to floor.
            #
            log(INFO, "Objects, cursors, floor: {}"
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
                        otherData['number'] == userData['number']
                        and not animation.complete
                    ):
                        still = True
                #
                # If there are no other animations: restore physics to the
                # object and reset its rotation overrides.
                if not still:
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
        finally:
            self.mainLock.release()

    # No override for game_keyboard.
    
    # Override.
    def _prepare_animation(self, animation):
        objectPath = animation['userData']['path']
        object_ = self._restInterface.rest_get(objectPath)
        log(INFO, "Suspending {}.", objectPath)
        object_.suspendDynamics(True)
        # ToDo: Near here, copy all the rotation values into the setList in case
        # one of them is being animated. Or maybe do that in the Rotation class.
        #
        # This could maybe be moved to the GameObject class and included in a
        # setter for suspendPhysics.
