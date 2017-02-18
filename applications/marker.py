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
# Blender Game Engine maths utilities, which can only be imported if running
# from within the Blender Game Engine.
# Import isn't needed because this class gets a Vector from the bpy layer.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# from mathutils import Vector
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
                   ,'location': (0, 0, -1)
                   # , 'dimensions': (0.1, 1, 2)
                   },
        'marker': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                   ,'location': (0, 0, 2)
                   , 'dimensions': (0.5, 0.5, 0.5)
                   },
        'counter': {'subtype':'Text', 'physicsType':'NO_COLLISION'
                    ,'location': (3, 5, 3)
                    },
        'clock': {'subtype':'Text', 'physicsType':'NO_COLLISION'
                    ,'location': (3, -5, 3)
                    }
    }
    
    # Override.
    def _name(self, subroutine):
        return " ".join((__package__, __name__, str(subroutine)))

    def data_initialise(self):
        self.bpyutils.delete_except(
            [self.dataGateway, 'Lamp'] + list(self.templates.keys()) )
    
    def add_object(self, objectName):
        object_ = self.gameScene.addObject(objectName, self.gameGateway)
        object_.worldPosition = self.bpy.data.objects[objectName].location
        if self.arguments.verbose:
            print(self._name(objectName),
                  self.bpy.data.objects[objectName].dimensions)
        return object_

    # Override.
    def game_initialise(self):
        #
        # Set up this application class's pulsar, which is different to the base
        # class pulsar.
        self._objectPulsar = self.add_object("pulsar")
        self.arguments.pulsar = "pulsar"
        #
        # Do base class initialisation.
        super().game_initialise()
        self.mainLock.acquire()
        #
        # Set up what this application uses.
        #
        # Marker object.
        self._objectMarker = self.add_object("marker")
        #
        # Counter object, which is a Blender Text.
        self._objectCounter = self.add_object("counter")
        self._objectCounter['Text'] = ""
        self._objectCounterNumber = 0
        #
        # Clock object, which is also a Blender Text.
        self._objectClock = self.add_object("clock")
        self._objectClock['Text'] = "clock"
        #
        # Spawn a thread on which to cycle the counter.
        self.mainLock.release()
        threading.Thread(target=self.cycle_count_run).start()
        
    def cycle_count_run(self):
        """Cycle a counter for ever. Run as a thread."""
        counterReset = 1000
        while True:
            if self.terminating():
                if self.arguments.verbose:
                    print(self._name('cycle count scale'), "Stop.")
                return
            if self.arguments.verbose:
                print(self._name('cycle count locking ...'))
            self.mainLock.acquire(True)
            self._objectCounter['Text'] = str(self._objectCounterNumber)
            self._objectCounterNumber = (
                (self._objectCounterNumber + 1) % counterReset)
            self.mainLock.release()
            if self.arguments.verbose:
                print(self._name('cycle count released.'))
            if self.arguments.sleep is not None:
                time.sleep(self.arguments.sleep)
        
    def game_tick_run(self):
        #
        # Formally, run the base class tick. Actually, it's a pass.
        super().game_tick_run()
        #
        # Move the marker to one vertex of the pulsar.
        self.mainLock.acquire(True)
        worldPosition = self._objectMarker.worldPosition.copy()
        for index in range(len(worldPosition)):
            worldPosition[index] = (
                self._objectPulsar.worldPosition[index]
                + self._objectPulsar.worldScale[index])
        self._objectMarker.worldPosition = worldPosition
        #
        # Update the time displayed in the clock.
        self._objectClock['Text'] = time.strftime("%H:%M:%S")
        self.mainLock.release()

    def ok_to_skip_tick(self):
        print(self._name('tick_skipped'), self.skippedTicks)
        return False
