#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application with threads and synchronisation.

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
# This module uses Thread and Lock classes.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Module for logging current time and sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# Local imports.
#
# Application base class module.
from . import base

class Application(base.Application):
    
    @property
    def tickLock(self):
        return self._tickLock
    
    def terminating(self):
        if not self._terminateLock.acquire(False):
            return True
        self._terminateLock.release()
        return False
    
    @property
    def skippedTicks(self):
        return self._skippedTicks

    def _run_with_tick_lock(self, run):
        if not self.tickLock.acquire(False):
            self._skippedTicks += 1
            if self.ok_to_skip_tick():
                return
            if self._tickWaitLock.acquire(False):
                print("Tick Wait Lock acquired ...")
                self.tickLock.acquire(True)
                print("Releasing Tick Wait Lock.")
                self._tickWaitLock.release()
            else:
                return
        self._skippedTicks = 0
        run()
        self.tickLock.release()
        
    def ok_to_skip_tick(self):
        return True

    # Override.
    def game_initialise(self):
        """Method that is invoked just after the constructor in the Blender game
        context. Don't override; implement game_intialise_run() instead."""
        #
        # It might be unnecessary that the terminate lock is a threading.Lock()
        # instance. An ordinary property might do just as well, because it only
        # gets set to True.
        self._terminateLock = threading.Lock()
        self._tickLock = threading.Lock()
        self._skippedTicks = 0
        self._tickWaitLock = threading.Lock()

        thread = threading.Thread(
            target=self._run_with_tick_lock,
            args=(self.game_initialise_run,))
        thread.start()

    # Override.
    def game_tick(self):
        """Method that is invoked on every tick in the Blender Game Engine.
        Don't override; implement game_tick_run() instead."""
        if self.terminating():
            return
        thread = threading.Thread(
            target=self._run_with_tick_lock,
            args=(self.game_tick_run,))
        thread.start()

    # Override.
    def game_terminate(self, verbose=False):
        if verbose:
            print("Acquiring terminate lock...")
        self._terminateLock.acquire(True)
        if verbose:
            print("Terminate lock acquired.")
            print("".join(("Joining threads:",
                           str(threading.active_count() - 1))))
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                thread.join()
        super().game_terminate()
    
    def game_initialise_run(self):
        """Method that is run in a thread in the initialise. Override it."""
        pass

    def game_tick_run(self):
        """Method that is run in a thread in every tick in which the tick lock
        can be acquired. Override it."""
        pass
