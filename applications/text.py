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
# Blender Game Engine maths utilities, which can only be imported if running
# from within the Blender Game Engine.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# This class gets a Vector from the bpy layer, so Vector needn't be imported.
from mathutils import Matrix
#
# Main Blender Python interface.
# Import isn't needed because the base class keeps a reference to the interface
# object.
# import bpy
#
# Font Drawing module, used to get text width.
# https://docs.blender.org/api/blender_python_api_current/blf.html
#
# bpy.ops.font.open(filepath="/home/jim/Downloads/fonts/IM Fell English/FeENrm2.ttf")
# bpy.data.curves['ememem'].font = bpy.data.fonts['IM_FELL_English_Roman']
#
import blf
#
# Local imports.
#
# Blender Driver application with threads and locks.
import blender_driver.application.thread

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.thread.Application):

    templates = {
        'text': {'text':".\n.", 'physicsType':'NO_COLLISION'},
        'smalltext': {'text':"0\n0", 'physicsType':'NO_COLLISION'
                      , 'scale':(0.5, 0.5, 0.5)},
        'cube': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                 , 'scale':(0.1, 0.1, 0.1)
                 #, 'scale':(0.15, 0.5, 5.0)
                 },
        'em': {'text':"m", 'physicsType':'NO_COLLISION'},
        'emem': {'text':"mm", 'physicsType':'NO_COLLISION'},
        'ememem': {'text':"mmm", 'physicsType':'NO_COLLISION'},
        'en': {'text':"n", 'physicsType':'NO_COLLISION'},
        'enen': {'text':"nn", 'physicsType':'NO_COLLISION'},
        'enenen': {'text':"nnn", 'physicsType':'NO_COLLISION'},
        'emnlem': {'text':"m\nm", 'physicsType':'NO_COLLISION'},
        'emsmall': {'text':"m", 'physicsType':'NO_COLLISION'
                    , 'scale':(0.5, 0.5, 0.5)},
        'emnlemsmall': {'text':"m\nm", 'physicsType':'NO_COLLISION'
                      , 'scale':(0.5, 0.5, 0.5)},
        'emwide': {'text':"m", 'physicsType':'NO_COLLISION'
                    , 'scale':(2.0, 1.0, 1.0)},
        'ememwide': {'text':"mm", 'physicsType':'NO_COLLISION'
                    , 'scale':(2.0, 1.0, 1.0)},
        'spacenl': {'text':" \n", 'physicsType':'NO_COLLISION'},
        'space': {'text':" ", 'physicsType':'NO_COLLISION'},
        'zero': {'text':"0", 'physicsType':'NO_COLLISION'
                 , 'location': (0, -2, 0)},
        'zerozero': {'text':"00", 'physicsType':'NO_COLLISION'
                 , 'location': (0, -4, 0)},
    }
    
    # Override.
    def _name(self, subroutine):
        return " ".join((__package__, __name__, str(subroutine)))

    def data_initialise(self):
        self.bpyutils.delete_except(
            [self.dataGateway, 'Lamp'] + list(self.templates.keys()) )
    
    @property
    def textBoxIndex(self):
        return self._textBoxIndex
    @textBoxIndex.setter
    def textBoxIndex(self, textBoxIndex):
        self._textBoxIndex = textBoxIndex % len(self._textBoxes)
        self.update_info()
        
    @property
    def textBox(self):
        return self._textBoxes[self.textBoxIndex]

    @property
    def textInfo(self):
        return self._textInfo[self.textBoxIndex]
    
    def postion_cube(self):
        if self._cube is not None:
            cubePosition = self.textBox.worldPosition.copy()
            # cubePosition[0] -= (self._cubeDimensions[0]
            #                     * 0.5
            #                     * self._cube.worldScale[0]) #+ 0.01
            # cubePosition[1] += (self._cubeDimensions[1]
            #                     * 0.5
            #                     * self._cube.worldScale[1])
            # cubePosition[2] += ((self.arguments.infoOffset * 0.5)
            #                     - (self._cubeDimensions[2] * 0.5))
            self._cube.worldPosition = cubePosition
        if self._cube2 is not None:
            cubePosition = self.textBox.worldPosition.copy()
            cubePosition[1] += self._textDimensions[self.textBoxIndex] * 1.35
            self._cube2.worldPosition = cubePosition
        
    
    def update_info(self):
        dimensionsFloat = list(blf.dimensions(0, self.textBox.text))

        # # object_ = self.bpy.data.objects['text']
        # name = 'temporary'
        # curve = self.bpy.data.curves.new(name, 'FONT')
        # curve.align_x = 'CENTER'
        # curve.align_y = 'CENTER'
        # curve.body = self.textBox.text
        # object_ = self.bpy.data.objects.new(name, curve)
        # # print(object_.dimensions)
        # scene = self.bpy.data.scenes[0]
        # # object_.data.body = self.textBox.text
        # 
        # scene.objects.link(object_)
        # scene.update()
        # # print(object_.dimensions)
        # dimensionsFloat.extend((object_.dimensions[0], object_.dimensions[1]))
        # self._textDimensions[self.textBoxIndex] = object_.dimensions[0]

        name = 'ememem'
        emememObjD = self.bpy.data.objects[name].dimensions[0]
        emememTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
        boxTxtD = blf.dimensions(0, self.textBox.text)[0]
        self._textDimensions[self.textBoxIndex] = (
            (boxTxtD / emememTxtD) * emememObjD)
        dimensionsFloat.append(self._textDimensions[self.textBoxIndex])



        # if self._cube is not None:
            # worldScale = self._cube.worldScale.copy()
            # self._cube.worldScale = [0.15
            #                          , object_.dimensions[0]# * 0.5
            #                          , object_.dimensions[1]# * 0.5
            #                          ]
        # self.bpy.data.objects.remove(object_, True)
        # self.bpy.data.curves.remove(curve, True)
        
        self.postion_cube()

        dimensionsStr = []
        for dimension in dimensionsFloat:
            dimensionsStr.append("{:.2f}".format(dimension))
        self.textInfo.text = "\n".join(dimensionsStr)

    # Override.
    def game_initialise(self):
        super().game_initialise()
        self.mainLock.acquire()
        try:
            self._textBoxIndex = None
            self._cube = None
            self._cube2 = None

            boxes = self.arguments.boxes
            self._textBoxes = [None] * boxes
            self._textDimensions = [None] * boxes
            self._textInfo = [None] * boxes
            worldPosition = None
            yOffset = 5.0
            for index in range(boxes):
                object_ = self.add_text('text', str(index + 1))
                if worldPosition is None:
                    worldPosition = object_.worldPosition.copy()
                    worldPosition[1] -= yOffset * 0.5 * boxes
                else:
                    worldPosition[1] += yOffset
                object_.worldPosition = worldPosition.copy()
                self._textBoxes[index] = object_
                
                object_ = self.add_text('smalltext')
                infoPosition = worldPosition.copy()
                infoPosition[2] += self.arguments.infoOffset
                object_.worldPosition = infoPosition
                self._textInfo[index] = object_

                self.textBoxIndex = index
                self.update_info()
                
            self._cube = self.gameScene.addObject('cube', self.gameGateway)
            self._cubeDimensions = self.bpy.data.objects['cube'].dimensions
            if self.arguments.verbose:
                print(self._name('game_initialise')
                      , self._cubeDimensions, self._cube.worldScale)
            self.print_dimensions()

            self._cube2 = self.gameScene.addObject('cube', self.gameGateway)

            # Next line invokes the setter, so the cube gets positioned.
            self.textBoxIndex = 0
            print("Ctrl-Q to terminate.")
        finally:
            self.mainLock.release()
    
    def print_dimensions(self):
        if self.arguments.verbose:
            keys = []
            keys[:] = self.templates.keys()
            keys.sort()
            for name in keys:
                template = self.templates[name]
                if 'text' in template:
                    print(name
                          , self.bpy.data.objects[name].dimensions
                          , blf.dimensions(0, template['text']))
            name = 'em'
            emObjD = self.bpy.data.objects[name].dimensions[0]
            emTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            name = 'emem'
            ememObjD = self.bpy.data.objects[name].dimensions[0]
            ememTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            name = 'ememem'
            emememObjD = self.bpy.data.objects[name].dimensions[0]
            emememTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            name = 'en'
            enObjD = self.bpy.data.objects[name].dimensions[0]
            enTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            name = 'enen'
            enenObjD = self.bpy.data.objects[name].dimensions[0]
            enenTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            name = 'enenen'
            enenenObjD = self.bpy.data.objects[name].dimensions[0]
            enenenTxtD = blf.dimensions(0, self.templates[name]['text'])[0]
            print(emObjD, emTxtD, ememObjD, ememTxtD)
            print(ememObjD - emObjD, ememTxtD - emTxtD)
            print("m", ememObjD - (2.0 * emObjD))
            print("n", enenObjD - (2.0 * enObjD))
            # print(ememObjD, ememTxtD, emememObjD, emememTxtD)
            print(emememObjD - ememObjD, emememTxtD - ememTxtD)
            print((ememObjD - emObjD) / (ememTxtD - emTxtD))
            print(2.0 * emObjD, (2.0 * emObjD) - ememObjD)
            print(3.0 * emObjD, (3.0 * emObjD) - emememObjD)
            
            # Divide by this: ememTxtD - emTxtD
            # Multiply by this: (ememObjD - emObjD)
            # Add the value for an empty text, given by:
            # emObjD - (ememObjD - emObjD)
            

    def add_text(self, objectName='text', text=""):
        object_ = self.gameScene.addObject(objectName, self.gameGateway)
        object_.worldPosition = self.bpy.data.objects[objectName].location
        object_.worldOrientation.rotate(Matrix.Rotation(radians(90), 4, 'Y'))
        object_.worldOrientation.rotate(Matrix.Rotation(radians(90), 4, 'X'))
        object_.text = text
        return object_
    
    def game_keyboard(self, keyEvents):
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        if self.arguments.verbose:
            print(self._name('game_keyboard'), str(keyEvents)
                  , '"'.join(('', keyString, ''))
                  , ctrl, alt,
                  self.bge.events.BACKSPACEKEY, self.bge.events.TABKEY)
        if keyString == "q" and ctrl:
            self.game_terminate()
            return
        append = not (alt or ctrl)
        textBox = self._textBoxes[self.textBoxIndex]
        for key, status in keyEvents:
            if status != self.bge.logic.KX_INPUT_JUST_ACTIVATED:
                continue
            if key == self.bge.events.TABKEY:
                self.print_dimensions()
                self.textBoxIndex += 1
                append = False
            if (key == self.bge.events.BACKSPACEKEY
                and len(self.textBox.text) > 0
               ):
                self.textBox.text = self.textBox.text[:-1]
                self.update_info()
                append = False
        if append:
            self.textBox.text = ''.join((self.textBox.text, keyString))
            self.update_info()
            
    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--boxes', type=int, default=3, help='Number of text boxes.')
        parser.add_argument(
            '--infoOffset', type=float, default=3.5, help=
            'Vertical offset from a text box to its information panel.')
        parser.add_argument(
            '--verbose', action='store_true', help='Verbose logging.')
        return parser
