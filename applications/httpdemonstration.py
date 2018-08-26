#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

This code illustrates:

-   HTTP server in Blender Game Engine as back end.
-   JavaScript front end.

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
from . import cursorphysics
#
# Blender Driver application with HTTP server.
import blender_driver.application.http

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))

class Application(
    blender_driver.application.http.Application, cursorphysics.Application):

    def game_initialise(self):
        super().game_initialise()
        self._bannerObject.text = "\n".join((
            " ".join(("Browse", self._url)),
            "Ctrl-Q here to terminate, or ESC to crash."))
        self._restInterface.rest_put(
            ('root', 'floor'), tuple(self._cursorPath) + ('subjectPath',))
        gameObjects = self._restInterface.rest_delete(('root', 'gameObjects'))
        del gameObjects[:]
        self._restInterface.rest_put({
             'speed': self._cameraLinear,
             'valuePath': ('root', 'camera', 'worldPosition', 0),
             'targetValue': 20.0
        }, ('animations', 'camera_setup', 0))
