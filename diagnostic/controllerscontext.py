#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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

# Local imports.
#
# Proper controllers, which have some utility subroutines.
import blender_driver.controllers
#
# Driver and Base class.
from . import driverutils

class Context(driverutils.Base):
    driver = None

def initialise(controller):
    """Controller entry point for the first ever tick."""
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    if not controller.sensors[0].positive:
        return

    try:
        context.driver = driverutils.Driver(-1, 20)
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
