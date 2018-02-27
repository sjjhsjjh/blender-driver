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
    import blf
    #
    # bpy.ops.font.open(filepath="/home/jim/Downloads/fonts/IM Fell English/FeENrm2.ttf")
    # bpy.data.curves['ememem'].font = bpy.data.fonts['IM_FELL_English_Roman']
    #
except ImportError as error:
    print(__doc__)
    print(error)
#
# Local imports.
#
from . import bpyutils

class TextUtilities(object):
    @property
    def objectNames(self):
        return self._objectNames

    def data_initialise(self, bpyutils, objectName=None):
        if objectName is None:
            objectName = self.objectNames[0]

        bpyutils.set_up_object(
            objectName, {'text':"mmmmm", 'physicsType':'NO_COLLISION'})
        self._objectNames = [objectName]
    
    def game_calibrate(self, objectName=None):
        '''Store a calibration ratio.'''
        numerator, denominator = self.get_calibration(objectName)
        self._ratio = numerator / denominator

    def get_calibration(self, objectName=None):
        '''\
        Get a calibration ratio as a float tuple: (numerator, denominator).
        '''
        if objectName is None:
            objectName = self.objectNames[0]
        object_ = self._bpy.data.objects[objectName]
        return (float(object_.dimensions[0])
                , float(blf.dimensions(0, object_.data.body)[0]))

    @staticmethod
    def text_width_raw(text):
        '''Text width from the Blender Font module, without calibration.'''
        return blf.dimensions(0, text)[0]
        
    def text_width(self, text):
        '''\
        Text width from the Blender Font module, calibrated by the stored
        calibration ratio, if there is one, or on the fly otherwise.
        '''
        ratio = self._ratio
        if ratio is None:
            numerator, denominator = self.get_calibration()
            ratio = numerator / denominator
        #
        # Next line has an unexplained fudge factor: 1.35
        return TextUtilities.text_width_raw(text) * ratio * 1.35

    def __init__(self, bpy):
        self._bpy = bpy
        self._ratio = None
        self._objectNames = ["TextUtilitiesmmmmm"]
