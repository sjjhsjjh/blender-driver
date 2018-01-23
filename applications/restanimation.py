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
from math import radians
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
# Local imports.
#
# Blender Driver application with background banner.
from . import demonstration
#
# Wrapper for Blender game object that is easy to make RESTful.
from path_store.blender_game_engine import get_game_object_subclass
#
# RESTful interface base class and Animation subclass for pathstore.
from path_store.rest import AnimatedRestInterface

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(demonstration.Application):
    
    templates = {
        'cube': {
            'subtype':'Cube', 'physicsType':'NO_COLLISION',
            'location': (0, 0, 0)}
    }

    # Override.
    _instructions = (
        "Ctrl-Q to terminate; space, plus, minus, or 0 to move left object;"
        "\n< or > to rotate it;"
        "\nplus Ctrl to move right object. Middle object doesn't move.")

    _objectCount = 3
    _objectRootPath = ('root',)

    # Overriden.
    def game_initialise(self):
        super().game_initialise()
        self._restInterface = AnimatedRestInterface()
        
        self._objectName = "cube"
        self.mainLock.acquire()
        try:
            self._GameObject = get_game_object_subclass(self.bge)
            objectName = self._objectName
            #
            # Insert game objects.
            #
            # Working path.
            path = list(self._objectRootPath)
            for index in range(self._objectCount):
                object_ = self._GameObject(self.game_add_object(objectName))
                path.append(index)
                self._restInterface.rest_put(object_, path)
                #
                # Displace along the y axis.
                path.extend(('worldPosition', 1))
                value = self._restInterface.rest_get(path)
                displace = (
                    6.0 * (float(index) - (float(self._objectCount) / 2.0)))
                self._restInterface.rest_put(value + displace, path)
                #
                # Revert working path.
                del path[-3:]
        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        self.mainLock.acquire()
        try:
            # Set the top-level nowTime shortcut, which sets it in all the
            # current animations, which makes them animate in the scene.
            completions = self._restInterface.set_now_times(self.tickPerf)
        finally:
            self.mainLock.release()

    def game_keyboard(self, keyEvents):
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        if keyString == "q" and ctrl:
            log(DEBUG, "Terminating.")
            self.game_terminate()
            return

        self.mainLock.acquire()
        try:
            #
            # If Ctrl is held down, animate object 2, otherwise animate object 0.
            # Object 1 never moves.
            objectNumber = 0
            if ctrl:
                objectNumber = 2
            #
            # Do the command, or log a message if the key isn't defined.
            # Ignore a shift key on its own.
            if (
                (not self._keyboard_command(keyString, objectNumber))
                and keyString != ""
            ):
                log(INFO, 'No command for keypress. {} "{}" ctrl:{} alt:{}'
                    , keyEvents, keyString, ctrl, alt)
        finally:
            self.mainLock.release()
        
    def _keyboard_command(self, keyString, objectNumber):
        """Execute the keyboard command for the specified key string, and return
        True, or return False.
        
        Can be overriden, and can be called from the subclass. The mainLock will
        already have been acquired. """
        if keyString == " ":
            self.animate_linear(objectNumber, None)
        elif keyString == "+":
            self.animate_linear(objectNumber, 1)
        elif keyString == "-":
            self.animate_linear(objectNumber, -1)
        elif keyString == "0":
            self.animate_linear(objectNumber, 0)
            self.animate_angular(objectNumber, 0)
            self.animate_size(objectNumber, 0)
        elif keyString == ">":
            self.animate_angular(objectNumber, -1)
        elif keyString == "<":
            self.animate_angular(objectNumber, 1)
        elif keyString == "s":
            self.animate_size(objectNumber, 1)
        elif keyString == "S":
            self.animate_size(objectNumber, -1)
        else:
            return False
        return True
        
    
    def _prepare_animation(self, animation):
        """Override this."""
        pass
        
    def animate_size(self, objectNumber, direction):
        #
        # Convenience variable.
        restInterface = self._restInterface
        #
        # Path to the object's Z size.
        valuePath = list(self._objectRootPath) + [
            objectNumber, 'worldScale', 2]
        #
        # Assemble the animation in a dictionary, starting with these.
        animation = {
            'modulo': 0,
            'path': valuePath,
            'speed': 1.0,
            'userData': {
                'number': objectNumber,
                'path': self._objectRootPath + (objectNumber,)
            }
        }
        #
        # Get the current value.
        value = restInterface.rest_get(valuePath)
        #
        # Set the speed and target value, based on the current value and the
        # direction parameter.
        if direction == 0:
            animation['targetValue'] = 1.0
        else:
            if value > 1.0 or direction > 0:
                animation['targetValue'] = value + (1.0 * direction)
            else:
                animation['targetValue'] = value / 2.0
        log(INFO, 'Value:{} Values:{}',
            value, tuple(restInterface.rest_get(valuePath[:-1])))
        #
        # There is up to one size animation per object.
        animationPath = ['animations', 'size', objectNumber]
        self._prepare_animation(animation)
        #
        # Insert the animation. The point maker will set the store
        # attribute.
        log(INFO, 'Patching {} {}', animationPath, animation)
        restInterface.rest_put(animation, animationPath)
        #
        # Set the start time, which has the following side effects:
        # -   Retrieves the start value.
        # -   Clears the complete state.
        animationPath.append('startTime')
        restInterface.rest_put(self.tickPerf, animationPath)

    def animate_linear(self, objectNumber, direction):
        #
        # Convenience variable.
        restInterface = self._restInterface
        #
        # Path to the object's Z value.
        valuePath = list(self._objectRootPath) + [
            objectNumber, 'worldPosition', 2]
        #
        # Assemble the animation in a dictionary, starting with these.
        animation = {
            'modulo': 0,
            'path': valuePath,
            'speed': self.arguments.speed,
            'userData': {
                'number': objectNumber,
                'path': self._objectRootPath + (objectNumber,)
            }
        }
        #
        # Get the current value.
        value = restInterface.rest_get(valuePath)
        #
        # Set the speed and target value, based on the current value and the
        # direction parameter.
        if direction is None:
            target = self.arguments.target
            if value > 0:
                target *= -1
            animation['targetValue'] = value + target
        elif direction == 0:
            animation['targetValue'] = 0.0
        else:
            animation['targetValue'] = None
            if direction < 0:
                animation['speed'] *= -1
        #
        # There is up to one altitude animation per object.
        animationPath = ['animations', 'position', objectNumber]
        self._prepare_animation(animation)
        #
        # Insert the animation. The point maker will set the store
        # attribute.
        log(INFO, 'Patching {} {}', animationPath, animation)
        restInterface.rest_put(animation, animationPath)
        #
        # Set the start time, which has the following side effects:
        # -   Retrieves the start value.
        # -   Clears the complete state.
        animationPath.append('startTime')
        restInterface.rest_put(self.tickPerf, animationPath)
        
    def animate_angular(self, objectNumber, direction):
        #
        # Convenience variable.
        restInterface = self._restInterface
        #
        # Path to the object's Z rotation.
        valuePath = list(self._objectRootPath) + [
            objectNumber, 'rotation', 2]
        #
        # Assemble the animation in a dictionary, starting with these.
        animation = {
            'modulo': radians(360),
            'path': valuePath,
            'speed': radians(45),
            'userData': {
                'number': objectNumber,
                'path': self._objectRootPath + (objectNumber,)
            }
        }
        #
        # Get the current value, which will be in radians.
        value = restInterface.rest_get(valuePath)
        log(DEBUG, 'Value:{} Values:{}',
            value, restInterface.rest_get(valuePath[:-1]))
        if direction == 0:
            animation['targetValue'] = 0.0
            if value > 0.0:
                animation['speed'] *= -1
        else:
            animation['targetValue'] = value + radians(45 * direction)
            animation['speed'] *= direction
            # animation['targetValue'] = None
        #
        # There is up to one rotation animation per object.
        animationPath = ['animations', 'orientation', objectNumber]
        self._prepare_animation(animation)
        #
        # Insert the animation. The point maker will set the store
        # attribute.
        log(INFO, 'Patching {} {}', animationPath, animation)
        self._restInterface.rest_put(animation, animationPath)
        #
        # Set the start time, which has the following side effects:
        # -   Retrieves the start value.
        # -   Clears the complete state.
        animationPath.append('startTime')
        self._restInterface.rest_put(self.tickPerf, animationPath)
        
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
