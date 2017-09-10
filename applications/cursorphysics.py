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

    def _add_visualiser(self):
        return self._GameObject(self.game_add_object('visualiser'))

    # Overriden.
    def game_initialise(self):
        super().game_initialise()



        
        self._objectName = "cube"



        self.mainLock.acquire()
        try:
            #
            # Add tether to game objects.
            for index in range(self.objectCount):


                empty = self.game_add_object('empty')
                object_.tether = empty

                cursor = Cursor()
                cursor.add_visualiser = self._add_visualiser
                cursor.restInterface = self._restInterface
                cursor.subjectPath = ('root', index)
                cursor.offset = 3.0
                cursor.length = 4.0
                cursor.radius = 2.0
                cursor.rotation = radians(90)
                cursor.visible = True
                
            self._floor = self._GameObject(self.game_add_object('floor'))

        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        super().game_tick_run()
        self.mainLock.acquire()
        try:



            try:
                animations = self._restInterface.rest_get('animations')
            except KeyError:
                animations = tuple()
            for index, animation in enumerate(animations):
                if animation is not None and animation.complete:
                    object_ = self._restInterface.rest_get(animation.path[:-2])
                    object_.restoreDynamics()
                    self._restInterface.rest_put(None, ('animations', index))
            
        finally:
            self.mainLock.release()

    # No override for game_keyboard.
        
            # objectPath = ('root', objectNumber)
            # object_ = restInterface.rest_get(objectPath)
            # object_.suspendDynamics()
