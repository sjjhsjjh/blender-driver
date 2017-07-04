#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

Abstract base class for demonstration applications.

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
import logging
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Third party modules, in alphabetic order.
#
# Module for degrees to radians conversion.
# https://docs.python.org/3.5/library/math.html#math.radians
from math import radians
#
# Blender library imports, in alphabetic order.
#
# These modules can only be imported if running from within Blender.
try:
    # Main Blender Python interface, which is used to get the size of a mesh.
    # Import isn't needed because the base class keeps a reference to the
    # interface object.
    # import bpy
    #
    # Blender Game Engine KX_GameObject
    # Import isn't needed because this class gets an object that has been
    # created elsewhere.
    # https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
    #
    # Blender Game Engine maths utilities, which can only be imported if running
    # from within the Blender Game Engine.
    # http://www.blender.org/api/blender_python_api_current/mathutils.html
    # This class gets a Vector from the bpy layer, so Vector needn't be
    # imported.
    from mathutils import Matrix
except ImportError as error:
    print(__doc__)
    print(error)
#
# Local imports.
#
# Blender Driver application with threads and locks.
import blender_driver.application.thread

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(blender_driver.application.thread.Application):
    _instructions = "Press ESC to crash BGE, or any other key to terminate."
    _bannerName = 'banner'
    _bannerObject = None
    
    @property
    def bannerObject(self):
        return self._bannerObject
    
    @property
    def dontDeletes(self):
        return self._dontDeletes
    
    # Overriden.
    def data_initialise(self):
        #
        # Formally, run the base class method. Actually, it's a pass.
        super().data_initialise()
        #
        # Do common initialisation for subclasses.
        self._bannerObject = self.data_add_banner()
        self._dontDeletes = [self.dataGateway, 'Lamp', self._bannerName]
        if self.templates is not None:
            self._dontDeletes.extend(self.templates.keys())
        
    def data_add_banner(self):
        banner = "\n".join(
            ("Blender Driver" , self.applicationName , self._instructions))
        return self.bpyutils.set_up_object(
            self._bannerName, {'text':banner, 'physicsType':'NO_COLLISION'
                               , 'location': (-5, -8, 3)})

    # Overriden.
    def game_initialise(self):
        super().game_initialise()
        self.mainLock.acquire()
        try:
            self._bannerObject = self.game_add_text(self._bannerName)
            log(DEBUG, "Game scene objects {}\nArguments: {}\nSettings: {}"
                , self.gameScene.objects, vars(self.arguments), self.settings)
            print(self._instructions)
        finally:
            self.mainLock.release()

    def game_add_object(self, objectName):
        object_ = self.gameScene.addObject(objectName, self.gameGateway)
        object_.worldPosition = self.bpy.data.objects[objectName].location
        log(DEBUG, "{} {}."
            , objectName, self.bpy.data.objects[objectName].dimensions)
        return object_

    def game_add_text(self, objectName, text=None):
        object_ = self.gameScene.addObject(objectName, self.gameGateway)
        object_.worldPosition = self.bpy.data.objects[objectName].location
        object_.worldOrientation.rotate(Matrix.Rotation(radians(90), 4, 'Y'))
        object_.worldOrientation.rotate(Matrix.Rotation(radians(90), 4, 'X'))
        if text is not None:
            # No text specified. Object will show whatever text was set up in
            # the data context.
            object_.text = text
        return object_

    def tick_skipped(self):
        log(WARNING, "Skipped ticks: {:d}", self.skippedTicks)
