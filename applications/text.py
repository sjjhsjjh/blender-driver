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
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
import logging
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Module for degrees to radians conversion.
# https://docs.python.org/3.5/library/math.html#math.radians
from math import radians
#
# This module uses Thread and Lock classes.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Module for logging current time and sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# Third party modules, in alphabetic order.
#
# Blender library imports, in alphabetic order.
#
# These modules can only be imported if running from within Blender.
try:
    # Main Blender Python interface.
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
    #
    # Font Drawing module, used to get text width.
    # https://docs.blender.org/api/blender_python_api_current/blf.html
    import blf
except ImportError as error:
    print(__doc__)
    print(error)
# Local imports.
#
# Blender Driver application with threads and locks.
from . import demonstration

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(demonstration.Application):

    templates = {
        'text': {'text':".\n.", 'physicsType':'NO_COLLISION'
                 , 'location': (0, 0, -1)},
        'smalltext': {'text':"0\n0", 'physicsType':'NO_COLLISION'
                      , 'scale':(0.5, 0.5, 0.5)},
        'cube': {'subtype':'Cube', 'physicsType':'NO_COLLISION'
                 , 'scale':(0.1, 0.1, 0.1) },
        'counter': {'text':"counter text long", 'physicsType':'NO_COLLISION'},
        'clock': {'text':"short", 'physicsType':'NO_COLLISION'}
        }
    
    # Override.
    _instructions = "Ctrl-Q to terminate.\nTAB to traverse."

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
            self._cube.worldPosition = cubePosition
        if self._cube2 is not None:
            cubePosition = self.textBox.worldPosition.copy()
            cubePosition[1] += self._textDimensions[self.textBoxIndex]
            self._cube2.worldPosition = cubePosition
    
    def update_info(self):
        dimensions = list(blf.dimensions(0, self.textBox.text))
        textWidth = self.text_width(self.textBox.text)
        self._textDimensions[self.textBoxIndex] = textWidth
        dimensions.append(textWidth)
        self.postion_cube()
        self.textInfo.text = "\n".join(
            "{:.2f}".format(_) for _ in dimensions)

    # Override.
    def game_initialise(self):
        super().game_initialise()
        self.mainLock.acquire()
        try:
            self._textBoxIndex = None
            self._cube = None
            self._cube2 = None

            self._set_up_text_boxes()
            
            self._objectClock = self.game_add_text("clock")
            worldPosition = self.bannerObject.worldPosition.copy()
            worldPosition[1] += 13.0
            self._objectClock.worldPosition = worldPosition.copy()
            #
            # Counter object, which is a Blender Text.
            self._objectCounter = self.game_add_text("counter")
            self._objectCounterNumber = 0
            self.position_counter()

            self._cube = self.gameScene.addObject('cube', self.gameGateway)
            self._cubeDimensions = self.bpy.data.objects['cube'].dimensions
            log(DEBUG, "Cube dimensions: {}. World scale: {}."
                , self._cubeDimensions, self._cube.worldScale)

            self._cube2 = self.gameScene.addObject('cube', self.gameGateway)

            # Next line invokes the setter, so the cube gets positioned.
            self.textBoxIndex = 0
        finally:
            self.mainLock.release()
        #
        # Spawn a thread on which to cycle the counter.
        threading.Thread(target=self.cycle_count_run).start()
        
    def _set_up_text_boxes(self):
        boxes = self.arguments.boxes
        self._textBoxes = [None] * boxes
        self._textDimensions = [None] * boxes
        self._textInfo = [None] * boxes
        worldPosition = None
        yOffset = 5.0
        for index in range(boxes):
            object_ = self.game_add_text('text', str(index + 1))
            if worldPosition is None:
                worldPosition = object_.worldPosition.copy()
                worldPosition[1] -= yOffset * 0.5 * boxes
            else:
                worldPosition[1] += yOffset
            object_.worldPosition = worldPosition.copy()
            self._textBoxes[index] = object_
                
            object_ = self.game_add_text('smalltext')
            infoPosition = worldPosition.copy()
            infoPosition[2] += self.arguments.infoOffset
            object_.worldPosition = infoPosition
            self._textInfo[index] = object_

            self.textBoxIndex = index
            self.update_info()

    def cycle_count_run(self):
        """Cycle a counter for ever. Run as a thread."""
        counterReset = 1000
        while True:
            self.mainLock.acquire()
            try:
                if self.terminating():
                    log(DEBUG, "Stop.")
                    return
                self._objectCounter.text = str(self._objectCounterNumber)
                self._objectCounterNumber = (
                    (self._objectCounterNumber + 1) % counterReset)
            finally:
                self.mainLock.release()
            if self.arguments.sleep is not None:
                time.sleep(self.arguments.sleep)

    def game_keyboard(self, keyEvents):
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        log(DEBUG, '{} "{}" ctrl:{} alt:{} {} {}'
            , keyEvents, keyString, ctrl, alt
            , self.bge.events.BACKSPACEKEY, self.bge.events.TABKEY)
        if keyString == "q" and ctrl:
            self.game_terminate()
            return
        append = not (alt or ctrl)
        textBox = self._textBoxes[self.textBoxIndex]
        for key, status in keyEvents:
            if status != self.bge.logic.KX_INPUT_JUST_ACTIVATED:
                continue
            if key == self.bge.events.TABKEY:
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
            
    def game_tick_run(self):
        #
        # Formally, run the base class tick. Actually, it's a pass.
        super().game_tick_run()
        self.mainLock.acquire()
        try:
            #
            # Update the time displayed in the clock.
            self._objectClock.text = time.strftime("%H:%M:%S")
            #
            # Slide the counter around.
            self.position_counter()
        finally:
            self.mainLock.release()
    
    def position_counter(self):
        worldPosition = self._objectClock.worldPosition.copy()
        worldPosition[2] -= 2.0
        
        counterRange = 50
        counterScale = 4.0
        counterPosition = self._objectCounterNumber % (counterRange * 2)
        if counterPosition > counterRange:
            counterPosition = (counterRange * 2) - counterPosition
        worldPosition[1] += (
            (counterScale * float(counterPosition)) / float(counterRange))
        self._objectCounter.worldPosition = worldPosition.copy()

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--boxes', type=int, default=3, help='Number of text boxes.')
        parser.add_argument(
            '--infoOffset', type=float, default=2.0, help=
            'Vertical offset from a text box to its information panel.')
        parser.add_argument(
            '--sleep', type=float, help=
            "Sleep after each increment, for a floating point number of"
            " seconds. Default is not to sleep.")
        return parser
