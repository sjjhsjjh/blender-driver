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
# Blender Game Engine KX_GameObject
# Import isn't needed because this class gets an object that has been created
# elsewhere.
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
#
# Main Blender Python interface.
# Import isn't needed because the base class keeps a reference to the interface
# object.
# import bpy
#
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
            self._objectMarker = self.add_object('marker')
            self._objectAsterisk = self.game_add_text('asterisk')
            self._objectPlus = self.game_add_text('plus')
        finally:
            self.verbosely(__name__, 'game_initialise', "releasing.")
            self.mainLock.release()

    def game_tick_run(self):
        #
        # Formally, run the base class tick. Actually, it's a pass.
        super().game_tick_run()
        self.mainLock.acquire(True)
        try:
            #
            # Move the marker to one vertex of the pulsar.
            worldPosition = self._objectMarker.worldPosition.copy()
            for index in range(len(worldPosition)):
                worldPosition[index] = (
                    self._objectPulsar.worldPosition[index]
                    + self._objectPulsar.worldScale[index])
            self._objectMarker.worldPosition = worldPosition.copy()
            #
            # Move the plus to the middle of one face of the marker, offset
            # by a little bit so it doesn't flicker.
            worldPosition[0] += self._objectMarker.worldScale[0] + 0.01
            #
            # Fudge the text positioning.
            worldPosition[1] -= 0.15
            worldPosition[2] -= 0.15
            self._objectPlus.worldPosition = worldPosition.copy()
            #
            # Move the asterisk to the middle of one face of the pulsar, offset
            # by a little bit so it doesn't flicker.
            worldPosition = self._objectPulsar.worldPosition.copy()
            worldPosition[0] += self._objectPulsar.worldScale[0] + 0.01
            #
            # Fudge the text positioning.
            worldPosition[1] -= 0.3
            worldPosition[2] -= 1.0
            self._objectAsterisk.worldPosition = worldPosition.copy()
        finally:
            self.mainLock.release()
