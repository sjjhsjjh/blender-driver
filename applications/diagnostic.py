#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver diagnostic application.

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
# Module for the version of Python.
# https://docs.python.org/3.4/library/sys.html#sys.version
from sys import version as pythonVersion
#
# Module for logging current time and sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# This module uses Thread and Lock classes.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Local imports.
#
# Proper application base class module.
import blender_driver.application

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.Application):
    def _name(self, subroutine):
        return " ".join((__package__, self.__class__.__name__, str(subroutine)))
        
    def game_initialise(self):
        self._counter = 0
        self._threads = []
        if self.arguments.lock:
            self._threadLock = threading.Lock()
        else:
            self._threadLock = None
        print(self._name('initialise'), self._counter)
        print(self.arguments)
        print("Game scene objects", self.gameScene.objects)
        
    def game_tick(self):
        self._counter += 1
        print(time.strftime("%H:%M:%S"), self._name('tick'), self._counter,
              self.arguments.sleep, len(self._threads))
        if self.arguments.ticks > 0 and self._counter > self.arguments.ticks:
            print("".join((
                "Terminating after ticks. Counted:", str(self._counter),
                " Maximum:", str(self.arguments.ticks))))
            for thread in self._threads:
                thread.join()
            self.game_terminate()
        else:
            if self.arguments.thread:
                thread = threading.Thread(
                    target=self._tick_sleep,
                    args=(str(self._counter),),
                    name=str(self._counter))
                thread.start()
                self._threads.append(thread)
            else:
                self._tick_sleep()
    
    def _tick_sleep(self, name=None):
        if self._threadLock is not None:
            acquired = self._threadLock.acquire(False)
            if acquired:
                print(time.strftime("%H:%M:%S"), self._name(name),
                      "acquired lock.")
            else:
                print(time.strftime("%H:%M:%S"), self._name(name),
                      "didn't acquire lock.")
                return
            
        if self.arguments.sleep is None:
            print(time.strftime("%H:%M:%S"), self._name(name), "no sleep.")
        else:
            if int(self.arguments.sleep) == self.arguments.sleep:
                for sleep in range(self.arguments.sleep):
                    time.sleep(1)
                    print(time.strftime("%H:%M:%S"), self._name(name),
                          "sleep", sleep+1, "of", self.arguments.sleep)
            else:
                time.sleep(self.arguments.sleep)
                print(time.strftime("%H:%M:%S"), self._name(name),
                          "sleep", self.arguments.sleep)
                
        if self._threadLock is not None:
            print(time.strftime("%H:%M:%S"), self._name(name),
                  "releasing lock.")
            self._threadLock.release()
    
    def game_keyboard(self, keyEvents):
        #
        # Dump the keyboard and settings collection, for diagnostic purposes.
        print(self._name(''.join(("game_keyboard(,", str(keyEvents), ") ",
                                  str(self._key_number(keyEvents))))))
        print("Settings", self.settings)
        print("Arguments", self.arguments)
        print("Threads", self._threads)
        print("Python", pythonVersion)

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--sleep', type=float,
            help=
            "Sleep in each tick, for a floating point number of seconds."
            " Default is not to sleep.")
        parser.add_argument(
            '--lock', action='store_true',
            help='Thread lock.')
        parser.add_argument(
            '--thread', action='store_true',
            help='Start a thread in every tick.')
        parser.add_argument(
            '--ticks', type=int, default=10,
            help="Terminate after a number of ticks, or 0 for never.")
        return parser
