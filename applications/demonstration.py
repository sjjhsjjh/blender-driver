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
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Blender library imports, in alphabetic order.
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
    
    # Overriden.
    def data_initialise(self):
        #
        # Do common initialisation for subclasses.
        self._bannerObject = self.data_add_banner()
        self.dontDeletes.append(self._bannerName)
        #
        # Run the base class method.
        super().data_initialise()
        
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

    # Overriden.
    def game_keyboard(self, *args):
        #
        # Formally, run the base class method. Actually, it's a pass.
        super().game_keyboard(*args)
        #
        # Default is to terminate on any key press.
        log(DEBUG, "Terminating.")
        self.game_terminate()
        
    def tick_skipped(self):
        log(WARNING, "Skipped ticks: {:d}.", self.skippedTicks)
