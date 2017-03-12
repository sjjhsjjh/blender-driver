#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application base class.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
import argparse
#
# Python module for dynamic import, which is used so that this module can be
# loaded in the bpy context and in the bge context. It is not possible to import
# bge in the bpy context.
# https://docs.python.org/3.5/library/importlib.html
import importlib

class Application(object):
    templates = None
    
    _applicationName = None
    @property
    def applicationName(self):
        if self._applicationName is None:
            self._applicationName = (
                self.__class__.__module__.rpartition(".")[-1])
        return self._applicationName

    @property
    def bpy(self):
        """Reference to the Blender Python interface object.
        
        A subclass can use this instead of importing bpy, in case that isn't
        possible in its execution context."""
        return self._bpy
    
    @property
    def bpyutils(self):
        """Reference to the Blender Driver utilities interface object.
        
        A subclass can use this instead of importing blender_driver.bpyutils, in
        case that isn't possible in its execution context."""
        return self._bpyutils

    @property
    def dataGateway(self):
        """Reference to the driver gateway data object."""
        return self._dataGateway
    
    @property
    def dataScene(self):
        """Reference to the data Scene object."""
        return self._dataScene
    
    def diagnostic_remove_controllers(self, controllers):
        """Method that is invoked to remove controllers. Only override to remove
        controllers for diagnostic purposes. This method is called in the data
        context. To remove a controller, set its property to None, as in:
        
        controllers.tick = None"""
        pass
    
    def data_initialise(self):
        """Override it."""
        pass

    def data_constructor(self, scene, gateway):
        """Method that is invoked just after the constructor in the Blender data
        context. Don't override."""
        #
        # Set up references to modules that might be needed in a subclass, but
        # not be importable there.
        #
        # Main Blender Python interface, bpy.
        self._bpy = importlib.import_module('bpy')
        #
        # Blender Driver bpy utilities. Seems that it has to be obtained by
        # importing the parent package.
        parent = importlib.import_module('..', __package__)
        self._bpyutils = parent.bpyutils
        #
        # Store the references from the constructor caller.
        self._dataGateway = gateway
        self._dataScene = scene
        #
        # Add the template objects.
        self.bpyutils.set_up_objects(self.templates)

    @property
    def argumentParser(self):
        """argparse.ArgumentParser instance for the launcher."""
        return self._argumentParser

    @property
    def bge(self):
        """Reference to the Blender Game Engine Python interface object.
        
A subclass can use this instead of importing bge, in case that isn't possible in
its execution context.
        
See also:
        
-   https://www.blender.org/api/blender_python_api_current/bge.logic.html
-   http://www.blender.org/api/blender_python_api_current/bge.types.html
"""
        return self._bge

    @property
    def gameScene(self):
        """Reference to the game Scene object.
        
See also:
        
-   http://www.blender.org/api/blender_python_api_current/bge.types.html#bge.types.KX_Scene
"""
        return self._gameScene
    
    @property
    def gameGateway(self):
        """Reference to the driver gateway game object."""
        return self._gameGateway
    
    @property
    def settings(self):
        """Dictionary of settings from everything prior, including the command
        line."""
        return self._settings
    
    @property
    def arguments(self):
        """Command line switches for the application."""
        return self._arguments
    
    def key_events_to_string(self, keyEvents):
        """Generate a string from a keyboard sensor event array. Handles
        multiple keys, and left and right shift. Doesn't handle Caps Lock."""
        # For keyEvents.
        # https://docs.blender.org/api/blender_python_api_current/bge.types.SCA_KeyboardSensor.html
        #
        # For key constants and EventToCharacter
        # https://docs.blender.org/api/blender_python_api_current/bge.events.html
        #
        # For KX_INPUT_* values
        # https://docs.blender.org/api/blender_python_api_current/bge.logic.html#id5
        #
        # First, check for any shift keys.
        shift = False
        ctrl = False
        alt = False
        for key, status in keyEvents:
            shift = (shift
                     or key == self.bge.events.RIGHTSHIFTKEY
                     or key == self.bge.events.LEFTSHIFTKEY)
            ctrl = (ctrl
                    or key == self.bge.events.LEFTCTRLKEY
                    or key == self.bge.events.RIGHTCTRLKEY)
            alt = (alt
                   or key == self.bge.events.LEFTALTKEY
                   or key == self.bge.events.RIGHTALTKEY)
        #
        # Build a list of key characters, possibly capitalised.
        characters = []
        for key, status in keyEvents:
            if status == self.bge.logic.KX_INPUT_JUST_ACTIVATED:
                characters.append(self.bge.events.EventToCharacter(key, shift))
        #
        # Concatenate and return.
        return "".join(characters), ctrl, alt
    
    def game_initialise(self):
        """Method that is invoked just after the constructor in the Blender game
        context. Override it."""
        pass

    def game_keyboard(self, keyEvents):
        """Method that is invoked on every keyboard event in the Blender Game
        Engine. Override it."""
        pass
    
    def game_tick(self):
        """Method that is invoked on every tick in the Blender Game Engine.
        Override it."""
        pass

    def game_terminate(self):
        """Terminate the Blender Game Engine by ending the scene. Call super()
        if overriden."""
        self.gameScene.end()

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Override and call super if the
        application has command line switches."""
        parser = argparse.ArgumentParser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        return parser
    
    def game_constructor(self, scene, gateway):
        """Method that is invoked just after the constructor in the Blender Game
        Engine context. Don't override."""
        # Set up references to modules that might be needed in a subclass, but
        # not be importable there.
        #
        # Main Blender Python interface, bpy, and Blender Game Engine interface,
        # bge.
        self._bpy = importlib.import_module('bpy')
        self._bge = importlib.import_module('bge')
        self._gameScene = scene
        self._gameGateway = gateway

    def __init__(self, settings):
        """Constructor common to both Blender data and Blender Game Engine
        contexts. Call super if overriden."""
        #
        # Store the settings collection
        self._settings = settings.copy()
        #
        # Parse the application switches.
        self._argumentParser = self.get_argument_parser()
        self._arguments, \
        unknownArguments = self.argumentParser.parse_known_args(
            self.settings['arguments']['applicationSwitches'] )
        if len(unknownArguments) > 0:
            raise ValueError(''.join((
                'Unknown arguments "', '" "'.join(unknownArguments), '".')))
