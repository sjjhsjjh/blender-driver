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
        'cube': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'location': (0, 0, 0)}
    }

    # Override.
    _instructions = "\n".join((
        "Ctrl-Q to terminate; space, plus, minus, or 0 to move object 0;"
        , "plus Ctrl to move object 2. Object 1 doesn't move."))

    def data_initialise(self):
        super().data_initialise()
        self.bpyutils.delete_except(self.dontDeletes)

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
            objectCount = 3
            for index in range(objectCount):
                object_ = self._GameObject(self.game_add_object(objectName))
                self._restInterface.rest_put(object_, ('root', index))
                #
                # Displace along the y axis.
                axisPath = ('root', index, 'worldPosition', 1)
                value = self._restInterface.rest_get(axisPath)
                displace = 3.0 * (float(index) - (float(objectCount) / 2.0))
                self._restInterface.rest_put(value + displace, axisPath)
            
            # worldOrientation = self._restInterface.rest_get((
            #     'root', 1, 'worldOrientation'))
            # quaternion = worldOrientation.to_quaternion()
            # print(worldOrientation, quaternion.axis, quaternion.angle)
            # rotation = Matrix.Rotation(radians(30), 4, 'Z')
            # quaternion.rotate(rotation)
            # print(worldOrientation, quaternion)
            # self._restInterface.rest_put(
            #     quaternion, ('root', 1, 'worldOrientation'))
            # 
            # worldOrientation = self._restInterface.rest_get((
            #     'root', 1, 'worldOrientation'))
            # quaternion = worldOrientation.to_quaternion()
            # print('After', worldOrientation, quaternion.axis, quaternion.angle)
            
            # radians_ = self._restInterface.rest_get(('root', 1, 'rotation'))
            # degrees_ = tuple(degrees(_) for _ in radians_)
            # orientation = self._restInterface.rest_get(
            #     ('root', 1, 'worldOrientation'))
            # print(orientation, radians_, degrees_)
            # 
            # self._restInterface.rest_put(
            #     (0, 0, radians(45)), ('root', 1, 'rotation'))
            # radians_ = self._restInterface.rest_get(('root', 1, 'rotation', 2))
            # print(radians_, degrees(radians_))

            # self._restInterface.rest_put(
            #     radians(60), ('root', 1, 'rotation', 2))
            # radians_ = self._restInterface.rest_get(('root', 1, 'rotation', 2))
            # print(radians_, degrees(radians_))
            # radians_ = self._restInterface.rest_get(('root', 1, 'rotation'))
            # degrees_ = tuple(degrees(_) for _ in radians_)
            # orientation = self._restInterface.rest_get(
            #     ('root', 1, 'worldOrientation'))
            # print(orientation, radians_, degrees_)
            
            valuePath = ('root', 1, 'rotation', 2)
            animation = {
                'path': valuePath,
                'speed': radians(5),
                'targetValue': radians(60)}
            animationPath = ['animations', 1]
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

            
        finally:
            self.mainLock.release()

    # Override.
    def game_tick_run(self):
        self.mainLock.acquire()
        try:
            # Set the top-level nowTime shortcut, which sets it in all the
            # current animations, which makes them animate in the scene.
            self._restInterface.nowTime = self.tickPerf
        finally:
            self.mainLock.release()

    def game_keyboard(self, keyEvents):
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        if keyString == "q" and ctrl:
            log(DEBUG, "Terminating.")
            self.game_terminate()
            return
        #
        # If Ctrl is held down, animate object 2, otherwise animate object 0.
        # Object 1 never moves.
        objectNumber = 0
        if ctrl:
            objectNumber = 2

        if keyString == " ":
            self.animate(objectNumber, None)
        elif keyString == "+":
            self.animate(objectNumber, 1)
        elif keyString == "-":
            self.animate(objectNumber, -1)
        elif keyString == "0":
            self.animate(objectNumber, 0)
        elif keyString == "":
            pass
        else:
            log(INFO, 'No command for keypress. {} "{}" ctrl:{} alt:{}'
                , keyEvents, keyString, ctrl, alt)
        
    def animate(self, objectNumber, direction):
        self.mainLock.acquire()
        try:
            #
            # Convenience variable.
            restInterface = self._restInterface
            #
            # Path to the object's Z value.
            valuePath = ('root', objectNumber, 'worldPosition', 2)
            #
            # Assemble the animation in a dictionary, starting with these.
            animation = {'path': valuePath, 'speed': self.arguments.speed}
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
            # There is up to one animation per object.
            animationPath = ['animations', objectNumber]
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
