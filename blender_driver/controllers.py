#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Games Engine controller interface.

This module can only be used from within the Blender Game Engine."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Python module for dynamic import, which is used to load the module that
# includes the driver application's Game subclass.
# https://docs.python.org/3.5/library/importlib.html
import importlib
#
# Python module for JavaScript Object Notation (JSON) strings.
import json
#
# Third party modules that are imported statically, in alphabetic order.
#
# Blender.
try:
    #
    # Blender Game Engine interface, which can only be imported if running from
    # within the Blender Game Engine.
    import bge
except ImportError as error:
    print( __doc__ )
    print( error )
#
# Local module for getting game property values.
from . import bpyutils

class Context(object):
    """Dummy class for an explicit context in which to store the driver
    object."""
    driver = None

context = Context()

def initialise(controller):
    """Controller entry point for the first ever tick."""
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    if not controller.sensors[0].positive:
        return
    #
    # If anything here raises an exception, attempt to terminate BGE.
    try:
        # The controller's owner will be the driver gateway game object.
        driver = initialise_application(controller.owner)
        #
        # This invocation is for completeness, just in case the application does
        # more initialisation after the constructor for some reason.
        driver.game_initialise()
        #
        # Store the new driver object in the explicit context.
        context.driver = driver
    except:
        terminate_engine()
        raise

def initialise_application(object_):
    """Create and initialise a driver instance from a game object."""
    #
    # The object will be the gateway game object. It will have a collection of
    # settings in one or more game properties. One of the settings is the path
    # of the driver application class that runs the whole shebang. The property
    # or properties will have been added by the owner.bpyutils.load_driver()
    # subroutine.
    #
    # Retrieve the settings.
    settingsJSON = bpyutils.get_game_property(object_, 'settingsJSON')
    #
    # Load the settings into a dictionary.
    settings = json.loads(settingsJSON)
    try:
        if settings['arguments']['verbose']:
            print("controllers.initialise_application loaded settings from game"
                  " property:", settings)
        #
        # Import the module.
        module = importlib.import_module(settings['module'])
        #
        # Pick the class object out of the module.
        driverClass = getattr(module, settings['class'])
    except KeyError:
        print("KeyError in controllers.initialise_application subroutine.")
        print("JSON", settingsJSON)
        print("dictionary", settings)
        raise
    #
    # Create and return the driver application instance. The constructor gets:
    #
    # -   The collection of settings read from the game properties.
    # -   The game scene, which it will need to set up its initial objects.
    # -   The driver gateway game object.
    driver = driverClass(settings)
    driver.game_constructor(bge.logic.getCurrentScene(), object_)
    return driver

def terminate_engine():
    """Terminate the Blender Game Engine."""
    bge.logic.getCurrentScene().end()
    bge.logic.endGame()

def tick(controller):
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    if controller.sensors[0].positive:
        try:
            context.driver.game_tick()
        except:
            terminate_engine()
            raise

def keyboard(controller):
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    sensor = controller.sensors[0]
    if sensor.positive:
        try:
            context.driver.game_keyboard(sensor.events)
        except:
            terminate_engine()
            raise

try:
    bpyutils.set_active_layer(0)
except:
    terminate_engine()
    raise