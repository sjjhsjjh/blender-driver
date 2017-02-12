#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver diagnostic application.
This application doesn't make anything happen in the 3D scene. It demonstrates
various things relating to use of Python in the Blender Game Engine (BGE).

-   When a controllers module gets loaded by BGE.
-   Use of threads and thread locks for synchronisation.
-   Keyboard events.

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
# This module prints diagnostic information about threads.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Module for logging current time and sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# Local imports.
#
# Proper threaded application module.
import blender_driver.application.thread

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.thread.Application):
    def _name(self, subroutine):
        return " ".join((__package__, self.__class__.__name__, str(subroutine)))
        
    def diagnostic_remove_controllers(self, controllers):
        super().diagnostic_remove_controllers(controllers)
        if self.arguments.removeInitialiseController:
            controllers.initialise = None
        if self.arguments.removeTickController:
            controllers.tick = None
        
    # Override.
    def game_initialise(self):
        if self.arguments.thread:
            super().game_initialise()
        else:
            self.game_initialise_run()

    def game_initialise_run(self):
        self._counter = 0
        print(self._name('initialise'), self._counter)
        print(self.arguments)
        print("Game scene objects", self.gameScene.objects)
        if self.arguments.removeTickController:
            print("Tick controller removed. Terminate BGE by pressing Escape.")

        self._dummy_action(self.arguments.sleepInitialise, "initialise")
        
    # Override.
    def game_tick(self):
        self._counter += 1
        print(time.strftime("%H:%M:%S"), self._name('tick'), self._counter,
              self.arguments.sleepTick, threading.active_count())

        if self.arguments.ticks > 0 and self._counter > self.arguments.ticks:
            print("".join((
                "Terminating after ticks. Counted:", str(self._counter),
                " Maximum:", str(self.arguments.ticks),
                " Threads:", str(threading.active_count())
                )))
            self.game_terminate()
            return
        
        if self.arguments.thread:
            super().game_tick()
        else:
            self.game_tick_run()

    # Override.
    def game_tick_run(self):
        self._dummy_action(
            self.arguments.sleepTick, " ".join(('tick', str(self._counter))))

    # Override.
    def ok_to_skip_tick(self):
        print(time.strftime("%H:%M:%S"), self._counter, "tick skipped.")
        return True

    # Override.
    def game_terminate(self):
        if self.arguments.terminateLock:
            super().game_terminate(True)
        else:
            print("No terminate lock.")
            #
            # Go up two class inheritance levels and call the method there.
            super(blender_driver.application.thread.Application, self
                  ).game_terminate()
    
    def _dummy_action(self, duration, name=None):
        if self.arguments.tickLock:
            print(time.strftime("%H:%M:%S"), self._name(name), "ticking.")
            
        if duration is None:
            print(time.strftime("%H:%M:%S"), self._name(name), "no sleep.")
        else:
            if int(duration) == duration:
                duration = int(duration)
                for sleep in range(duration):
                    if self.terminating():
                        print(time.strftime("%H:%M:%S"), self._name(name),
                              "stopped by terminate lock.")
                        break
                    time.sleep(1)
                    print(time.strftime("%H:%M:%S"), self._name(name),
                          "sleep", sleep+1, "of", duration)
            else:
                if self.terminating():
                    print(time.strftime("%H:%M:%S"), self._name(name),
                          "stopping instead of sleeping.")
                else:
                    time.sleep(duration)
                    print(time.strftime("%H:%M:%S"), self._name(name), "sleep",
                          duration)
                
        if self.arguments.tickLock:
            print(time.strftime("%H:%M:%S"), self._name(name), "end of tick.")
    
    # Override.
    def terminating(self):
        if self.arguments.terminateLock:
            return super().terminating()
        return False
    
    def game_keyboard(self, keyEvents):
        #
        # Dump the keyboard event, for diagnostic purposes.
        print(self._name(''.join(("game_keyboard(,", str(keyEvents), ") ",
                                  str(self.key_number(keyEvents))))))
        if self.arguments.dumpOnKey:
            print("Settings", self.settings)
            print("Arguments", self.arguments)
            print("Threads", threading.enumerate())
            print("Python", pythonVersion)
        if self.key_number(keyEvents) == 113 and self.arguments.quitOnQ:
            self.game_terminate()

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--dumpOnKey', action='store_true', help=
            "Dump diagnostic information on every key press. Default is to"
            " dump only the key event.")
        parser.add_argument(
            '--sleepTick', type=float, help=
            "Sleep in each tick, for an integer or floating point number of"
            " seconds. If an integer is specified, actually execute that number"
            " of one second sleeps. Otherwise, execute a single sleep of the"
            " specified duration. Default is not to sleep.")
        parser.add_argument(
            '--sleepInitialise', type=float, help=
            "Sleep in the initialise. Same semantics as --sleepTick.")
        parser.add_argument(
            '--terminateLock', action='store_true', help=
            "Indicate termination with a thread lock. The lock is acquired and"
            " released before every sleep, in a tick or initialise.")
        parser.add_argument(
            '--tickLock', action='store_true', help=
            "Acquire and release a thread lock in every tick and initialise."
            " Acquisition is synchronous. If acquisition fails, processing is"
            " skipped for that tick.")
        parser.add_argument(
            '--thread', action='store_true', help=
            'Start a thread in every tick, and in the initialise.')
        parser.add_argument(
            '--ticks', type=int, default=10, help=
            "Terminate after a number of ticks, or 0 for never. Default is to"
            " terminate after 10 ticks.")
        parser.add_argument(
            '--quitOnQ', action='store_true', help="Quit when Q is pressed.")
        parser.add_argument(
            '--removeTickController', action='store_true', help=
            "Remove the tick controller. This causes the Python instance to"
            " receive no execution cycles after initialisation, unless there is"
            " a keyboard event. This means that nothing will happen after the"
            " initialise controller has finished.")
        parser.add_argument(
            '--removeInitialiseController', action='store_true', help=
            "Remove the initialise controller. Why do this? If you want to see"
            " when the Python instance gets started in the Blender Game"
            " Engine.")
        return parser
