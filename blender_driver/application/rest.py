#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application with various RESTful classes and interfaces.

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
# The import isn't needed because this class uses the base class to get an
# object.
# import argparse
#
# Local imports.
#
# Application base class module.
from . import thread
#
# Wrapper for Blender game object and camera that is easy to make RESTful.
from path_store.blender_game_engine import \
    get_game_object_subclass, get_camera_subclass, Cursor, \
    get_game_text_subclass
#
# RESTful interface base class and Animation subclass for pathstore.
from path_store.rest import AnimatedRestInterface

class Application(thread.Application):
    
    @property
    def Camera(self):
        return self._Camera

    # Override.
    def game_add_object(self, objectName):
        return self._GameObject(super().game_add_object(objectName))
    
    # Override.
    def game_add_text(self, objectName, text=None):
        return self._GameText(super().game_add_text(objectName, text))
    
    def _add_visualiser(self):
        return self._GameObject(self.game_add_object(self._visualiserName))
    def _add_empty(self):
        return self._GameObject(self.game_add_object(self._emptyName))

    def game_add_cursor(self):
        cursor = Cursor()
        #
        # Give the cursor the means to add necessary objects.
        cursor.add_visualiser = self._add_visualiser
        cursor.add_empty = self._add_empty
        #
        # Cursor needs a restInterface to get an object from the path.
        cursor.restInterface = self._restInterface
        return cursor
    
    def game_initialise(self):
        super().game_initialise()
        self._objectRootPath = ('root','objects')
        self._visualiserName = 'visualiser'
        self._emptyName = 'empty'

        self._restInterface = AnimatedRestInterface()
        self._restInterface.rest_put(None, self._objectRootPath)

        self._GameObject = get_game_object_subclass(self.bge)
        self._Camera = get_camera_subclass(self.bge, self._GameObject)
        self._GameText = get_game_text_subclass(self.bge, self._GameObject)

    # Override.
    def game_tick_run(self):
        # Formally, call the base class although it is a pass.
        super().game_tick_run()
        with self.mainLock:
            # Call the shortcut to set current time into all the current
            # animations, which makes them animate in the scene.
            self.print_completions_log(
                *self._restInterface.set_now_times(self.tickPerf))
            #
            # Update all cursors, by updating all physics objects.
            def update(point, path, results):
                if point is not None:
                    point.update()
            self._restInterface.rest_walk(update, self._objectRootPath)

    def print_completions_log(self, anyCompletions, logStore):
        '''\
        Called every tick and passed the AnimatedRestInterface.set_now_times
        return value. Override the application requires these results for any
        reason. See the unittest application for an example.
        '''
        pass
