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
# Blender Driver application with background banner.
from . import demonstration
#
# Animation base class, for demonstration.
from path_store.animation import Animation
#
# Wrapper for Blender game object that is easy to make RESTful.
from path_store.blender_game_engine import get_game_object_subclass
#
# RESTful interface base class and Animation subclass for pathstore.
from path_store.rest import RestInterface, PathAnimation

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(demonstration.Application):
    
    templates = {
        'cube': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'location': (0, 0, 0)}
    }

    # Override.
    _instructions = "Ctrl-Q to terminate.\nspace, plus, minus, or 0 to animate."

    def data_initialise(self):
        super().data_initialise()
        self.bpyutils.delete_except(self.dontDeletes)

    # Overriden.
    def game_initialise(self):
        super().game_initialise()
        self._restInterface = RestInterface()
        self._animations = [None, None, None]
        self._objectName = "cube"
        self.mainLock.acquire()
        try:
            self._GameObject = get_game_object_subclass(self.bge)

            objectName = self._objectName

            #
            # Insert game objects.
            objectCount = 3
            for index in range(objectCount):
                object_ = self._GameObject(self.game_add_object(objectName))
                self._restInterface.rest_put(object_, index)
                #
                # Displace along the y axis.
                axisPath = (index, 'worldPosition', 1)
                value = self._restInterface.rest_get(axisPath)
                displace = 3.0 * (float(index) - (float(objectCount) / 2.0))
                self._restInterface.rest_put(value + displace, axisPath)
            
        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        self.mainLock.acquire()
        try:
            deletions = False
            for index, animation in enumerate(self._animations):
                if animation is None:
                    continue
                if isinstance(animation, PathAnimation):
                    animation.set(self.tickPerf)
                else:
                    animation.nowTime = self.tickPerf
                    value = animation.get_value()
                    log(DEBUG, "{} {}", self.tickPerf, value)
                    self._restInterface.rest_put(value, (2, 'worldPosition', 2))
                if animation.complete:
                    self._animations[index] = None
                    deletions = True
            
            if deletions:
                print("Animations:{}.".format(list(
                    None if _ is None else "Some" for _ in self._animations)))

        finally:
            self.mainLock.release()

    
    def game_keyboard(self, keyEvents):
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        if keyString == "q" and ctrl:
            log(DEBUG, "Terminating.")
            self.game_terminate()
            return

        objectNumber = 0
        if ctrl:
            objectNumber = 2

        try:
            if keyString == " ":
                self.animate(objectNumber, None)
            elif keyString == "+":
                self.animate(objectNumber, 1)
            elif keyString == "-":
                self.animate(objectNumber, -1)
            elif keyString == "0":
                self.animate(objectNumber, 0)
            else:
                raise Exception("No command for keypress.")
            return
        except Exception as exception:
            log(INFO, '{} {} "{}" ctrl:{} alt:{} {} {}'
                , exception, keyEvents, keyString, ctrl, alt
                , self.bge.events.BACKSPACEKEY, self.bge.events.TABKEY)
        
    def animate(self, objectNumber, direction=None):
        self.mainLock.acquire()
        try:
            if objectNumber == 2:
                animation = Animation()
    
                animation.startValue = self._restInterface.rest_get((
                    objectNumber, 'worldPosition', 2))
                animation.startTime = self.tickPerf
    
            else:
                animation = PathAnimation()
                animation.store = self._restInterface.principal
                animation.path = (objectNumber, 'worldPosition', 2)
                animation.start(self.tickPerf)
                
            animation.speed = self.arguments.speed

            if direction is None:
                target = self.arguments.target
                if animation.startValue > 0:
                    target *= -1
                animation.targetValue = animation.startValue + target
            elif direction == 0:
                animation.targetValue = 0.0
            else:
                animation.targetValue = None
                if direction < 0:
                    animation.speed *= -1
            
            self._animations[objectNumber] = animation

        finally:
            self.mainLock.release()
        
    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--speed', type=float, default=2.0, help=
            "Speed of change, in Blender units per second. Default: 2.0.")
        parser.add_argument(
            '--target', type=float, default=5.0,
            help="Distance moved in each animation. Default: 5.0.")
        return parser
