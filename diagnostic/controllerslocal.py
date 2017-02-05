#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Games Engine controller interface.
This module is a diagnostic and demonstration version of the proper
blender_driver.controllers module.

This code demonstrates:

-   Access to a local variable set when the controllers module is imported.

The value of the local variable isn't changed in this code, so it's not very
useful. Trying to change the value is demonstrated in the
controllersunboundlocal.py file in this directory.

This module can only be used from within the Blender Game Engine."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Local imports.
#
# Proper controllers, which have some utility subroutines.
import blender_driver.controllers

counter = -1

def initialise(controller):
    """Controller entry point for the first ever tick."""
    # Assume there is only a single sensor
    if not controller.sensors[0].positive:
        # Only take action on the positive transition.
        return
    try:
        # Next line prints the expected counter value, -1.
        print('initialise 0', counter)
        print('Terminate the game engine manually, with the Escape key.')
    except:
        blender_driver.controllers.terminate_engine()
        raise

def tick(controller):
    pass

def keyboard(controller):
    pass

#
# Next line prints the expected counter value, -1.
print("".join(('Controllers module "', __name__, '" ', str(counter))))
