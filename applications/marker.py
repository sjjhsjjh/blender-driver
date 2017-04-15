#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

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
# Module for degrees to radians conversion.
# https://docs.python.org/3.5/library/math.html#math.radians
from math import radians
#
# Module for random number generation.
# https://docs.python.org/3.5/library/random.html
from random import randrange
#
# Module for logging current time and sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# This module uses Thread and Lock classes.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Third party modules, in alphabetic order.
#
# Blender library imports, in alphabetic order.
#
# These modules can only be imported if running from within Blender.
try:
    #
    # Blender Game Engine KX_GameObject
    # Import isn't needed because this class gets an object that has been created
    # elsewhere.
    # https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
    #
    # Blender Game Engine maths utilities, which can only be imported if running
    # from within the Blender Game Engine.
    # http://www.blender.org/api/blender_python_api_current/mathutils.html
    from mathutils import Vector
    #
    # Main Blender Python interface.
    # Import isn't needed because the base class keeps a reference to the interface
    # object.
    # import bpy
except ImportError as error:
    print(__doc__)
    print(error)
# Local imports.
#
# Application demonstration module, which is used as a base.
from . import pulsar

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(pulsar.Application):

    templates = {
        'pulsar': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'location': (0, 0, -1)},
        'marker': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   , 'scale': (0.5, 0.5, 0.5)},
        'asterisk': {'text':"*", 'physicsType':'NO_COLLISION'
                     , 'scale': (2, 2, 2)},
        'plus': {'text':"+", 'physicsType':'NO_COLLISION'
                 , 'scale': (0.5, 0.5, 0.5)},
        'minus': {'text':"-", 'physicsType':'NO_COLLISION'
                 , 'scale': (0.5, 0.5, 0.5)}
    }
    
    def data_initialise(self):
        super().data_initialise()
        self.bpyutils.delete_except(
            [self.dataGateway, 'Lamp', self._bannerName]
            + list(self.templates.keys()) )
    
    def add_object(self, objectName):
        object_ = self.gameScene.addObject(objectName, self.gameGateway)
        object_.worldPosition = self.bpy.data.objects[objectName].location
        self.verbosely(__name__, 'add_object'
                       , objectName
                       , self.bpy.data.objects[objectName].dimensions)
        return object_

    # Override.
    def game_initialise(self):
        #
        # Set up this application class's pulsar, which is different to the base
        # class pulsar. The base class doesn't need to add the pulsar, because
        # it doesn't delete it in its data_initialise, in turn because it
        # doesn't have a templates collection.
        self._objectPulsar = self.add_object("pulsar")
        self.arguments.pulsar = "pulsar"
        #
        # Do base class initialisation.
        super().game_initialise()
        self.verbosely(__name__, 'game_initialise', "locking...")
        self.mainLock.acquire()
        try:
            self.verbosely(__name__, 'game_initialise', "locked.")
            
            self._objectMarker1 = self.add_object('marker')
            self._objectMarker2 = self.add_object('marker')
            self._objectAsterisk = self.game_add_text('asterisk')
            self._objectPlus = self.game_add_text('plus')
            self._objectMinus = self.game_add_text('minus')
            
            self._dimension = 2
            self.advance_dimension()
            self._cornerTo = (1,1,1)
            self.advance_corner()
            self._perfFrom = 0.0
        finally:
            self.verbosely(__name__, 'game_initialise', "releasing.")
            self.mainLock.release()
            
    def advance_corner(self):
        self._cornerFrom = self._cornerTo
        cornerTo = list(self._cornerFrom)
        cornerTo[self._dimension] *= -1
        self._cornerTo = tuple(cornerTo)
    
    def advance_dimension(self):
        if self.arguments.circuit:
            self._dimension = 2 if self._dimension == 1 else 1
        else:
            self._dimension = randrange(len(self._cornerTo))
    
    def position_text(self, object_, faceText, fudgeY=-0.15, fudgeZ=-0.15):
        worldPosition = object_.worldPosition.copy()
        #
        # Move the face text to the middle of one face of the object, offset by
        # a little bit so it doesn't flicker.
        worldPosition[0] += object_.worldScale[0] + 0.01
        #
        # Fudge the text positioning.
        worldPosition[1] += fudgeY
        worldPosition[2] += fudgeZ
        faceText.worldPosition = worldPosition.copy()
    
    def get_corner(self, object_, signs):
        return_ = object_.worldPosition.copy()
        for index in range(len(return_)):
            return_[index] += signs[index] * object_.worldScale[index]
        return return_

    def game_tick_run(self):
        #
        # Formally, run the base class tick. Actually, it's a pass.
        super().game_tick_run()
        self.mainLock.acquire(True)
        try:
            #
            # Move the marker to one vertex of the pulsar.
            self._objectMarker1.worldPosition = self.get_corner(
                self._objectPulsar, self._cornerFrom)
            #
            # Position the plus on the marker.
            self.position_text(self._objectMarker1, self._objectPlus)
            #
            # Position the lead marker.
            fromVector = self.get_corner(self._objectPulsar, self._cornerFrom)
            fromScalar = fromVector[self._dimension]
            toVector = self.get_corner(self._objectPulsar, self._cornerTo)
            toScalar = toVector[self._dimension]
            direction = 1 if fromScalar < toScalar else -1
            nowScalar = fromScalar + (
                self.arguments.speed
                * (self._perfTick - self._perfFrom)
                * direction)
            
            fromVector[self._dimension] = nowScalar
            if ((fromScalar < toScalar and nowScalar >= toScalar)
                or (fromScalar > toScalar and nowScalar <= toScalar)
                ):
                fromVector = toVector
                self.advance_dimension()
                self.advance_corner()
                self._perfFrom = self._perfTick
            self._objectMarker2.worldPosition = fromVector
            #
            # Position the minus on the lead marker.
            self.position_text(self._objectMarker2, self._objectMinus)
            #
            # Position asterisk on the pulsar.
            self.position_text(self._objectPulsar
                               , self._objectAsterisk, -0.3, -1.0)
        finally:
            self.mainLock.release()

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--speed', type=float, default=3.0, help=
            "Speed of marker in Blender units (BU) per second. Default: 3.0.")
        parser.add_argument(
            '--circuit', action='store_true', help=
            "Make the marker do a circuit of the visible face of the pulsar."
            " Default is for the marker to pick a random direction when it"
            " reaches a corner.")
        return parser
