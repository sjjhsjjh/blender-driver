#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Games Engine controller interface.
This module is a diagnostic and demonstration version of the proper
blender_driver.controllers module.

This code demonstrates:

-   Use of an explicit context object in a Blender Game Engine (BGE) controllers
    module.
-   Creation of a driver object when BGE starts.
-   Storing the driver object in the explicit context.

This is the current best approach for the driver object. It is used by the
proper blender_driver.controllers module.

This module can only be used from within the Blender Game Engine."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for perf_counter.
# https://docs.python.org/3/library/time.html
import time
#
# Local imports.
#
# Proper controllers, which have some utility subroutines.
import blender_driver.controllers
#
# Driver and Base class.
from . import driverutils
#
# Tick time dumper.
from .analysis import timing_analysis_dump

class Context(driverutils.Base):
    driver = None

class TimingDriver(driverutils.Driver):
    # Override, mostly a copy paste.
    def initialise(self, controller):
        # Assume there is only a single sensor.
        if not controller.sensors[0].positive:
            # Only take action on the positive transition.
            return
        self._counter += 1
        self._initialisePerf = time.perf_counter()
        self._tickTimes = []
        print('{} {:d} {:,.4f}'.format(
            self._name('initialise'), self._counter, self._initialisePerf))
    
    
    # Override, mostly a copy paste.
    def tick(self, controller):
        # Assume there is only a single sensor.
        if not controller.sensors[0].positive:
            # Only take action on the positive transition.
            return
        self._tickTimes.append(time.perf_counter() - self._initialisePerf)
        self._counter += 1
        print('{}{:3d} {:.4f}'.format(
            self._name('tick'), self._counter, self._tickTimes[-1]))
        if self._counter > self._maximum:
            self._terminate()
            
    def _terminate(self):
        print("".join((
            "Counter maximum exceeded. Counter:", str(self._counter),
            " Maximum:", str(self._maximum), ". Terminating.")))
        print(timing_analysis_dump(self._tickTimes))
        blender_driver.controllers.terminate_engine()

def initialise(controller):
    """Controller entry point for the first ever tick."""
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    if not controller.sensors[0].positive:
        return

    try:
        context.driver = TimingDriver(-1, 20)
        context.driver.initialise(controller)
        print("Expect a line every tick, for 21 ticks.")
    except:
        blender_driver.controllers.terminate_engine()
        raise

def tick(controller):
    try:
        context.driver.tick(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

def keyboard(controller):
    try:
        context.driver.keyboard(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

context = Context()

print("".join(('Controllers module "', __name__, '" ', str(context))))
