#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
#
# This module uses the Thread class.
# https://docs.python.org/3.4/library/threading.html#thread-objects
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
# Blender Driver application with threads and locks.
from . import pulsar

from path_store.blender_game_engine import GameObject

from path_store.rest import RestInterface

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(pulsar.Application):
    
    templates = {
        'pulsar': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'location': (0, 0, -1)}
    }

    def data_initialise(self):
        super().data_initialise()
        self.bpyutils.delete_except(self.dontDeletes)

    # Overridden.
    def pulse_object_scale(self):
        """Pulse the scale of three game objects for ever. Run as a thread."""
        objectName = "pulsar"
        #
        # Get the underlying dimensions of the Blender mesh, from the data
        # layer. It's a mathutils.Vector instance.
        dimensions = tuple(self.bpy.data.objects[objectName].dimensions)
        
        restInterface = RestInterface()
        
        displace = (
            (self.arguments.minScale + self.arguments.changeScale)
            * dimensions[1])
        
        #
        # Insert game objects.
        for index in range(3):
            object_ = GameObject(self.game_add_object(objectName))
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

        nativeObject = restInterface.rest_get(2)
        get_scales = self._get_scales()
        while True:
            log(DEBUG, "locking ...")
            self.mainLock.acquire()
            try:
                log(DEBUG, "locked.")
                if self.terminating():
                    log(DEBUG, "Stop.")
                    get_scales.close()
                    return
                scales = next(get_scales)
                worldScale = list(dimensions)
                for index, value in enumerate(scales):
                    worldScale[index] *= value
                    restInterface.rest_put(worldScale[index]
                                           , (1, 'worldScale', index))

                restInterface.rest_put(worldScale, (0, 'worldScale'))
                nativeObject.worldScale = worldScale
            finally:
                log(DEBUG, "releasing.")
                self.mainLock.release()

            if self.arguments.sleep is not None:
                time.sleep(self.arguments.sleep)
