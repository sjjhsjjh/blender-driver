#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

This code illustrates:

-   Basic use of the Blender Game Engine (BGE) KX_GameObject interface, to
    change the size of a game object.
-   Termination of BGE when any key is pressed.
-   Spawning a single thread at the start of BGE execution. The thread is join'd
    before terminating BGE.
-   Use of a thread lock to indicate termination is due.

This application doesn't override game_tick, which is then a pass in the base
class. It doesn't switch off the tick controller. If it does then the thread
doesn't seem to get scheduled at any time after the game_initialise has
finished.

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
# Blender Game Engine KX_GameObject
# Import isn't needed because this class gets an object that has been created
# elsewhere.
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
#
# Blender Game Engine maths utilities, which can only be imported if running
# from within the Blender Game Engine.
# Import isn't needed because this class gets a Vector from the bpy layer.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# from mathutils import Vector
# 
# Main Blender Python interface, which is used to get the size of a mesh.
# Import isn't needed because the base class keeps a reference to the interface
# object.
# import bpy
#
# Local imports.
#
# Blender Driver application with threads and locks.
import blender_driver.application.thread

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.thread.Application):
    def _name(self, subroutine):
        return " ".join((__package__, __name__, str(subroutine)))
    
    def pulse_object_scale(self):
        """Pulse the scale of a game object for ever. Run as a thread."""
        minScale = self.arguments.minScale
        changeScale = self.arguments.changeScale
        increments = self.arguments.increments
        objectName = self.arguments.pulsar
        #
        # Get the underlying dimensions of the Blender mesh, from the data
        # layer. It's a mathutils.Vector instance.
        dimensions = self.bpy.data.objects[objectName].dimensions
        #
        # Get a reference to the game object.
        object_ = self.gameScene.objects[objectName]
        while True:
            for cycle in range(3):
                for scale in range(increments):
                    if self.terminating():
                        print(self._name('pulse object scale'), "Stop.")
                        return
                    if self.arguments.verbose:
                        print(self._name('pulse object scale locking ...'))
                    self.tickLock.acquire(True)
                    scales = (
                        minScale
                        + (changeScale * (scale + 1) / increments)
                        , minScale
                        + (changeScale * (increments - scale) / increments)
                        , minScale)
                    worldScale = dimensions.copy()
                    for index in range(3):
                        worldScale[index] *= scales[(cycle+index)%3]
                    object_.worldScale = worldScale
                    self.tickLock.release()
                    if self.arguments.verbose:
                        print(self._name('pulse object scale released.'))
                    if self.arguments.sleep is not None:
                        time.sleep(self.arguments.sleep)
        
    def game_initialise_run(self):
        print(self._name('game_initialise_run'), self.arguments)
        print("Settings", self.settings)
        print("Game scene objects", self.gameScene.objects)
        threading.Thread(target=self.pulse_object_scale).start()
        
    def game_keyboard(self, keyEvents):
        print(self._name('game_keyboard'), "Terminating.")
        self.game_terminate()
        
    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--increments', type=int, default=40,
            help="Number of increments. Default: 40.")
        parser.add_argument(
            '--changeScale', type=float, default=2.0,
            help="Change of scale. Default: 2.0.")
        parser.add_argument(
            '--minScale', type=float, default=0.5,
            help="Minimum scale. Default: 0.5.")
        parser.add_argument(
            '--pulsar', default="Cube",
            help="Name of the object to pulse.")
        parser.add_argument(
            '--sleep', type=float,
            help=
            "Sleep after each increment, for a floating point number of"
            " seconds. Default is not to sleep.")
        parser.add_argument(
            '--verbose', action='store_true', help=
            'Verbose logging of lock acquisition and release.')
        return parser
