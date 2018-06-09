#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver diagnostic application.
This application doesn't make anything happen in the 3D scene. It demonstrates
various things relating to use of Python in the Blender Game Engine (BGE).

-   When a controllers module gets loaded by BGE.
-   When the BGE Python instance can get execution cycles.
-   Use of threads and thread locks for synchronisation.
-   Keyboard events.

The command line options can switch off some things on which Blender Driver
relies, to demonstrate reliance.

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
from logging import DEBUG, INFO, WARNING, ERROR, log, getLogger
#
# This module prints diagnostic information about threads.
# https://docs.python.org/3.5/library/threading.html#thread-objects
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
#
# Tick time dumper.
from diagnostic.analysis import timing_summary, timing_analysis_dump

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.thread.Application):
        
    def diagnostic_remove_controllers(self, controllers):
        super().diagnostic_remove_controllers(controllers)
        if self.arguments.removeInitialiseController:
            controllers.initialise = None
        if self.arguments.removeTickController:
            controllers.tick = None

    # Override.
    def game_initialise(self):
        super().game_initialise()
        self._counter = 0
        self._tickTimes = []
        if not getLogger().isEnabledFor(DEBUG):
            log(WARNING, "Diagnostic application should be run verbose.")

        if self.arguments.mainLock:
            log(DEBUG, "acquiring main lock ...")
            self.mainLock.acquire()
            log(DEBUG, "acquired main lock.")
        log(DEBUG
            , "counter:{}.\nPython: {}\nArguments: {}\nGame scene objects: {}"
            , self._counter, self.pythonVersion, vars(self.arguments)
            , self.gameScene.objects)
        if self.arguments.removeTickController:
            print("Tick controller has been removed. Terminate BGE by"
                  " pressing Escape.")

        if self.arguments.mainLock:
            log(DEBUG, "releasing main lock.")
            self.mainLock.release()
        
        if self.arguments.thread:
            threading.Thread(
                target=self._dummy_action,
                args=(self.arguments.sleepInitialise, "initialise")
            ).start()
        else:
            self._dummy_action(self.arguments.sleepInitialise, "initialise")
        
        
    # Override.
    def game_tick(self):
        self._counter += 1
        log(DEBUG, {'counter': self._counter,
                    'Threads': threading.active_count(),
                    'sleepTick': self.arguments.sleepTick})

        if self.arguments.ticks > 0 and self._counter > self.arguments.ticks:
            log(INFO, "Terminating after ticks:{}. Maximum:{}. Threads:{}."
                , self._counter, self.arguments.ticks, threading.active_count())
            self.game_terminate()
            return
        
        if self.arguments.tickLock and self.arguments.thread:
            super().game_tick()
            # Above would set the _tickPerf. Other branches don't execute it so
            # set it "manually".
        elif self.arguments.thread:
            # Threads without locking.
            self._tickPerf = time.perf_counter() - self._gameInitialisePerf
            threading.Thread(target=self.game_tick_run).start()
        else:
            self._tickPerf = time.perf_counter() - self._gameInitialisePerf
            self.game_tick_run()
        # Case of tickLock but not threading is treated as not tickLock.

    # Override.
    def game_tick_run(self):
        self._tickTimes.append(self.tickPerf)
        self._dummy_action(
            self.arguments.sleepTick, " ".join(('tick', str(self._counter))))

    # Override.
    def tick_skipped(self):
        self._tickTimes.append(None)

    # Override.
    def game_terminate(self):
        if self.arguments.terminateLock and self.arguments.thread:
            super().game_terminate()
        else:
            if self.arguments.terminateLock:
                self.game_terminate_lock()
            if self.arguments.thread:
                self.game_terminate_threads()
            #
            # Go up two class inheritance levels and call the method there.
            super(blender_driver.application.thread.Application, self
                  ).game_terminate()
       
        log(INFO, 'Tick time analysis: interval:{:d} {}\n{}'
            , self.tickInterval, timing_summary(self._tickTimes)
            , timing_analysis_dump(self._tickTimes))
    
    def _dummy_action(self, duration, name=None):
        if self.arguments.mainLock:
            log(DEBUG, '{} acquiring main lock at start ...', name)
            self.mainLock.acquire()

        log(DEBUG, '{} start of dummy.', name)
            
        if duration is None:
            log(DEBUG, '{} no sleep.', name)
        else:
            if int(duration) == duration:
                duration = int(duration)
                # This is a kind of N and a half times loop. Before the loop
                # starts, the mainLock is already acquired. Inside the loop it
                # gets released and then acquired. If the loop is broken out of,
                # or just runs out, the lock is in the acquired state.
                for sleep in range(duration):
                    if self.terminating():
                        log(DEBUG, '{} stopping.', name)
                        break
                    if self.arguments.mainLock:
                        log(DEBUG, '{} releasing main lock in loop.', name)
                        self.mainLock.release()
                        log(DEBUG, '{} acquiring main lock in loop.', name)
                        self.mainLock.acquire()
                        
                    log(DEBUG, '{} about to sleep {} of {}.'
                        , name, sleep+1, duration)
                    time.sleep(1)
            else:
                if self.terminating():
                    log(DEBUG, '{} stopping instead of sleeping.', name)
                else:
                    time.sleep(duration)
                    log(DEBUG, '{} sleep {}.', name, duration)
                
        log(DEBUG, '{} end of dummy.', name)
        if self.arguments.mainLock:
            log(DEBUG, '{} releasing main lock at end.', name)
            self.mainLock.release()
    
    # Override.
    def terminating(self):
        if self.arguments.terminateLock:
            return super().terminating()
        return False
    
    def game_keyboard(self, keyEvents):
        #
        # Dump the keyboard event, for diagnostic purposes.
        keyString, ctrl, alt = self.key_events_to_string(keyEvents)
        log(DEBUG, '{} "{}" ctrl:{} alt:{}', keyEvents, keyString, ctrl, alt)

        if self.arguments.dumpOnKey:
            log(DEBUG, {
                'settings': self.settings,
                'arguments': self.arguments,
                'Threads': threading.active_count()})
        if keyString == "q" and self.arguments.quitOnQ:
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
            "Use the Terminate Lock to indicate termination, if using threads.")
        parser.add_argument(
            '--mainLock', action='store_true', help=
            "Use the Main Lock to control processing, if using threads.")
        parser.add_argument(
            '--tickLock', action='store_true', help=
            "Acquire and release a thread lock in every tick, if using"
            " threads. Acquisition is synchronous. If acquisition fails,"
            " processing is skipped for that tick.")
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
