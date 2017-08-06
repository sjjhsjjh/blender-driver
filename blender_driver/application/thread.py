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
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# This module uses Thread and Lock classes.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Module for perf_counter.
# https://docs.python.org/3.5/library/time.html
import time
#
# Local imports.
#
# Application base class module.
from . import base

class Application(base.Application):
    
    @property
    def mainLock(self):
        return self._mainLock
    
    def terminating(self):
        """
        Check whether the application is being terminated. To be super-safe,
        only call this after acquiring mainLock.
        """
        if self._terminateLock.acquire(False):
            self._terminateLock.release()
            return False
        return True
    
    @property
    def skippedTicks(self):
        return self._skippedTicks
    
    @property
    def tickPerf(self):
        """
        Reference time for the start of the current tick; float representation
        of a number of seconds. Value will have been generated by
        time.perf_counter().
        """
        return self._tickPerf

    # Override.
    def game_initialise(self):
        """Method that is invoked just after the constructor in the Blender game
        context. Call super first if overriden."""
        #
        # It might be unnecessary that the terminate lock is a threading.Lock()
        # instance. An ordinary property might do just as well, because it only
        # gets set to True.
        self._terminateLock = threading.Lock()
        self._mainLock = threading.Lock()
        self._tickLock = threading.Lock()
        self._tickRaise = None
        self._skippedTicks = 0
        #
        # Reference time for when the game engine was started.
        self._gameInitialisePerf = time.perf_counter()
        self._tickPerf = 0.0

    # Override.
    def game_tick(self):
        """Method that is invoked on every tick in the Blender Game Engine.
        Don't override; implement game_tick_run() instead.
        """
        #
        # If a previous _run_with_tick_lock raised an exception, raise it now,
        # on the main thread so that the whole thing terminates.
        if self._tickRaise is not None:
            self._tickLock.acquire()
            try:
                exception = self._tickRaise
                self._tickRaise = None
                raise exception
            finally:
                self._tickLock.release()

        threading.Thread(
            target=self._run_with_tick_lock,
            args=(self.game_tick_run,),
            name="game_tick"
        ).start()

    def _run_with_tick_lock(self, run):
        if self._tickLock.acquire(False):
            try:
                self._skippedTicks = 0
                try:
                    self.mainLock.acquire()
                    if self.terminating():
                        log(INFO, "_run_with_tick_lock terminating.")
                        return
                    #
                    # Reference time for this tick.
                    self._tickPerf = (
                        time.perf_counter() - self._gameInitialisePerf)
                finally:
                    self.mainLock.release()
                run()
            except Exception as exception:
                # Catch the exception here and put it into a shared place.
                # (It's OK while this code has acquired tickLock.) This thread
                # can then be allowed to finish. The exception will be raised in
                # the next tick, see game_tick, above.
                self._tickRaise = exception
            except:
                self._tickRaise = Exception(
                    "Non-Exception raised in _run_with_tick_lock")
            finally:
                self._tickLock.release()
            return
            
        self._skippedTicks += 1
        self.tick_skipped()
        
    def game_tick_run(self):
        """
        Method that is run in a thread in every tick in which the tick lock
        can be acquired. Override it.
        If an exception is raised, it will be kept until the next tick, so that
        it can be raised on the main thread, which will cause BGE to terminate.
        """
        pass

    def tick_skipped(self):
        """
        Method that is run in a thread in every tick in which the tick lock
        can't be acquired. Override it to print an error messsage.
        """
        pass

    # Override.
    def game_terminate(self):
        self.game_terminate_lock()
        self.game_terminate_threads()
        log(DEBUG, "Terminating game.")
        super().game_terminate()

    def game_terminate_lock(self):
        log(DEBUG, "Acquiring terminate lock...")
        self._terminateLock.acquire()
        log(DEBUG, "Terminate lock acquired.")

    def game_terminate_threads(self):
        log(DEBUG, "Number of threads: {}.", threading.active_count())
        for thread in threading.enumerate():
            if thread is threading.current_thread():
                log(DEBUG, "Not joining current: {}.", thread)
            elif thread is threading.main_thread():
                log(DEBUG, "Not joining main: {}.", thread)
            else:
                log(DEBUG, "Joining: {} ...", thread)
                thread.join()
                log(DEBUG, "Joined.")
