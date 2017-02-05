#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Games Engine controller interface.
This module is a diagnostic and demonstration version of the proper
blender_driver.controllers module.

This code demonstrates:

-   Creation of a driver object when BGE starts.
-   Storing the driver object in the game object that owns the controller.

This is an alternative to having an explicit context, as demonstrated in the
controllerscontext.py module.

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
    #
    # If anything here raises an exception, attempt to terminate BGE.
    try:
        # Instantiate and initialise an instance of a diagnostic class.
        driver = driverutils.Driver(-1, 20)
        driver.initialise(controller)
        print("Expect a line every tick, for 21 ticks.")
        #
        # Keep a reference to the driver in the gateway game object, which will
        # be the owner of the current controller. This reference is how the
        # other controller subroutines will access the driver.
        controller.owner['driver'] = driver
    except:
        blender_driver.controllers.terminate_engine()
        raise

def tick(controller):
    try:
        get_driver(controller).tick(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

def keyboard(controller):
    try:
        get_driver(controller).keyboard(controller)
    except:
        blender_driver.controllers.terminate_engine()
        raise

def get_driver(controller):
    if 'driver' in controller.owner.getPropertyNames():
        return controller.owner['driver']
    else:
        raise AttributeError("Driver not loaded.")

print("".join(('Controllers module "', __name__, '"')))
