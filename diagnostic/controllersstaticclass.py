#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Games Engine controller interface.
This module is a diagnostic and demonstration version of the proper
blender_driver.controllers module.

This code demonstrates:

-   Creation of a driver object when the controllers module is imported.
-   Storing the driver object implicitly in the module's execution context.

This approach works but doesn't allow the class of the driver object to be
determined at run time. Approaches that do allow run-time specification of the
driver class are demonstrated in the controllersgameobject.py and
controllerscontext.py files in this directory.

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
# Driver class.
from . import driverutils

def initialise(controller):
    """Controller entry point for the first ever tick."""
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    if not controller.sensors[0].positive:
        return

    try:
        driver.initialise(controller)
        print("Expect a line every tick, for 21 ticks.")
    except:
        blender_driver.controllers.terminate_engine()
        raise

def tick(controller):
    try:
        driver.tick(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

def keyboard(controller):
    try:
        driver.keyboard(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

driver = driverutils.Driver(-1, 20)

print("".join(('Controllers module "', __name__, '" ', str(driver))))
