#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Driver diagnostic.

This module contains a class that is used in some diagnostic and demonstration
versions of the proper blender_driver.controllers module."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Local imports.
#
# Proper controllers, used for its handy termination subroutine.
import blender_driver.controllers

class Base(object):
    """Class with some handy diagnostic print statements."""

    def _name(self, subroutine):
        return " ".join((self.__class__.__name__, subroutine))
    
    def __str__(self):
        return ''.join((
            "<", self.__class__.__name__, " ", str(self.__dict__), " >"))
    
    def __del__(self):
        """Destructor."""
        print(self._name("destructor"))

    def __init__(self):
        """Constructor."""
        print(self._name("constructor"))

class Driver(Base):
    def initialise(self, controller):
        # Assume there is only a single sensor.
        if not controller.sensors[0].positive:
            # Only take action on the positive transition.
            return
        self._counter += 1
        print(self._name('initialise'), self._counter)
    
    def tick(self, controller):
        # Assume there is only a single sensor.
        if not controller.sensors[0].positive:
            # Only take action on the positive transition.
            return
        self._counter += 1
        print(self._name('tick'), self._counter)
        if self._counter > self._maximum:
            print("".join((
                "Counter maximum exceeded. Counter:", str(self._counter),
                " Maximum:", str(self._maximum), ". Terminating.")))
            blender_driver.controllers.terminate_engine()
    
    def keyboard(self, controller):
        # Assume there is only a single sensor.
        if not controller.sensors[0].positive:
            # Only take action on the positive transition.
            return
        raise NotImplementedError()
        
    def __init__(self, counter, maximum):
        """Constructor."""
        super().__init__()
        self._counter = counter
        self._maximum = maximum

print("".join(('Diagnostic module "', __name__, '"')))
