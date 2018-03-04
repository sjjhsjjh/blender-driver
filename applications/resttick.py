#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

This code illustrates:

-   Basic use of the Blender Game Engine (BGE) KX_GameObject interface, to
    change the size of a game object.
-   Termination of BGE when any key is pressed.
-   Spawning a single thread at the start of BGE execution. The thread is
    joined before terminating BGE.
-   Use of a thread lock to indicate termination is due.

This application doesn't override the Blender Driver game_tick, which is then a
pass in the base class.

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

from math import fmod

#
# This module uses the Thread class.
# https://docs.python.org/3.5/library/threading.html#thread-objects
import threading
#
# Module for sleep.
# https://docs.python.org/3.5/library/time.html
import time
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
#
# Local imports.
#
# Blender Driver application with a pulsating object.
from . import pulsar
#
# Wrapper for Blender game object that is easy to make RESTful.
from path_store.blender_game_engine import get_game_object_subclass
#
# RESTful interface base class.
from path_store.rest import RestInterface

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

# ToDo:
# -   Use tickPerf to make the animation based on elapsed time.
# -   Also do that in marker ... and pulsar.
# -   Might mean moving the scaling into the tick, instead of having it in the
#     thread. Pulsar doesn't have a tick though.
# -   Spin through iterations of get_scale based on a speed parameter.
#     Controls are like: change of scale to be spread over X time.
#     Maybe have a subroutine like get_scales_at(referenceTime) That does:
#     -   Modulo-like calculation to determine which dimension is inc'ing and
#         dec'ing.
#     -   Division to get to the values.

class Application(pulsar.Application):
    
    templates = {
        'pulsar': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'location': (0, 0, -1)}
    }

    # Overriden.
    def game_initialise(self):
        self._restInterface = RestInterface()
        self._objectName = "pulsar"
        super().game_initialise()

    # Overridden.
    def pulse_object_scale(self):
        """Pulse the scale of three game objects for ever. Run as a thread."""
        self.mainLock.acquire()
        try:
            self._GameObject = get_game_object_subclass(self.bge)

            objectName = self._objectName
            #
            # Get the underlying dimensions of the Blender mesh, from the data
            # layer. It's a mathutils.Vector instance.
            dimensions = tuple(self.bpy.data.objects[objectName].dimensions)
            
            restInterface = self._restInterface
            
            displace = (
                (self.arguments.minScale + self.arguments.changeScale)
                * dimensions[1])
            
            #
            # Insert game objects.
            for index in range(3):
                object_ = self._GameObject(self.game_add_object(objectName))
                restInterface.rest_put(object_, index)
            #
            # Move game objects.
            #
            # First moves up the y axis.
            value = restInterface.rest_get((0, 'worldPosition', 1))
            restInterface.rest_put(value + displace, (0, 'worldPosition', 1))
            #
            # Second moves down the y axis.
            value = restInterface.rest_get((1, 'worldPosition', 1))
            restInterface.rest_put(value - displace, (1, 'worldPosition', 1))
            #
            # Third moves in the x and z axes.
            value = restInterface.rest_get((2, 'worldPosition'))
            value[0] += displace
            value[2] += self.arguments.minScale * 2
            # There is no rest_put because the value returned by the rest_get is a
            # reference, because it's an object maybe. These accesses go via the
            # HostedProperty _Holder __setitem__ accessor.
    
            # The game objects are manipulated through different programming
            # interfaces:
            # -   Object 0 by rest_put of a worldScale array.
            # -   Object 1 by rest_put of each element of the worldScale array.
            # -   Object 2 by native setting of the worldScale property.
    
            # nativeObject = restInterface.rest_get(2)
            get_scales = self._get_scales()
        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        self.mainLock.acquire()
        try:
            nativeObject = self._restInterface.rest_get(2)
            objectName = self._objectName
    
            minScale = self.arguments.minScale
            changeScale = self.arguments.changeScale
    
            worldScale = list(self.bpy.data.objects[objectName].dimensions)
    
            cycleTime = self.arguments.cycleTime
            subcycleTime = cycleTime / 3.0
            moduloTime = fmod(self.tickPerf, cycleTime)
            dimension = int(moduloTime / subcycleTime)
            moduloTime = fmod(moduloTime, subcycleTime) / subcycleTime
            
            worldScale[dimension] *= minScale
            worldScale[(dimension + 1) % 3] *= (
                minScale + (changeScale * (1.0 - moduloTime)))
            worldScale[(dimension + 2) % 3] *= (
                minScale + (changeScale * moduloTime))
            
            self._restInterface.rest_put(worldScale, (0, 'worldScale'))
            for index, value in enumerate(worldScale):
                self._restInterface.rest_put(value, (1, 'worldScale', index))
            nativeObject.worldScale = worldScale
    
            # print(self.tickPerf, dimension, moduloTime, worldScale)
        finally:
            self.mainLock.release()

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--cycleTime', type=float, default=6.0,
            help="Length of cycle in seconds. Default: 6.0.")
        return parser

