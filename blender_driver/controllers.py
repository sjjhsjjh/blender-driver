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
# includes the driver application subclass.
# https://docs.python.org/3.5/library/importlib.html
import importlib
#
# Python module for JavaScript Object Notation (JSON) strings.
# https://docs.python.org/3.5/library/json.html
import json
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
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
    raise
#
# Local imports.
#
# Local module for getting game property values.
from . import bpyutils
#
# Local module for setting up Python logging.
from .loggingutils import initialise_logging

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
    # If anything here raises an exception, attempt to terminate BGE here.
    # There's no driver object yet.
    try:
        # The controller's owner will be the driver gateway game object.
        driver = initialise_application(controller.owner)
        #
        # Store the new driver object in the explicit context.
        context.driver = driver
    except:
        terminate_engine()
        raise
    #
    # If the next code raises an exception, terminate in the driver object
    # instead ...
    try:
        context.driver.game_initialise()
    except:
        try:
            context.driver.game_terminate()
        except Exception as exception:
            # ... unless the driver object hasn't been initialised correctly and
            # cannot terminate.
            terminate_engine()
            # Don't raise here; that would replace the original exception from
            # the initialise with the exception from the terminate.
            log(ERROR
                , "Failed to game_terminate after game_initialise failed. {}"
                , exception)
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
    # Retrieve the settings and load them into a dictionary.
    settingsJSON = bpyutils.get_game_property(object_, 'settingsJSON')
    settings = json.loads(settingsJSON)
    print(initialise_logging(settings['arguments']['verbose']))
    try:
        log(DEBUG, "loaded settings from game property {}", settings)
        #
        # Import the module.
        module = importlib.import_module(settings['module'])
        #
        # Pick the class object out of the module.
        driverClass = getattr(module, settings['class'])
    except KeyError:
        log(ERROR, "KeyError in controllers.initialise_application subroutine."
            "\nJSON: {}\n dictionary: {}", settingsJSON, settings)
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
            # terminate_engine()
            context.driver.game_terminate()
            raise

def keyboard(controller):
    # Assume there is only a single sensor and only take action on the positive
    # transition.
    sensor = controller.sensors[0]
    if sensor.positive:
        #
        # In general, the driver object will have been saved to the context by
        # the initialise controller. That won't have happened if the initialise
        # controller has been removed and we're in some kind of diagnostic run.
        # Check that here and invoke initialise now in that case.
        if context.driver is None:
            initialise(controller)
            log(WARNING, "Keyboard controller executed late initialise.")
        try:
            context.driver.game_keyboard(sensor.events)
        except:
            context.driver.game_terminate()
            # terminate_engine()
            raise

try:
    bpyutils.set_active_layer(0)
except:
    terminate_engine()
    raise

print("".join(('Controllers module "', __name__, '" ', str(context))))
