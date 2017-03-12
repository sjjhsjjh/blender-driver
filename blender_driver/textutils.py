#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Utility layer on the Blender Python programming interface for text handling.
This isn't the utilities for the Blender Game Engine.

This module can only be used from within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order, would go here.
#
# Blender library imports, in alphabetic order.
#
# These modules can only be imported if running from within Blender.
try:
    # Font Drawing module, used to get text width.
    # https://docs.blender.org/api/blender_python_api_current/blf.html
    #
    # bpy.ops.font.open(filepath="/home/jim/Downloads/fonts/IM Fell English/FeENrm2.ttf")
    # bpy.data.curves['ememem'].font = bpy.data.fonts['IM_FELL_English_Roman']
    #
    import blf
except ImportError as error:
    print(__doc__)
    print(error)
#
# Local imports.
#
from . import bpyutils

class TextUtilities(object):
    _calibratorName = "TextUtilitiesmmmmm"
    _bpy = None
    _calibratorRatio = None
    _objectNames = None
    
    @property
    def initialised(self):
        return False if self._calibratorRatio is None else True
    
    @property
    def objectNames(self):
        return self._objectNames

    def data_initialise(self, bpyutils, objectName=None):
        if objectName is None:
            objectName = self._calibratorName
        else:
            self._calibratorName = objectName
        bpyutils.set_up_object(
            objectName, {'text':"mmmmm", 'physicsType':'NO_COLLISION'})
        self._objectNames = [objectName]
    
    def game_initialise(self, objectName=None):
        if objectName is None:
            objectName = self._calibratorName
        else:
            self._calibratorName = objectName
        self._objectNames = [objectName]
        object_ = self._bpy.data.objects[objectName]
        self._calibratorRatio = (
            object_.dimensions[0] / blf.dimensions(0, object_.data.body)[0])
        
    def text_width(self, text):
        if self._calibratorRatio is None:
            return 0.0
        #
        # Next line has an unexplained fudge factor: 1.35
        return blf.dimensions(0, text)[0] * self._calibratorRatio * 1.35

    def __init__(self, bpy):
        self._bpy = bpy
